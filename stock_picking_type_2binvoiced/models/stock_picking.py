# -*- coding: utf-8 -*-
# Copyright© 2016 ICTSTUDIO <http://www.liderit.es>
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'


    invoice_type = fields.Selection([ ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")],string="Default Invoice Status")


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def _set_default_invoice_state(self):
    	result = 'none'
    	_logger.error('########### Valor de context en default invoice state: %s', self._context)
    	if self._context.get('default_picking_type_id'):
    		pick_type = self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id'))
    		if pick_type.invoice_type:
    			result = pick_type.invoice_type
    			_logger.error('########### Valor de pick_type_status en default invoice state: %s', pick_type.invoice_type)
        else:
            # esto porque el modulo stock_picking_menu modifica el context
            if self._context.get('default_picking_type_code'):
                pick_type = self.env['stock.picking.type'].search([
                    ('code', '=',self._context.get('default_picking_type_code'))],order='id', limit=1)
                if pick_type[0].invoice_type:
                    result = pick_type[0].invoice_type

    	return result


    invoice_state = fields.Selection(default =_set_default_invoice_state)
