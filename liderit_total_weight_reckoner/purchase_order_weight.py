from openerp import models, fields, api

class PurchaseWeight(models.Model):

   _inherit = 'purchase.order.line'

   po_weight = fields.Float(string='Gross Weight',
                               store=True,
                               related='product_id.weight')
   po_net_weight = fields.Float(string='Net Weight',
                               store=True,
                               related='product_id.weight_net')
   po_quantity = fields.Float(string='Quantity',
                               store=True,
                               related='product_qty')

class PurchaseWeightOrder(models.Model):
  
    _inherit = 'purchase.order'
    @api.depends('order_line.po_weight')
    @api.depends('order_line.po_net_weight')
    @api.depends('order_line.po_quantity')
    def _calcweight(self):
        # Added for to control multiple calls
        for purchase in self:
            currentweight = 0
            for order_line in purchase.order_line:
                currentweight = currentweight + (order_line.po_weight * order_line.po_quantity)

            purchase.po_weight_total = currentweight

    po_weight_total = fields.Float(compute='_calcweight', string='Total Gross Weight')

    def _calcweight_net(self):
        # Added for to control multiple caslls
        for purchase in self:
            currentweight_net = 0
            for order_line in purchase.order_line:
                currentweight_net = currentweight_net + (order_line.po_net_weight * order_line.po_quantity)

            purchase.po_net_weight_total = currentweight_net

    po_net_weight_total = fields.Float(compute='_calcweight_net', string='Total Net Weight')