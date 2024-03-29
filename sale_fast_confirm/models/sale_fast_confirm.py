# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Odoo, Open Source Management Solution
#
#    Author: Andrius Laukavičius. Copyright: JSC NOD Baltic
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

from openerp import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def order_process_now(self):
        """
        Confirms order and creates and validates invoice, confirms pickings.
        """
        for sale in self:
            # Process order 
            sale.action_button_confirm()
            inv_id = sale.action_invoice_create()
            if inv_id:
                inv = self.env['account.invoice'].browse(inv_id)
                inv.signal_workflow('invoice_open')
            for picking in sale.picking_ids:
                picking.force_assign()
                picking.action_done()

            view = self.env.ref(
                'account.'
                'invoice_form')

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.invoice',
                'res_id': inv_id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view.id,
                'target': 'current',
                'nodestroy': True,
            }



