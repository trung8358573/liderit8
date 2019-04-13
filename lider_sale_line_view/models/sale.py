# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'

    def _get_over_minprice(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        for line in self.browse(cr, uid, ids, context=context):
        	if line.product_id.product_tmpl_id.min_price:
        		res[line.id] = line.price_reduce - line.product_id.product_tmpl_id.min_price
        return res

    def _search_over_minprice(self, cr, uid, obj, name, args, context=None):
    	res = []
    	ids = obj.search(cr,uid,[]) # ids
    	for line in self.browse(cr, uid, ids):
    		if line.product_id.product_tmpl_id.min_price:
    			if (line.price_reduce - line.product_id.product_tmpl_id.min_price) < 0:
    				res.append(line.id)
    	return [('id','in',res)]

    def _get_line_netprice(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.price_subtotal / line.product_uom_qty
        return res


    def _search_line_netnull(self, cr, uid, obj, name, args, context=None):
    	res = []
    	ids = obj.search(cr,uid,[]) # ids
    	for line in self.browse(cr, uid, ids):
    		if (line.price_subtotal / line.product_uom_qty) == 0:
    			res.append(line.id)
    	return [('id','in',res)]



    _columns={
    	'over_minprice': fields.function(_get_over_minprice, type='float', string='Sobre Minimo', fnct_search=_search_over_minprice, digits_compute=dp.get_precision('Product Price')),
    	'line_netnull': fields.function(_get_line_netprice, type='float', string='Neto Nulo', fnct_search=_search_line_netnull, digits_compute=dp.get_precision('Product Price')),
    }

   
