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

from openerp import models
import logging 
_logger = logging.getLogger(__name__)

class product_standard_price(models.Model):
    _inherit = 'purchase.order' 


    def _create_stock_moves(self, cr, uid, order, order_lines, picking_id=False, context=None):

        stock_move = self.pool.get('stock.move')
        todo_moves = []
        new_group = self.pool.get("procurement.group").create(cr, uid, {'name': order.name, 'partner_id': order.partner_id.id}, context=context)

        
        for order_line in order_lines:
            if order_line.state == 'cancel':
                continue
            if not order_line.product_id:
                continue

            if order_line.product_id.type in ('product', 'consu'):
                for vals in self._prepare_order_line_move(cr, uid, order, order_line, picking_id, new_group, context=context):
                    move = stock_move.create(cr, uid, vals, context=context)
                   
                    price_unit_disc = (order_line.price_unit*order_line.product_id.uom_po_id.factor)*(1-order_line.discount/100)
                    #_logger.error('###########################################################################')
                    #_logger.error('# Producto: %s' % order_line.name)
                    #_logger.error('# Descuento (order_line.discount): %d' % order_line.discount)                   
                    #_logger.error('# Precio unidad (order_line.price_unit): %d' % order_line.price_unit)
                    #_logger.error('# Cantidad (order_line.product_qty.): %d' % order_line.product_qty)  
                    #_logger.error('# Precio unidad con descuento (price_unit_disc): %f' % price_unit_disc)
                    #_logger.error('###########################################################################')
                    stock_move.write (cr,uid,move,{'price_unit':price_unit_disc},context=None)
                    
                    todo_moves.append(move)

        todo_moves = stock_move.action_confirm(cr, uid, todo_moves)
        stock_move.force_assign(cr, uid, todo_moves) 
