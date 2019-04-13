# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import models, api, fields
import pytz
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    notes = fields.Text('Notes')
    barcode = fields.Char("Barcode")

    @api.model
    def load_currency(self, company_id):
        if company_id:
            company_obj = self.env['res.company'].browse(company_id)
            if company_obj and company_obj.currency_id:
                return company_obj.currency_id.read()

    @api.model
    def create_update_so(self, vals):
        order_lines = []
        for each in vals.get('lines'):
            order_lines.append((0, 0, {
                'product_id': each.get('product').get('id'),
                'product_uom_qty': each.get('quantity'),
                'price_unit': each.get('price_unit'),
                'name': each.get('description') or each.get('product').get('display_name')
            }))
        values = {
            'partner_id': vals.get('partner_id'),
            'notes': vals.get('notes'),
            'payment_term': vals.get('payment_term'),
            'order_line': order_lines,
            # 'date_order':vals.get('datetime') or datetime.now(),
        }
        if not vals.get('sale_order_id'):
            order_id = self.create(values)
        else:
            order_id = self.browse(vals.get('sale_order_id'))
            order_id.order_line.unlink()

            order_id.update(values)
        return order_id.id

    @api.model
    def load_sale_order_by_id(self, sale_order_id):
        sale_order = self.browse(sale_order_id)
        sale_order_lines = []
        if sale_order:
            if sale_order.order_line:
                for line in sale_order.order_line:
                    product_obj = line.product_id
                    line = {
                        'line_id':line.id,
                        'product_id':line.read(['product_id'])[0],
                        'display_price':product_obj.list_price,
                        'quantity': line.product_uom_qty,
                        'display_name': product_obj.display_name,
                        'price_unit': line.price_unit,
                        'product': product_obj.read(['name', 'display_name', 'list_price', 'ean13', 'description_sale','virtual_available'])[0],
                        'description':line.name,
                    }
                    sale_order_lines.append(line)
            values = {
                'sale_order_id':sale_order_id,
                'partner_id': sale_order.partner_id.read(['name', 'property_product_pricelist'])[0],
                'payment_term': sale_order.payment_term.id if sale_order.payment_term else False,
                'notes': sale_order.notes,
                'lines': sale_order_lines,
                'date_order':self._get_datetime(sale_order.date_order) or '',
            }
            return [values]
        else:
            return False

    @api.multi
    def _get_datetime(self, date_time):
        if self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        date_from = pytz.utc.localize(datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)
        date = date_from.strftime("%d-%m-%Y %H:%M")
        return date

    @api.model
    def load_sale_order_by_query(self, query):
        sale_order = self.search_read(['|', ('barcode','=',query),('name','ilike',query), ['state','=','draft']],['id'])
        if sale_order and sale_order[0] and sale_order[0].get('id'):
            return self.load_sale_order_by_id(sale_order[0].get('id'))
        else:
            return False

    @api.model
    def get_product_price(self, pricelist_id, product_id):
        pricelist = self.env['product.pricelist'].browse(int(pricelist_id))
        res = []
        if pricelist:
            new_price = pricelist.price_get(product_id, 1)
            if new_price:
                res.append({
                    'product_id': product_id,
                    'new_price': new_price.get(int(pricelist_id))
                })
        if res:
            return res
        return False

    @api.model
    def get_product_tax_amount(self, price_unit, quantity, product_id, partner_id):
        val = 0.0
        product_id = self.env['product.product'].browse(product_id)
        partner_id = self.env['res.partner'].browse(partner_id)
        for c in self.pool['account.tax'].compute_all(
                self._cr, self._uid, product_id.taxes_id, float(price_unit), float(quantity),
                product_id, partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return {
            'amount': val,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: