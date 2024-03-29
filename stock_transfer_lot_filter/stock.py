# -*- coding: utf-8 -*-
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015 Rooms For (Hong Kong) Limited T/A OSCG
#    <https://www.odoo-asia.com>
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

from openerp import models, fields, api, _


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'
    
    @api.one
    @api.depends('product_id','ref','quant_ids.qty','quant_ids.location_id')
    def _compute_balance(self):
        int_loc_ids = self.env['stock.location'].search([('usage','=','internal')])
        location_ids = [loc.id for loc in int_loc_ids]
        quant_ids = self.env['stock.quant'].search([('lot_id','=',self.id), ('product_id','=',self.product_id.id), ('location_id','in',location_ids)])
        for quant in quant_ids:
            self.lot_balance += quant.qty
            
    lot_balance = fields.Float(string='Lot Qty on Hand',
        store=True, readonly=True, compute='_compute_balance')

    def init(self, cr):
        # update lot_balance field when installing
        cr.execute("""
            update stock_production_lot lot
            set lot_balance =
                (select sum(qty)
                from stock_quant
                where lot_id = lot.id
                and product_id = lot.product_id
                and location_id in
                    (select id
                    from stock_location
                    where usage = 'internal'
                    )
                )
        """)
