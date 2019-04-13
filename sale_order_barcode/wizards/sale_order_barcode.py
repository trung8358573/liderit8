# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError


class SaleOrderBarcode(models.TransientModel):
    _name = 'sale.order.barcode'
    _description = 'Sale Order Barcode Wizard'

    product_barcode = fields.Char(
        string='Product Barcode (EAN13)',
        help="This field is designed to be filled with a barcode reader")
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True)
    product_qty = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0)
    product_uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='Unit of Measure',
        required=True)
    type = fields.Selection(
        [
            ('insert', 'Insert'),
            ('update', 'Update'),
        ],
        string='Type',
        required=True,
        default=lambda self: self._context.get('type', 'insert')
    )

    @api.multi
    def _prepare_domain(self):
        self.ensure_one()
        domain = [
            ('ean13', '=', self.product_barcode),
            ('sale_ok', '=', True)
        ]
        return domain

    @api.multi
    def _check_uom(self, lines):
        self.ensure_one()
        new_uom = self.product_uom_id.id
        old_uom = lines.product_uom.id

        if new_uom != old_uom:
            return False
        else:
            return True

    @api.multi
    def _convert_uom(self, lines, product_qty):
        self.ensure_one()
        obj_product = self.env['product.uom']
        from_uom = self.product_uom_id.id
        to_uom = lines.product_uom.id

        return obj_product._compute_qty(
            from_uom_id=from_uom,
            qty=product_qty,
            to_uom_id=to_uom)

    @api.onchange('product_barcode')
    def product_barcode_onchange(self):
        obj_product = self.env['product.product']
        if self.product_barcode:
            domain = self._prepare_domain()
            products = obj_product.search(domain)
            if len(products) == 1:
                self.product_id = products[0]
            elif len(products) > 1:
                return {'warning': {
                    'title': _('Error'),
                    'message': _(
                        'Several products have been found '
                        'with this code as EAN13 or Internal Reference:\n %s'
                        '\nYou should select the right product manually.'
                        ) % '\n'.join([
                            product.name_get()[0][1] for product in products
                        ])}}
            else:
                return {'warning': {
                    'title': _('Error'),
                    'message': _(
                        'No product found with this code as '
                        'EAN13 or product is not for sale. You should select '
                        'the right product manually.')}}

    @api.onchange('product_id')
    def product_id_onchange(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.multi
    def create_sale_order_line(self):
        self.ensure_one()
        obj_sale_order_line = self.env['sale.order.line']
        active_id = self._context['active_id']

        lines = obj_sale_order_line.search([
            ('order_id', '=', active_id),
            ('product_id', '=', self.product_id.id),
        ])

        if len(lines) == 1:
            check_uom = self._check_uom(lines)
            if check_uom is True:
                product_qty = self.product_qty
            else:
                product_qty = self._convert_uom(
                    lines,
                    self.product_qty
                )
            if self.type == 'insert':
                lines.write({
                    'product_uom_qty': lines.product_uom_qty + product_qty
                })
            elif self.type == 'update':
                lines.write({
                    'product_uom_qty': product_qty
                })
        elif len(lines) > 1:
            raise UserError(_("More than 1 line found"))

        elif len(lines) == 0:
            obj_sale_order_line.create({
                'order_id': active_id,
                'product_id': self.product_id.id,
                'product_uom': self.product_uom_id.id,
                'product_uom_qty': self.product_qty
            })

    @api.multi
    def save(self):
        self.ensure_one()
        self.create_sale_order_line()
        action = {
            'name': _('Sale Order Barcode Interface'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.barcode',
            'view_mode': 'form',
            'nodestroy': True,
            'target': 'new',
            'context': self._context,
            }
        return action
