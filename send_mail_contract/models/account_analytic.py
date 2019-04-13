# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def send_mail_template(self):
        # Find the e-mail template
        #template = self.env.ref('mail_template_demo.example_email_template')
        template = self.env['email.template'].search([('name','=','plantilla_contrato')])
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        # if template:
        # 	self.env['email.template'].browse(template[0].id).send_mail(self.id)

        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        # template = self.env.ref('account.email_template_edi_invoice', False)
        try:
            template = self.env['email.template'].search([('name','=','plantilla_contrato')], limit=1).id
        except Exception:
                    return False    # view not found
        
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)

        ctx = dict(
            default_model='account.analytic.account',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }