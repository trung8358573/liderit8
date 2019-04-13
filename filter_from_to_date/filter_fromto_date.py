# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv

class stock_picking(osv.osv):
    _inherit = 'account.move.line'

    _columns = {
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
    	'due_date_from': fields.function(
    	    lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
    	),
    	'due_date_to': fields.function(
    	    lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
    	),
    }

class stock_move(osv.osv):
    _inherit = 'stock.move'

    _columns = {
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }

class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
    	'due_date_from': fields.function(
    	    lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
    	),
    	'due_date_to': fields.function(
    	    lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
    	),
    }

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    _columns = {
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }

class account_imove_line(osv.osv):
    _inherit = 'account.move.line'

    _columns = {
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    _columns = {
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
