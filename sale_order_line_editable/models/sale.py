# -*- coding: utf-8 -*-
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp import models, api, fields

import logging 
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_line = fields.One2many(
    	comodel_name='sale.order.line',
    	inverse_name='order_id',
    	string = 'Order Lines',
    	readonly=True,
    	states={
    	'draft': [('readonly', False)], 
    	'sent': [('readonly', False)],
    	'progress': [('readonly', False)],
    	'manual': [('readonly', False)],
    	'done': [('readonly', False)]
    	},
    	copy=True)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    name = fields.Text(string='Description', 
    	required=True, 
    	readonly=True, 
    	states={
    		'draft': [('readonly', False)],
    		'confirmed': [('readonly', False)],
    		'done': [('readonly', False)]
    		}
    	)