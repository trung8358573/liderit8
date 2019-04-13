# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp

import logging 
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    devolucion_cobro = fields.Boolean('Es una devolución de cobro')

    _defaults = {
        'devolucion_cobro': False
    }

class PaymentReturn(models.Model):
    _inherit = 'payment.return'

    def _get_date_maturity(self, return_line):
        return return_line.date_maturity

    
    @api.multi
    def action_confirm(self):
        self.ensure_one()
        # Check for incomplete lines
        if self.line_ids.filtered(lambda x: not x.move_line_ids):
            raise UserError(
                _("You must input all moves references in the payment "
                  "return."))
        invoices_returned = self.env['account.invoice']

        move = {
            'name': '/',
            'ref': _('Return %s') % self.name,
            'journal_id': self.journal_id.id,
            'date': self.date,
            'company_id': self.company_id.id,
            'period_id': (self.period_id.id or self.period_id.with_context(
                company_id=self.company_id.id).find(self.date).id),
        }
        move_id = self.env['account.move'].create(move)
        for return_line in self.line_ids:

            lines2reconcile = return_line.move_line_ids.mapped(
                'reconcile_id.line_id')
            invoices_returned |= self._get_invoices(lines2reconcile)
            #para recoger la factura de esta linea de devolucion
            this_invoice_returned = self._get_invoices(lines2reconcile)
            # para recoger dato de vencimiento del movimiento, no la factura
            _logger.error('##### AIKO ###### Payment return liderit busco maturity para move_id %s' % lines2reconcile[0].move_id.id)
            
            my_maturity = self.env['account.move.line'].search([('move_id','=',lines2reconcile[0].move_id.id),('date_maturity','!=',False)])
            if len (my_maturity)>0:
                _logger.error('##### AIKO ###### Payment return liderit registro maturity con valor %s' % my_maturity[0].date_maturity)
                my_maturity_date = my_maturity[0].date_maturity
            for move_line in return_line.move_line_ids:
                _logger.error('##### AIKO ###### Payment return liderit valor de move_line %s' % move_line.id)
                move_amount = self._get_move_amount(return_line, move_line)

                if len(this_invoice_returned) > 0 and len (my_maturity) > 0:
                    _logger.error('##### AIKO ###### Payment return liderit factura para apunte %s,con id %s' % (move_id.id, this_invoice_returned[0].id))
                    move_line2 = move_line.copy(
                        default={
                            'move_id': move_id.id,
                            'debit': move_amount,
                            'name': move['ref'],
                            'credit': 0,
                            'devolucion_cobro': True,
                            'date_maturity': my_maturity_date,
                            # paramos esto porque solo se puede asociar un asiento con una factura y por tanto
                            # no se puede asociar un efecto recirculado con una factura.
                            # 'invoice': this_invoice_returned[0].id,
                            'payment_mode_id': this_invoice_returned[0].payment_mode_id.id,
                        })
                else:
                    _logger.error('##### AIKO ###### Payment return liderit no encuentra factura para apunte %s' % move_id.id)
                    move_line2 = move_line.copy(
                        default={
                            'move_id': move_id.id,
                            'debit': move_amount,
                            'name': move['ref'],
                            'credit': 0,
                            'devolucion_cobro': True,
                        })
                lines2reconcile |= move_line2
                move_line2.copy(
                    default={
                        'debit': 0,
                        'credit': move_amount,
                        'account_id':
                            self.journal_id.default_credit_account_id.id,
                        'devolucion_cobro': True,
                    })
                # Criterio de Lider: no hacer conciliacion, solo copiar move line para nuevo efecto identificado como devolucion
                # Break old reconcile  (esto no lo hacemos)
                # move_line.reconcile_id.unlink()
            # Make a new one with at least three moves (esto tampoco)
            # lines2reconcile.reconcile_partial()
            # return_line.write(
            #     {'reconcile_id': move_line2.reconcile_partial_id.id})
        # Mark invoice as payment refused
        invoices_returned.write(self._prepare_invoice_returned_vals())
        move_id.button_validate()
        self.write({'state': 'done', 'move_id': move_id.id})
        return True

    