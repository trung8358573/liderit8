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

class product_pricelist_item(models.Model):
    _inherit = 'product.pricelist.item' 

    def _check_product(self, cr, uid, ids, context=None):
    	for record in self.browse(cr, uid, ids, context=context):
    		#un contador de productos por version de tarifa
	        cr.execute(
	        	"""select product_id, price_version_id, min_quantity, cast(count(1) as int)
						from product_pricelist_item
						where product_id is not null
						group by product_id, price_version_id, min_quantity
				"""
			)
	        #con x[3] recuperamos el contador de valores repetidos agrupados por producto, version y cantidad
	        item_ids = [x[3] for x in cr.fetchall()]
	        _logger.error('# Check product: %s' % item_ids)
	        for it in item_ids:
	        	_logger.error('# Check product: it con valor %s' % it)
		        if it>1:
		            return False
    	return True

    _constraints = [
        (_check_product, 'Error ! You cannot duplicate product in same version', ['product_id']),
    ]