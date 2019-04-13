# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class sale_order_line(osv.osv):
	_inherit = 'sale.order.line'

	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
		uom=False, qty_uos=0, uos=False, name='', partner_id=False,
		lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):

		res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
			uom, qty_uos, uos, name, partner_id,
			lang, update_tax, date_order, packaging, fiscal_position, flag, context)

		product_obj = self.pool.get('product.product')
		partner_obj = self.pool.get('res.partner')
		prod_cust_code = self.pool.get ('product.customer.code')
		partner = partner_obj.browse(cr, uid, partner_id)
		context_partner = {'lang': partner.lang, 'partner_id': partner_id}
		product_obj = product_obj.browse(cr, uid, product, context=context_partner)
		search_condition =[('product_id','=',product),('partner_id','=',partner_id)]

		if not flag:
			prod_cust_search = prod_cust_code.search(cr,uid,search_condition)
			if len(prod_cust_search)>0:
				prod_cust_id = prod_cust_code.browse(cr,uid,prod_cust_search[0])
				res['value']['name'] = prod_cust_id.product_code +' '+ product_obj.name

		return res