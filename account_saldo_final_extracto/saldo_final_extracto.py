# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Hugo Santos (<http://factorlibre.com>).
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
from openerp.osv import osv, fields
from openerp import tools
import os, sys
import logging
_logger = logging.getLogger(__name__)

#ampliamos la clase account_journal para elegir si se calcula automáticamente el saldo final de un extracto bancario
class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'saldo_final': fields.boolean('Permitir calcular automáticamente el saldo final en un extracto bancario'),
    }
    _defaults = {
        'saldo_final': False
    }


class account_bank_statement(osv.osv):
	_inherit = 'account.bank.statement'
	
	def write(self, cr, uid, ids, vals, context=None):
		res = {}
		for stat in self.browse(cr, uid, ids, context):
			if stat.journal_id.saldo_final:
				vals['balance_end_real'] = stat.balance_end
				_logger.error('##### AIKO ###### Marcado saldo final en diario con valores %s'%vals)
				res = super(account_bank_statement, self).write(cr, uid, ids, vals, context=context)
		return res
