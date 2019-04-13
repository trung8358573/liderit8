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

import logging 
_logger = logging.getLogger(__name__)

def crea_voucher(self, cr, uid, invoice_id, cobro, context=None):
    invoice_obj = self.pool.get('account.invoice')
    invoice = invoice_obj.browse(cr,uid,invoice_id)
    voucher_obj = self.pool.get('account.voucher')
    journal_obj = self.pool.get('account.journal')
        
    #generamos un recibo voucher con valores
    valvoucher ={}
    valvoucher['partner_id'] = invoice.partner_id.id
    valvoucher['type'] = invoice.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
    search_journal =[('cobros_tercap','=',True)]
    jour_id = journal_obj.search(cr,uid,search_journal)
    if len(jour_id) > 0:
        valvoucher['journal_id'] = journal_obj.browse(cr,uid,jour_id[0]).id
        valvoucher['account_id'] = journal_obj.browse(cr,uid,jour_id[0]).default_debit_account_id.id
    else:
        search_journal =[('type','=','cash')]
        jour_id = journal_obj.search(cr,uid,search_journal)
        valvoucher['journal_id'] = journal_obj.browse(cr,uid,jour_id[0]).id
        valvoucher['account_id'] = journal_obj.browse(cr,uid,jour_id[0]).default_debit_account_id.id

    valvoucher['date'] = fields.datetime.now()
    valvoucher['amount'] = cobro
    valvoucher['company_id'] = invoice.company_id.id
    valvoucher['reference'] = 'Pago de factura '+ str(invoice.number)
    #_logger.error('##### AIKO ###### Import_control en cobro factura datos para nuevo voucher %s'%valvoucher)
    new_voucher_id = voucher_obj.create(cr,SUPERUSER_ID,valvoucher,context=None)

    return new_voucher_id


def crea_lineas_voucher(self, cr, uid, invoice_id, cobro, new_voucher_id, context=None):
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
            valfiles['amount'] = cobro
            valfiles['account_id'] =invoice.partner_id.property_account_receivable.id
            valfiles['type'] = 'cr'
            valfiles['partner_id'] = invoice.partner_id.id
            #_logger.error('##### AIKO ###### Import_control en cobro factura datos para nueva linea voucher %s'%valfiles)
            voucher_line_obj.create(cr,SUPERUSER_ID,valfiles,context=None)
            #_logger.error('##### AIKO ###### Import_control creada linea de voucher %s'%vou_line_id)

def crea_voucher_withpay(self, cr, uid, invoice_id, pay_id, context=None):
    invoice_obj = self.pool.get('account.invoice')
    invoice = invoice_obj.browse(cr,uid,invoice_id)
    voucher_obj = self.pool.get('account.voucher')
    
    #generamos un recibo voucher con valores
    valvoucher ={}
    valvoucher['partner_id'] = invoice.partner_id.id
    #valvoucher['type'] = 'receipt'
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

       
def crea_lineas_voucher_withpay(self, cr, uid, invoice_id, pay_id, new_voucher_id, context=None):
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
            vou_line_id = voucher_line_obj.create(cr,SUPERUSER_ID,valfiles,context=None)
            #_logger.error('##### AIKO ###### Import_control creada linea de voucher %s'%vou_line_id)
