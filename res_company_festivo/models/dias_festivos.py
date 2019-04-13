# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

import openerp
from openerp.osv import osv, fields

import logging
_logger = logging.getLogger(__name__)

class ResHoliday(osv.osv):
	_name = "res.holiday"

	_columns = {
		'name': fields.date('Dia de vacaciones'),
	}

	


class ResCompany(osv.osv):
	_inherit = 'res.company'

	_columns={
		'holiday_ids': fields.many2many('res.holiday','res_company_holiday_rel','company_id','holiday_id','Dia de vacaciones'),
	}

	
	