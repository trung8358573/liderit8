# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

from openerp import models, fields, api

from openerp.addons.account.wizard.pos_box import CashBox

import logging 
_logger = logging.getLogger(__name__)


class CashBoxOut(CashBox):

	_inherit = 'cash.box.out'

	account_id = fields.Many2one('account.account', string='Cuenta')

	def _compute_values_for_statement_line(self, cr, uid, box, record, context=None):

		values = super(CashBoxOut, self)._compute_values_for_statement_line(cr, uid, box, record, context=context)

		# for ibox in box:

		# 	new_account = self.pool.get('cash.box.out').search(cr, uid, [('id','=',ibox)])

		_logger.error('########### Valor de account: %s', box.account_id)

		values['account_id'] = box.account_id.id

		return values
