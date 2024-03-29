# -*- encoding: utf-8 -*-
##############################################################################
#    event_advanced
#    Copyright (c) 2016 Francisco Manuel García Claramonte <francisco@garciac.es>
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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

import logging
logger = logging.getLogger(__name__)



class SygColegio(models.Model):
    _inherit = ['syg.colegio']

    #tenemos que cortar el largo de los campos a utilizar en nuevos valores, porque el diseño no lo permite


    label_name = fields.Char(related="partner_id.name", size=34)
    label_street = fields.Char(related="partner_id.street", size=34)
    label_city = fields.Char(related="partner_id.city", size=26)
    provincia = fields.Char(string='Provincia',store=True,related='partner_id.state_id.name')