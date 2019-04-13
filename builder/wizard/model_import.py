__author__ = 'one'

from openerp import models, api, fields, _


class ModelLine(models.TransientModel):
    _name = 'builder.ir.model.import.line'

    import_id = fields.Many2one('builder.ir.model.import.wizard', 'Wizard', required=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    create_fields = fields.Boolean('Include Fields')
    set_inherited = fields.Boolean('Set as Inherit', default=True)


class ModelImport(models.TransientModel):
    _name = 'builder.ir.model.import.wizard'

    model_ids = fields.Many2many('ir.model', 'builder_ir_model_import_wizard_model_rel', 'wizard_id', 'model_id', 'Models')
    exclude_fields = fields.Boolean('Exclude Fields')
    create_fields = fields.Boolean('Include Fields')
    relations_only = fields.Boolean('Relations Only')
    set_inherited = fields.Boolean('Set as Inherit', default=True)
    exclude_auto_fields = fields.Boolean('Exclude Auto Fields', default=True)

    @api.one
    def _create_model_fields(self, module, model_items, model_map, relations_only=True):

        _review_models = []

        for model in model_items:
            module_model = self.env['builder.ir.model'].search([('module_id', '=', module.id), ('model', '=', model.model)])

            for field in model.field_id:
                if not self.set_inherited and self.exclude_auto_fields and field.name in ['id', 'write_date', 'create_date']:
                    continue

                if not self.env['builder.ir.model.fields'].search([('model_id', '=', module_model.id), ('name', '=', field.name)]):
                    values = {
                        'model_id': model_map[model.model].id,
                        'name': field.name,
                        'field_description': field.field_description,
                        'ttype': field.ttype,
                        'selection': field.selection,
                        'required': field.required,
                        'readonly': field.readonly,
                        'select_level': field.select_level,
                        'translate': field.translate,
                        'size': field.size,
                        'on_delete': field.on_delete,
                        'domain': field.domain,
                        'selectable': field.selectable,
                        'is_inherited': self.set_inherited,
                        'redefine': not self.set_inherited
                    }

                    if field.ttype in ['one2many', 'many2many', 'many2one']:
                        if field.relation in model_map:
                            values.update({
                                'relation': field.relation,
                                'relation_model_id': model_map[field.relation].id,
                                'relation_field': field.relation_field
                            })

                            _review_models.append(model)
                        else:
                            continue

                    if not relations_only or (relations_only and field.ttype in ['one2many', 'many2many', 'many2one']):
                        new_field = model_map[model.model].field_ids.create(values)

        if len(_review_models):
            self._create_model_fields(module, _review_models, model_map, relations_only)

    @api.one
    def action_import(self):
        model_obj = self.env['builder.ir.model']

        model_map = {}

        module = self.env[self.env.context.get('active_model')].search([('id', '=', self.env.context.get('active_id'))])

        for model in module.model_ids:
            model_map[model.model] = model

        for model in self.model_ids:
            module_model = self.env['builder.ir.model'].search([('module_id', '=', module.id), ('model', '=', model.model)])

            if model.modules:
                module.add_dependency(model.modules.split(', ')[0])

            if not module_model.id:
                new_model = model_obj.create({
                    'module_id': self.env.context.get('active_id'),
                    'name': model.name,
                    'model': model.model,
                    'osv_memory': model.osv_memory,
                    # 'inherit_model': self.set_inherited and model.model or False
                })

                if self.set_inherited:
                    new_model['inherit_model_ids'] = [{'model_source': 'system', 'system_model_id': model.id, 'system_model_name': model.model}]

                model_map[model.model] = new_model

        if (self.set_inherited and not self.exclude_fields) or (not self.set_inherited and (self.create_fields or self.relations_only) ):
            self._create_model_fields(module, self.model_ids, model_map, self.relations_only)

        return {'type': 'ir.actions.act_window_close'}