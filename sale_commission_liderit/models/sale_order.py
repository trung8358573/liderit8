# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
import logging 


_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.agents.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.order_line:
                record.commission_total += sum(x.amount for x in line.agents)

    commission_total = fields.Float(
        string="Commissions", compute="_compute_commission_total",
        store=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _default_agents(self):
        agents = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for agent in partner.agents:
                agents.append({'agent': agent.id,
                               'commission': agent.commission.id})
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(
        string="Agents & commissions",
        comodel_name='sale.order.line.agent', inverse_name='sale_line',
        copy=True, readonly=True, default=_default_agents)
    commission_free = fields.Boolean(
        string="Comm. free", related="product_id.commission_free",
        store=True, readonly=True)

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            line, account_id=account_id)
        vals['agents'] = [
            (0, 0, {'agent': x.agent.id,
                    'commission': x.commission.id}) for x in line.agents]
        return vals


class SaleOrderLineAgent(models.Model):
    _name = "sale.order.line.agent"
    _rec_name = "agent"

    sale_line = fields.Many2one(
        comodel_name="sale.order.line", required=True, ondelete="cascade")
    agent = fields.Many2one(
        comodel_name="res.partner", required=True, ondelete="restrict",
        domain="[('agent', '=', True')]")
    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")
    amount = fields.Float(compute="_compute_amount", store=True)

    # _sql_constraints = [
    #     ('unique_agent', 'UNIQUE(sale_line, agent)',
    #      'You can only add one time each agent.')
    # ]

    @api.onchange('agent')
    def onchange_agent(self):
        self.commission = self.agent.commission

    @api.depends('sale_line.price_subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = 0.0
            if (not line.sale_line.product_id.commission_free and
                    line.commission):
                if line.commission.amount_base_type == 'net_amount':
                     # subtotal = (line.sale_line.price_subtotal -
                     #            (line.sale_line.product_id.standard_price *
                     #            line.sale_line.product_uom_qty))
                     #Se ha modificado la sentencia para que se reste al producto su descuento correspondiente
                   
                     #subtotal = (line.sale_line.price_subtotal*(1- line.sale_line.discount/100.0))
                     subtotal = line.sale_line.price_subtotal
                   
                if line.commission.amount_base_type == 'gross_amount':
                    subtotal = (line.sale_line.price_subtotal/(1- line.sale_line.discount/100.0))
                    
 
               #Se añaden los dos siguientes casos para calcular la comision en base al margen bruto y neto
                if line.commission.amount_base_type == 'net_margin':
                    #se ha cambiado standard_price por price_unit                    
                    #subtotal = (line.sale_line.price_subtotal -
                             #  (line.sale_line.product_id.purchase_price *
                               # line.sale_line.product_uom_qty)
                     subtotal = (line.sale_line.price_subtotal -
                                line.sale_line.purchase_price* 
                                line.sale_line.product_uom_qty)
                

                if line.commission.amount_base_type == 'gross_margin':
                   #_logger.error('########### Valor price_subtotal: %s' % line.sale_line.price_subtotal)
                   subtotal = ((line.sale_line.price_subtotal/(1- line.sale_line.discount/100.0)) -
                                (line.sale_line.purchase_price *
                                 line.sale_line.product_uom_qty))
                    

                if line.commission.commission_type == 'fixed':
                    line.amount = subtotal * (line.commission.fix_qty / 100.0)
                else:
                    line.amount = line.commission.calculate_section(subtotal)
