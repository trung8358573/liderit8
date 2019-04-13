# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class product_product(osv.osv):
    _inherit = "product.template"

    _columns = {
        'min_price': fields.float('Min Price', digits_compute= dp.get_precision('Product Price')),
    }


class sale_order_line(models.Model):
    _inherit = "sale.order.line"


    @api.multi
    def check_minprice_ok(self):
        self.ensure_one()
        min_price = self.product_id.product_tmpl_id.min_price
        qty = self.product_uom_qty
        total = self.price_subtotal
        real_price = total / qty

        if real_price < min_price:
            return False
        else:
            return True
