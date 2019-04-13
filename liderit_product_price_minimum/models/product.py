# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class product_template(osv.Model):

    _inherit = 'product.template'

    _columns = {

        'min_totalprice':fields.float('Tramo mínimo', digits_compute= dp.get_precision('Product Unit of Measure')),
        }

    _defaults = {
        'min_totalprice': '0',
    }

product_template()


