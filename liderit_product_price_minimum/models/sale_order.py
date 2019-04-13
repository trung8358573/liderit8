# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if product:
            product_obj = self.pool.get('product.product').browse(cr, uid, product)
            line_min = product_obj.min_totalprice or 0
            if qty < line_min:
                res['value'].update({
                    'product_uom_qty': line_min,
                })
        return res

    ##this is what works :)

    @api.one
    @api.constrains('product_uom_qty')
    def _check_minimum(self):
        if self.product_id.product_tmpl_id.min_totalprice != 0:
            if self.product_uom_qty < self.product_id.product_tmpl_id.min_totalprice:
                raise ValidationError("No puede ofertar una cantidad inferior al limite minimo. Revise el producto %s"%self.product_id.name)
#
#        if (self.product_id.min_totalprice) > 0:
#            if (self.product_uom_qty)<(self.product_id.min_totalprice):
#                raise ValidationError("No se puede utilizar una cantidad menor que el tramo mínimo definido para el producto")
