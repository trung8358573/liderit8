from openerp import models, fields, api

class SaleWeight(models.Model):

   _inherit = 'sale.order.line'

   so_weight = fields.Float(string='Gross Weight',
                               store=True,
                               related='product_id.weight')
   so_net_weight = fields.Float(string='Net Weight',
                               store=True,
                               related='product_id.weight_net')
   so_quantity = fields.Float(string='Quantity',
                               store=True,
                               related='product_uom_qty')

class SaleWeightOrder(models.Model):

    _inherit = 'sale.order'
    @api.depends('order_line.so_weight')
    @api.depends('order_line.so_net_weight')
    @api.depends('order_line.so_quantity')
    def _calcweight(self):
        # Added for to control multiple calls
        for sale in self:
            currentweight = 0
            for order_line in sale.order_line:
                if order_line.product_tmpl_id:
                    wht = order_line.product_tmpl_id.weight
                else:
                    if order_line.product_id:
                        wht = order_line.product_id.product_tmpl_id.weight
                    else:
                        wht = 0
                currentweight += (wht * order_line.product_uom_qty)

            sale.so_weight_total = currentweight

    so_weight_total = fields.Float(compute='_calcweight', string='Total Gross Weight')

    def _calcweight_net(self):
        # Added for to control multiple calls
        for sale in self:
            currentweight_net = 0
            for order_line in sale.order_line:
                if order_line.product_tmpl_id:
                    wht = order_line.product_tmpl_id.weight
                else:
                    if order_line.product_id:
                        wht = order_line.product_id.product_tmpl_id.weight
                    else:
                        wht = 0
                currentweight_net +=  (wht * order_line.product_uom_qty)

            sale.so_net_weight_total = currentweight_net

    so_net_weight_total = fields.Float(compute='_calcweight_net', string='Total Net Weight')
