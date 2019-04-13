# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
import logging 


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_last_sale_order(self):
    	for record in self:
		    last_confirmed_order = self.env['sale.order'].search(
		        [('partner_id', '=', record.id)],
		        order='date_order desc',
		        limit=1
		    )

		    record['last_sale_order'] = last_confirmed_order.date_order or ''



    last_sale_order = fields.Datetime(string='Date of Last Sale Order', compute=_get_last_sale_order)

