# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""Inherit stock_picking to add early payment discount"""

# from openerp import models, fields, api, exceptions, _
from openerp.osv import osv, fields

import logging 
_logger = logging.getLogger(__name__)

class stock_picking(osv.osv):
    """Inherit purchase_order to add early payment discount"""

    _inherit = "stock.picking"

    def _create_invoice_from_picking(self, cr, uid, picking, vals, context=None):
        invoice_id = super(stock_picking, self)._create_invoice_from_picking(cr, uid, picking, vals, context=context)
        invoices = self.pool.get('account.invoice')
        purchases = self.pool.get('purchase.order')
        # para localizar el pedido de compra el campo origin del picking sera el name del pedido de compra
        purchase_orders = purchases.search(cr,uid,[('name','=',picking.origin)])
        _logger.error('########### Entra en purchase early discount stock picking create invoice from picking')
        if len (purchase_orders) > 0:
          for order in purchase_orders:
            _logger.error('########### En purchase early discount stock picking create invoice order es: %s' % order)
            pur_order = purchases.browse(cr,uid,order)
            if pur_order.early_payment_discount:
              _logger.error('########### En purchase early discount stock picking create invoice vale: %s' % pur_order.early_payment_discount)
              invoices.write (cr, uid, invoice_id, {'early_payment_discount': pur_order.early_payment_discount})

        
        return invoice_id

