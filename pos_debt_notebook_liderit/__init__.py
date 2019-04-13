# -*- coding: utf-8 -*-

import models

from openerp import SUPERUSER_ID
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class AccountAccount(models.Model):
    _inherit = 'account.account'

    deb_tpv_bool = fields.Boolean(string='Cuenta para deudas de TPV')

    @api.one
    @api.constrains('deb_tpv_bool')
    def _check_deb_tpv_bool(self):
        if self.deb_tpv_bool:
            deb_tpv_bool = self.search([('id','!=',self.id),('deb_tpv_bool','=',True)], limit=1)
            if deb_tpv_bool:
                raise ValidationError("Ya hay una cuenta para crédito en TPV")


def init_debt_journal(cr, registry):
    if registry['ir.model.data'].search(cr, SUPERUSER_ID, [('name', '=', 'debt_account')]):
        # Use account journal from module version < 2.0.0, don't supported multi-company mode
        return

    company_ids = registry['res.company'].search(cr, SUPERUSER_ID, [])
    for company in registry['res.company'].browse(cr, SUPERUSER_ID, company_ids):
        if len(registry['account.account'].search(cr, SUPERUSER_ID, [('company_id', '=', company.id)])) == 0:
            # You have to configure chart of account for company
            continue

        debt_journal_active = registry['account.journal'].search(cr, SUPERUSER_ID, [
            ('company_id', '=', company.id), ('debt', '=', True)])
        if debt_journal_active:
            continue

        '''
        debt_account = registry['account.account'].search(cr, SUPERUSER_ID, [
            ('code', '=', 'XDEBT'), ('company_id', '=', company.id)])
        '''
        debt_account = registry['account.account'].search(cr, SUPERUSER_ID, [
            ('deb_tpv_bool', '=', True), ('company_id', '=', company.id)])
        
        parent_id = registry['account.account'].search(cr, SUPERUSER_ID, [
            ('code', '=', '4300'), ('company_id', '=', company.id)])

        if debt_account:
            debt_account = debt_account[0]
        else:
            debt_account = registry['account.account'].create(cr, SUPERUSER_ID, {
                'name': 'Debt',
                # 'code': 'XDEBT',
                'code': '430090000',
                'parent_id': parent_id[0],
                'type': 'liquidity',
                'user_type': registry.get('ir.model.data').get_object_reference(cr, SUPERUSER_ID, 'account', 'data_account_type_asset')[1],
                'company_id': company.id,
                #'note': 'code "XDEBT" should not be modified as it is used to compute debt',
            })
            registry['ir.model.data'].create(cr, SUPERUSER_ID, {
                'name': 'debt_account_' + str(company.id),
                'model': 'account.account',
                'module': 'pos_debt_notebook_liderit',
                'res_id': debt_account,
                'noupdate': True,  # If it's False, target record (res_id) will be removed while module update
            })

        debt_journal_inactive = registry['account.journal'].search(cr, SUPERUSER_ID, [
            ('company_id', '=', company.id), ('debt', '=', False), ('code', '=', 'TDEBT')])
        if debt_journal_inactive:
            new_journal = registry['account.journal'].browse(cr, SUPERUSER_ID, debt_journal_inactive[0])
            new_journal.write({
                'debt': True,
                'default_debit_account_id': debt_account,
                'default_credit_account_id': debt_account,
            })
            new_journal = new_journal.id
        else:
            new_sequence = registry['ir.sequence'].create(cr, SUPERUSER_ID, {
                'name': 'Account Default Debt Journal ' + str(company.id),
                'padding': 3,
                'prefix': 'DEBT ' + str(company.id),
            })
            registry['ir.model.data'].create(cr, SUPERUSER_ID, {
                'name': 'journal_sequence' + str(new_sequence),
                'model': 'ir.sequence',
                'module': 'pos_debt_notebook_liderit',
                'res_id': new_sequence,
                'noupdate': True,  # If it's False, target record (res_id) will be removed while module update
            })
            new_journal = registry['account.journal'].create(cr, SUPERUSER_ID, {
                'name': 'Debt Journal',
                'code': 'TDEBT',
                'type': 'cash',
                'debt': True,
                'journal_user': True,
                'sequence_id': new_sequence,
                'company_id': company.id,
                'default_debit_account_id': debt_account,
                'default_credit_account_id': debt_account,
            })
            registry['ir.model.data'].create(cr, SUPERUSER_ID, {
                'name': 'debt_journal_' + str(new_journal),
                'model': 'account.journal',
                'module': 'pos_debt_notebook_liderit',
                'res_id': int(new_journal),
                'noupdate': True,  # If it's False, target record (res_id) will be removed while module update
            })

        config_ids = registry['pos.config'].search(cr, SUPERUSER_ID, [('company_id', '=', company.id)])
        for config in registry['pos.config'].browse(cr, SUPERUSER_ID, config_ids):
            config.write({
                'journal_ids': [(4, new_journal)],
                'debt_dummy_product_id': registry.get('ir.model.data').get_object_reference(cr, SUPERUSER_ID, 'pos_debt_notebook_liderit', 'product_pay_debt')[1],
            })
