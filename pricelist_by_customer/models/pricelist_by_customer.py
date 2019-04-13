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
class pricelist_by_cusotmer(osv.osv):
    _name = "pricelist.by.customer"
    #auto False para que no genere una tabla, porque es una vista
    _auto = False
    _columns = {
        'precio_lista': fields.float('Precio de Tarifa', readonly=True),
        'descuento': fields.float('Descuento %', readonly=True),
        'precio_neto': fields.float('Precio Neto', readonly=True),
        'precio_especial': fields.float('Precio Especial', readonly=True),
        'codigo': fields.char('Codigo', readonly=True),
        'producto': fields.char('Producto', readonly=True),
        'tarifa': fields.char('Nombre de la tarifa', readonly=True),
        'date_start': fields.date('Activo desde', readonly=True),
        'date_end': fields.date('Activo hasta', readonly=True),
    }
    _order = 'tarifa, codigo'


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'pricelist_by_customer')
        cr.execute("""
            CREATE OR REPLACE VIEW pricelist_by_customer AS (
            SELECT
                item.id as id,
                templ.list_price as precio_lista,
                (item.price_discount *-100) as descuento,
                (templ.list_price+(templ.list_price*item.price_discount)) as precio_neto,
                item.price_surcharge as precio_especial,
                product.default_code as codigo, 
                product.name_template as producto, 
                version.name as tarifa,
                version.date_start,
                version.date_end
            from product_pricelist_item item
            join product_pricelist_version version on
                item.price_version_id = version.id
            join product_pricelist list on
                list.id = version.pricelist_id
            join product_product product on
                item.product_id = product.id
            join product_template templ on
                product.product_tmpl_id = templ.id
            where list.type like 'sale' 
            and list.active 
            and item.base = 1
            and item.base_pricelist_id is null
            )
        """)
