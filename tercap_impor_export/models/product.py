# -*- coding: utf-8 -*-
##############################################################################
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

import openerp
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class product_template(osv.osv):
    _inherit = 'product.template'
    #creamos un campo para registrar el precio minimo de venta en productos
    _columns = {
        'min_price' :fields.float('Precio Minimo', digits_compute=dp.get_precision('Product Price'), help="Precio minimo de venta para el producto"),
        'max_price' :fields.float('Precio Maximo', digits_compute=dp.get_precision('Product Price'), help="Precio maximo de venta para el producto"),
    }
    _defaults = {
        'min_price' : 0.0,
    }


   