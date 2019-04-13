# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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

from openerp import models, fields, api
from datetime import datetime
from openerp import exceptions

import logging 
_logger = logging.getLogger(__name__)

class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):

        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                pack_datas = {
                    'lot_id': prod.lot_id.id,
                    'life': prod.lot_id.life_date,
                    'date': datetime.now(), # prod.date if prod.date else 
                }

                if pack_datas['lot_id'] and (str(pack_datas['life']) < str(pack_datas['date'])):
                    raise exceptions.ValidationError('Está intentando utilizar un producto caducado.')
                    _logger.error('########### Producto caducado')

        _logger.error('########### Transferido')
        super(stock_transfer_details, self).do_detailed_transfer()
