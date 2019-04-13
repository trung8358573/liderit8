from openerp import fields, models, api


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    proyecto_id = fields.One2many('project.project', compute='_get_proyecto', string='Proyectos')
    sale_ids = fields.One2many('sale.order', 'project_id', string='Budget', domain=[('state', 'in', ['draft', 'send', 'cancel'])])

   
    @api.model
    def _get_proyecto(self):
        for order in self:
            order.proyecto_id = self.env['project.project'].search([('analytic_account_id', '=', order.id)]).ids

class sale_order(models.Model):
	_inherit = 'sale.order'

	proyecto_id = fields.One2many (related='project_id.proyecto_id')
