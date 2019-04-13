# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, api
from openerp.osv import fields, osv, expression

import logging 
_logger = logging.getLogger(__name__)



class account_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
        'alter_stock': fields.boolean('Afecta al stock')
    }

    _defaults = {
        'alter_stock': False,
    }

    
    def invoice_validate(self, cr, uid, ids, context=None):
        invoice = self.pool.get('account.invoice')
        invoice_id = invoice.browse(cr, uid, ids[0], context=context)
        # tiene que estar marcada la factura y no proceder de un pedido ni de un albaran
        if invoice_id.alter_stock and len(invoice_id.sale_ids)==0 and len(invoice_id.picking_ids)==0:
            lines = invoice_id.invoice_line
            stock_move = self.pool.get('stock.move')
            wharehouse = self.pool.get('stock.location')
            picking_type = self.pool.get('stock.picking.type')

            search_cond1 = [('usage','=','customer')]
            search_cond2 = [('name','ilike','stock')]
            wharehouse_cust = wharehouse.search(cr, uid, search_cond1)
            wharehouse_exist = wharehouse.search(cr, uid, search_cond2)
            
            for l in lines:
                values = {}
                if l.product_id:
                    values ['product_id'] = l.product_id.id
                    values ['product_uom_qty'] = l.quantity
                    values ['product_uos_qty'] = l.quantity
                    values ['product_uom'] = l.uos_id.id
                    values ['product_uos'] = l.uos_id.id
                    if wharehouse_cust and wharehouse_exist:
                        if l.quantity > 0:
                            if wharehouse_exist:
                                search_cond_pick = [('code','like','outgoing'),('default_location_src_id','=',wharehouse_exist)]
                                picking_type_id = picking_type.search(cr, uid, search_cond_pick)
                            values ['location_id'] = wharehouse_exist[0]
                            values ['location_dest_id'] = wharehouse_cust[0]
                            if picking_type_id:
                                values ['picking_type_id'] = picking_type_id[0]
                            else:
                                search_cond_pick = [('code','like','outgoing')]
                                picking_type_id = picking_type.search(cr, uid, search_cond_pick)
                                values ['picking_type_id'] = picking_type_id[0]
                        else:
                            if l.quantity < 0:
                                if wharehouse_cust:
                                    search_cond_pick = [('code','like','incoming'),('default_location_dest_id','=',wharehouse_cust)]
                                    picking_type_id = picking_type.search(cr, uid, search_cond_pick)
                                values ['location_id'] = wharehouse_cust[0]
                                values ['location_dest_id'] = wharehouse_exist[0]
                                if picking_type_id:
                                    values ['picking_type_id'] = picking_type_id[0]
                                else:
                                    search_cond_pick = [('code','like','incoming')]
                                    picking_type_id = picking_type.search(cr, uid, search_cond_pick)
                                    values ['picking_type_id'] = picking_type_id[0]
                            else:
                                continue
                    else:
                        continue
                    values ['name'] = l.name
                    values ['origin'] = 'Factura ' + invoice_id.number
                    values ['partner_id'] =  invoice_id.partner_id.id
                    # creamos el movimiento de stock
                    stock_move_id = stock_move.create (cr, uid, values, context=context)
                    # procesamos el movimiento creado
                    todo = []
                    todo.append(stock_move_id)
                    _logger.error('##### AIKO ###### El valor del stock move a procesar es:%s'%todo)
                    stock_move.action_done(cr, uid, todo, context=context)

        return invoice.write(cr,uid,ids[0],{'state': 'open'}, context=context)