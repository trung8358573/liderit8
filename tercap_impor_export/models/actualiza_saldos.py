# -*- encoding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2013 Ld solutions
#    (<http://www.ldsolutions.es>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
# import time
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields, orm
from openerp import api
from openerp.tools.translate import _

import logging 
_logger = logging.getLogger(__name__)



def _actualiza_saldo_factura (self, cr, uid, ids, sale_pays, context=None):

    invoice = self.pool.get('account.invoice').browse(cr, uid, ids[0], context=context)
    move = invoice.move_id

    for p in sale_pays:
        _logger.error('##### AIKO ###### Actualiza_saldo_factura payment_id : %s' %p)                
        for c in p:
            _logger.error('##### AIKO ###### Actualiza_saldo_factura payment_id.id : %s' %c.id)
            account = c.account_id.id


            # First part, create voucher
            #account = transaction.journal_id.default_credit_account_id or transaction.journal_id.default_debit_account_id
            period_id = self.pool.get('account.voucher')._get_period(cr, uid)
            #partner_id = self.pool.get('res.partner')._find_accounting_partner(invoice.partner_id).id,

            voucher_data = {
                'partner_id': invoice.partner_id.id,
                'amount': c.debit,
                'journal_id': c.journal_id.id,
                'period_id': period_id,
                'account_id': account,
                'type': invoice.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'reference' : 'Pago de factura '+invoice.number,
            }

            _logger.debug('voucher_data')
            _logger.debug(voucher_data)


            voucher_id = self.pool.get('account.voucher').create(cr, uid, voucher_data, context=context)

            _logger.debug('test')
            _logger.debug(voucher_id)

            # Equivalent to workflow proform
            self.pool.get('account.voucher').write(cr, uid, [voucher_id], {'state':'draft'}, context=context)

            # Need to create basic account.voucher.line according to the type of invoice need to check stuff ...
            double_check = 0
            for move_line in invoice.move_id.line_id:
                # According to invoice type
                if invoice.type in ('out_invoice','out_refund'):
                    if move_line.debit > 0.0:
                        line_data = {
                            'name': 'Pago de factura '+invoice.number,
                            'voucher_id' : voucher_id,
                            'move_line_id' : move_line.id,
                            'account_id' : invoice.partner_id.property_account_receivable.id,
                            'partner_id' : invoice.partner_id.id,
                            'amount_unreconciled': abs(move_line.debit),
                            'amount_original': abs(move_line.debit),
                            'amount': abs(move_line.debit),
                            'type': 'cr',
                        }

                        _logger.debug('line_data')
                        _logger.debug(line_data)

                        line_id = self.pool.get('account.voucher.line').create(cr, uid, line_data, context=context)
                        double_check += 1
                else:
                    if move_line.credit > 0.0:
                        line_data = {
                            'name': 'Pago de factura '+invoice.number,
                            'voucher_id' : voucher_id,
                            'move_line_id' : move_line.id,
                            'account_id' : invoice.account_id.id,
                            'partner_id' : invoice.partner_id.id,
                            'amount_unreconciled': abs(move_line.credit),
                            'amount_original': abs(move_line.credit),
                            'amount': abs(move_line.credit),
                            'type': 'dr',
                        }

                        _logger.debug('line_data')
                        _logger.debug(line_data)

                        line_id = self.pool.get('account.voucher.line').create(cr, uid, line_data, context=context)
                        double_check += 1

                # Cautious check to see if we did ok
                if double_check == 0:
                    _logger.warning(invoice)
                    _logger.warning(voucher_id)
                    raise osv.except_osv(_("Warning"), _("I did not create any voucher line"))
                elif double_check > 1:
                    _logger.warning(invoice)
                    _logger.warning(voucher_id)
                    raise osv.except_osv(_("Warning"), _("I created multiple voucher line ??"))

                _logger.error('##### AIKO ###### Actualiza_saldo_factura validando voucher : %s' %voucher_id)
                # Where the magic happen
                self.pool.get('account.voucher').button_proforma_voucher(cr, uid, [voucher_id], context=context)