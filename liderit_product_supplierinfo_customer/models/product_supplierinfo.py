# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0,
            uos=False, name='', partner_id=False, lang=False,
            update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False
    ):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist=pricelist, product=product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name,
            partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        #llegar al product.supplierinfo relacionado
        #en el modelo product.supplierinfo hay name = id_cliente (partner_id), product_id, type='customer'

        if product:
            product_obj = self.env['product.product']
            product_customer = self.env['product.supplierinfo']
            #if self.user_has_groups(
            #        'sale_order_line_description.'
            #        'group_use_product_description_per_so_line'):
            if self.user_has_groups('base.group_sale_salesman'):
                lang = self.env['res.partner'].browse(partner_id).lang

                #ponemos por delante el criterio que si existe nombre en product.supplierinfo usaremos esa
                product_cust = product_customer.search([('name', '=', partner_id), ('product_id', '=', product), ('type', '=', 'customer')])
                
                product = product_obj.with_context(lang=lang).browse(product)
                
                if product_cust:
                    if 'value' not in res:
                        res['value'] = {}
                    if product_cust.product_code:
                        res['value']['name'] = '['+product_cust.product_code+'] '+product_cust.product_name
                    else:
                        res['value']['name'] = product_cust.product_name
                else:
                    if product.description_sale:
                        if 'value' not in res:
                            res['value'] = {}
                        res['value']['name'] = product.description_sale

        return res
