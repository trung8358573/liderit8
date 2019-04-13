# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit= 'sale.order'

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):

        invoice_obj = self.pool.get('account.invoice')

        resultado = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped=grouped, states=states, date_invoice = date_invoice, context=context)

        if resultado:
            inv_obj_brw = invoice_obj.browse(cr,uid,resultado)
            #vamos a tomar los 150 primeros caracteres solamente para que no desborde la pantalla
            ori_limit = str(inv_obj_brw.origin)[:150]
            name_limit = str(inv_obj_brw.name)[:150]
            ref_limit = str(inv_obj_brw.reference)[:150]
            invoice_obj.write (cr, uid, resultado, {'origin': ori_limit,'name': name_limit, 'reference':ref_limit})

        return resultado