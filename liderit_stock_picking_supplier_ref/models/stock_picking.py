# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api
from openerp.exceptions import Warning


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    supplier_ref = fields.Char(
        string='Supplier Ref.')


    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking, context=None):

    	active_id = len(picking) and picking[0] or False
    	this_picking = self.browse(cr,uid,active_id)

        if this_picking.supplier_ref == False and this_picking.picking_type_code == 'incoming':
            raise Warning('Tiene que indicar un documento de proveedor')
            return False
        else:
        	return super(StockPicking, self).do_enter_transfer_details(cr, uid, picking, context=context)
