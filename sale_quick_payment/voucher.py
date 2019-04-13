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
from openerp.tools.translate import _

def crea_voucher(self, cr, uid, invoice_id, pay_id, context=None):
    invoice_obj = self.pool.get('account.invoice')
    invoice = invoice_obj.browse(cr,uid,invoice_id)
    voucher_obj = self.pool.get('account.voucher')
        
    #generamos un recibo voucher con valores
    valvoucher ={}
    valvoucher['partner_id'] = invoice.partner_id.id
    valvoucher['type'] = invoice.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
    valvoucher['journal_id'] = pay_id.journal_id.id
    valvoucher['account_id'] = pay_id.account_id.id
    valvoucher['date'] = pay_id.date
    valvoucher['amount'] = pay_id.credit
    valvoucher['company_id'] = invoice.company_id.id
    valvoucher['reference'] = 'Pago de factura '+ str(invoice.number)
    #_logger.error('##### AIKO ###### Import_control en cobro factura datos para nuevo voucher %s'%valvoucher)
    new_voucher_id = voucher_obj.create(cr,SUPERUSER_ID,valvoucher,context=None)

    return new_voucher_id


def crea_lineas_voucher(self, cr, uid, invoice_id, pay_id, new_voucher_id, context=None):
    invoice_obj = self.pool.get('account.invoice')
    invoice = invoice_obj.browse(cr,uid,invoice_id)
    voucher_line_obj = self.pool.get('account.voucher.line')
        
    #registramos las lineas de ese recibo
    for line in invoice.move_id.line_id:
        if line.debit > 0.0:
            valfiles={}
            valfiles['name'] = 'Pago de factura '+ str(invoice.number)
            valfiles['voucher_id'] = new_voucher_id
            valfiles['move_line_id'] = line.id
            valfiles['amount_original'] = abs(line.debit)
            valfiles['amount_unreconciled'] = abs(line.debit)
            valfiles['amount'] = pay_id.credit
            valfiles['account_id'] =invoice.partner_id.property_account_receivable.id
            valfiles['type'] = 'cr'
            valfiles['partner_id'] = invoice.partner_id.id
            #_logger.error('##### AIKO ###### Import_control en cobro factura datos para nueva linea voucher %s'%valfiles)
            voucher_line_obj.create(cr,SUPERUSER_ID,valfiles,context=None)
            #_logger.error('##### AIKO ###### Import_control creada linea de voucher %s'%vou_line_id)
