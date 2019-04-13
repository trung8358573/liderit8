__author__ = 'one'

from openerp import models, api, fields, _

class MenuLookupWizard(models.TransientModel):
    _name = 'builder.ir.ui.menu.lookup.wizard'

    model_source = fields.Selection([('system', 'System'), ('development', 'Development')], 'Type', default='development')
    system_model_id = fields.Many2one('ir.ui.menu', 'Menu')
    development_model_id = fields.Many2one('builder.ir.ui.menu', 'Menu')
    lookup_mode = fields.Selection([('id', 'ID'), ('name', 'Name'), ('field', 'Field'), ('ref', 'Reference')], 'Lookup Mode', default='name', required=True)
    lookup_value = fields.Char('Lookup Value')
    show_type_selection = fields.Boolean('Show Type Selection', default=True)

    @api.onchange('model_source', 'system_model_id', 'development_model_id', 'lookup_mode')
    def lookup_value_update(self):
        self.lookup_value = self.get_value()

    @api.multi
    def action_lookup(self):

        active_model = self.env[self.env.context.get('active_model')].search([('id', '=', self.env.context.get('active_id'))])

        if active_model.id:
            setattr(active_model, self.env.context.get('target_field'), self.get_value())

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def get_value(self):
        raw_value = self.model_source == 'system' and self.system_model_id or self.development_model_id

        if self.lookup_mode == 'id':
            return raw_value.id
        elif self.lookup_mode == 'name':
            return getattr(raw_value, raw_value._rec_name, False)
        elif self.lookup_mode == 'field':
            return getattr(raw_value, self.env.context.get('lookup_field'), False)
        elif self.lookup_mode == 'ref':
            data = self.env['ir.model.data'].search([('model', '=', self.model_source == 'system' and 'ir.ui.menu' or 'builder.ir.ui.menu'), ('res_id', '=', raw_value.id)])
            if data:
                return "{module}.{id}".format(module=data.module, id=data.name)
            else:
                return False
