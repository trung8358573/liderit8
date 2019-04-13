# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SaleAdvancePaymentInvLine(models.TransientModel):
    _name = "sale.advance.payment.inv.line"

    sale_order_line_id = fields.Many2one('sale.order.line', string="Order Lines")
    name = fields.Char(string="Name", readonly=True)
    quantity = fields.Float(string="Quantity", readonly=True)
    subtotal = fields.Float(string="Subtotal", readonly=True)
    partial_invoice = fields.Float(string="To partial invoice")
    sale_advance_ref = fields.Many2one('sale.advance.payment.inv')

    @api.onchange("sale_order_line_id")
    def _onchange_sale_order_line_id_trust_parcial_invoice(self):
        vals = {}
        line = self.env['sale.order.line'].browse(self.sale_order_line_id)

        vals = {
            "name": line.name,
            "quantity": line.product_uom_qty,
            "subtotal": line.price_subtotal,
        }

        return vals
