# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    invoice_partner_id = fields.Many2one(
        'res.partner',
        string="Invoice Address")


    def _prepare_invoice_data(self, cr, uid, contract, context=None):
        context = context or {}
        invoice = super(AccountAnalyticAccount, self)._prepare_invoice_data(
            cr, uid, contract, context=context)
        if contract.invoice_partner_id:
            invoice.update({
                'partner_id': contract.invoice_partner_id
                and contract.invoice_partner_id.id})
        return invoice
