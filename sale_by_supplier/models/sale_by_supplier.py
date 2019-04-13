# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Hugo Santos (<http://factorlibre.com>).
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
from openerp.osv import osv, fields
from openerp import tools
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

#creamos una clase para tener en una vista la relacion entre pedidos de venta y proveedor del producto
class sale_by_supplier(osv.osv):
    _name = "sale.by.supplier"
    #auto False para que no genere una tabla, porque es una vista
    _auto = False
    _columns = {
        'date': fields.date('Fecha', readonly=True),
        'name_template': fields.char('Producto', readonly=True),
        'supplier': fields.char('Proveedor', readonly=True),
        'cantidad': fields.float('Cantidad', readonly=True),
        'price_unit': fields.float('Precio', readonly=True),
        'discount': fields.float('Descuento', readonly=True),
        'margin': fields.float('Margen', readonly=True),
    }
    _order = 'date'

 
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'sale_by_supplier')
        cr.execute("""
            CREATE OR REPLACE VIEW sale_by_supplier AS (
            SELECT
                lines.id as id, 
                date(to_char(sales.date_order,'YYYY/MM/dd')) as date, 
                product.name_template, 
                partner.name as supplier,
				lines.product_uom_qty as cantidad, 
				lines.price_unit, 
				lines.discount, 
				lines.margin
			from sale_order sales
			join sale_order_line lines on
				lines.order_id = sales.id
			join product_product product on
				lines.product_id = product.id
			join (
				select distinct name, product_tmpl_id
				from product_supplierinfo
				group by name, product_tmpl_id
			) supplier on
				product.product_tmpl_id = supplier.product_tmpl_id
			join res_partner partner on
				supplier.name = partner.id
            )
        """)
