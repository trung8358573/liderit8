# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Grzegorz Marczyński
#    Copyright 2016 QAQA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp import api, models
import openerp.addons.decimal_precision as dp


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def _cancelled_invoice(self, cr, uid, ids, field_names=None, arg=False, context=None):
        # check if there is any cancelled invoice with set internal_number
        #res_ids = self.search(cr, uid, [('state', '=', 'cancel'), ('internal_number', '!=', False)], context=context)
        # check if there is any cancelled invoice with set number
        res_ids = self.search(cr, uid, [('state', '=', 'cancel'), ('number', '!=', False),('type','=','out_invoice')], context=context)

        is_invoice = len(res_ids) > 0
        res = {id: is_invoice for id in ids}
        return res

    _columns = {
        'is_there_cancelled_invoice': fields.function(_cancelled_invoice, type="boolean",
                                                      string="Is there any cancelled invoice?", readonly=True),
    }

    def name_get(self, cr, uid, ids, context=None):
        # override in order to define custom methot for list presentation in the  selection widget
        if u'compute_name' in context:
            # check value from frontend and call custom method
            return getattr(self, context[u'compute_name'])(cr, uid, ids, context)
        else:
            # call base method
            return super(account_invoice, self).name_get(cr, uid, ids, context=context)

    def _get_cancelled_invoice_name(self, cr, uid, ids, context):
        # invoice presentation in the selection widget
        # this name is passed by context from view XML
        res = []
        for inv in self.browse(cr, uid, ids, context=context):
            #res.append((inv.id, "%s (%s)" % (inv.internal_number, inv.date_invoice)))
            res.append((inv.id, "%s (%s)" % (inv.number, inv.date_invoice)))
        return res


class Wizard(models.TransientModel):
    _name = 'account_invoice_reuse_cancelled_number.wizard'
    # wizard to present cancelled invoices for selection

    def _new_invoice(self):
        return self.env['account.invoice'].browse(self._context.get('active_id')).id

    def _last_cancelled_invoice(self):
        # show the least recently cancelled invoice
        #res_ids = self.pool['account.invoice'].search(self._cr, self._uid,
        #                                              [('state', '=', 'cancel'), ('internal_number', '!=', False)])
        res_ids = self.pool['account.invoice'].search(self._cr, self._uid,
                                                      [('state', '=', 'cancel'), ('number', '!=', False),('type','=','out_invoice')])
        if len(res_ids) > 0:
            return res_ids[len(res_ids) - 1]
        else:
            return False

    _columns = {
        'new_invoice_id': fields.many2one('account.invoice', string="This invoice", default=_new_invoice),
        #'cancelled_invoice_id': fields.many2one('account.invoice', string="Cancelled invoices",
        #                                        domain=[('state', '=', 'cancel'), ('internal_number', '!=', False)],
        #                                        default=_last_cancelled_invoice)
        'cancelled_invoice_id': fields.many2one('account.invoice', string="Cancelled invoices",
                                                domain=[('state', '=', 'cancel'), ('number', '!=', False),('type','=','out_invoice')],
                                                default=_last_cancelled_invoice)
    }

    @api.one
    def reuse_cancelled_invoice_number(self):
        # pass the internal number and the date from the cancelled invoice to the current draft invoice
        reuse_number = self.cancelled_invoice_id.number
        reuse_int_number = self.cancelled_invoice_id.internal_number
        reuse_inv_number = self.cancelled_invoice_id.invoice_number


        self.cancelled_invoice_id.internal_number = False
        self.cancelled_invoice_id.invoice_number = False
        self.cancelled_invoice_id.number = False
        #self.cancelled_invoice_id.date_invoice = False

        self.new_invoice_id.internal_number = reuse_int_number
        self.new_invoice_id.invoice_number = reuse_inv_number
        self.new_invoice_id.number = reuse_number
        self.new_invoice_id.date_invoice = self.cancelled_invoice_id.date_invoice
        self.new_invoice_id.journal_id = self.cancelled_invoice_id.journal_id
        
        return {}
