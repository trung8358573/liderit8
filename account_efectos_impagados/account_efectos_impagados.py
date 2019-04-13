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


class account_move_line(osv.osv):
	_inherit = "account.move.line"

	def _get_devolucion(self, cr, uid, ids, name, args, context=None):
		res = {}

		for line in self.browse(cr, uid, ids, context=context):
			if line.invoice:
				invoice_or = line.invoice.id
				factura = self.pool.get('account.invoice').browse(cr, uid, invoice_or, context=context).returned_payment
				if factura:
					res[line.id] = True
				else:
					res[line.id] = False
			else:
				res[line.id] = False

		return res

	_columns = {
		'devolucion_cobro': fields.function(_get_devolucion, type='boolean', string="Es una devolución de cobro", store=True),
	}
