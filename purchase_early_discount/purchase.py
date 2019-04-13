# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""Inherit purchase_order to add early payment discount"""

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp

import logging 
_logger = logging.getLogger(__name__)

class purchase_order(models.Model):
    """Inherit purchase_order to add early payment discount"""

    _inherit = "purchase.order"


    @api.one
    @api.depends('order_line', 'early_payment_discount',
                 'order_line.price_unit',
                 'order_line.taxes_id',
                 'order_line.discount',
                 'order_line.product_qty'
                 )

    def _amount_all2(self):
        """calculates functions amount fields"""

        if not self.early_payment_discount:
            self.early_payment_disc_total = self.amount_total
            self.early_payment_disc_tax = self.amount_tax
            self.early_payment_disc_untaxed = self.amount_untaxed
        else:
            cur = self.pricelist_id.currency_id
            self.early_payment_disc_tax = self.amount_tax *\
                    (1.0 - (float(self.early_payment_discount or 0.0)) /
                         100.0)
            self.early_payment_disc_untaxed = self.amount_untaxed *\
                    (1.0 - (float(self.early_payment_discount or 0.0)) /
                         100.0)
            self.early_payment_disc_total = self.amount_total *\
                    (1.0 - (float(self.early_payment_discount or 0.0)) /
                         100.0)
            self.total_early_discount = self.early_payment_disc_untaxed - \
                self.amount_untaxed

    def _get_order(self, cr, uid, ids, context={}):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    early_payment_discount = fields.Float('E.P. disc.(%)', digits=(16,2), help="Early payment discount")
    early_payment_disc_total = fields.Float('With E.P.', digits_compute=dp.get_precision('Account'), compute='_amount_all2')
    early_payment_disc_untaxed = fields.Float('Untaxed Amount E.P.', digits_compute=dp.get_precision('Account'), compute='_amount_all2')
    early_payment_disc_tax = fields.Float('Taxes E.P.', digits_compute=dp.get_precision('Account'), compute='_amount_all2')
    total_early_discount = fields.Float('E.P. amount', digits_compute=dp.get_precision('Account'), compute='_amount_all2')

    def onchange_partner_id2(self, cr, uid, ids, part, early_payment_discount=False, payment_term=False):
        """ Extend this event for delete early payment discount if it isn't
            valid to new partner or add new early payment discount
        """
        res = self.onchange_partner_id(cr, uid, ids, part)
        if not part:
            res['value']['payment_term_id'] = False
            res['value']['early_payment_discount'] = False
            return res

        if payment_term != res['value'].get('payment_term_id', False):
            payment_term = res['value']['payment_term_id']

        discount = self.onchange_payment_term(cr, uid, ids, payment_term, part)
        res['value']['early_payment_discount'] = discount['value']\
                                                ['early_payment_discount']
        return res

    def onchange_payment_term(self, cr, uid, ids, payment_term, part=False):
        """onchange event to update early payment dicount when the payment term changes"""
        """ On change event to update early payment dicount when the payment 
            term changes
        """

        early_discount_obj = self.pool.get('account.partner.payment.'\
                                           'term.early.discount')
        early_discs = []
        res = {}
        if payment_term:
            early_discs = early_discount_obj.search(cr, uid, [
                                      ('partner_id', '=', part),
                                      ('payment_term_id', '=', payment_term),
                                      ('is_supplier','=',True)])
            if early_discs:
                res['early_payment_discount'] = early_discount_obj.browse(cr,
                                  uid, early_discs[0]).early_payment_discount

            else:
                early_discs = early_discount_obj.search(cr, uid, [
                                      ('partner_id', '=', False),
                                      ('payment_term_id', '=', payment_term),
                                      ('is_supplier','=',True)])
                if early_discs:
                    res['early_payment_discount'] = early_discount_obj.browse(
                              cr, uid, early_discs[0]).early_payment_discount

        if not early_discs:
            early_discs = early_discount_obj.search(cr, uid, [
                                      ('partner_id', '=', part),
                                      ('payment_term_id', '=', False),
                                      ('is_supplier','=',True)])
            if early_discs:
                res['early_payment_discount'] = early_discount_obj.browse(cr,
                                  uid, early_discs[0]).early_payment_discount
            else: # Search default discount for everbody
                early_discs = early_discount_obj.search(cr, uid, [
                                      ('partner_id', '=', False),
                                      ('payment_term_id', '=', False),
                                      ('is_supplier','=',True)])
                if early_discs:
                    res['early_payment_discount'] = early_discount_obj.browse(
                              cr, uid, early_discs[0]).early_payment_discount
                else: # Delete early payment discount if there isn't early discount
                    res['early_payment_discount'] = False
        return {'value': res}

    @api.multi
    def action_invoice_create(self):

        invoice_id = super(purchase_order, self).action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        current_pur = self and self[0] or False
        _logger.error('########### Entra en purchase discount invoice create')
        if current_pur.early_payment_discount:
          _logger.error('########### Entra en purchase discount invoice create valor de early payment: %s' % current_pur.early_payment_discount)
          invoice.write({'early_payment_discount': current_pur.early_payment_discount})

        return invoice_id


class purchase_line_invoice(models.Model):
    """Inherit purchase_order to add early payment discount"""

    _inherit = "purchase.order.line_invoice"

    @api.multi
    def _make_invoice_by_partner(self):

        invoice_id = super(purchase.order.line_invoice,self)._make_invoice_by_partner(self)
        invoice = self.env['account.invoice'].browse(invoice_id)
        _logger.error('########### Entra en purchase line invoice make by partner con valor de orders %s'%self.orders)

        for order in self.orders:
          purchase = self.env['purchase.order'].browse(order.id)
        
          _logger.error('########### Entra en purchase line invoice make by partner para la compra %s'%purchase.id)
          if purchase.early_payment_discount:
            _logger.error('########### Entra en purchase line invoice make by partner valor de early payment: %s' % purchase.early_payment_discount)
            invoice.write({'early_payment_discount': purchase.early_payment_discount})

        return invoice_id

    @api.multi
    def makeInvoices(self):

      result = super(purchase.order.line_invoice,self).makeInvoices(self)
      _logger.error('########### Entra en purchase line invoice makeInvoices que da result %s'%result)

      return result