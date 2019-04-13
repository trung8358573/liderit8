# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name  
            if operator in ('=ilike', '=like'):
                operator = operator[1:]
            query_args = {'name': search_name}
            limit_str = ''
            if limit:
                limit_str = ' limit %(limit)s'
                query_args['limit'] = limit
            search_name = query_args['name']
            cr.execute("SELECT p.id FROM res_partner p WHERE (p.name ilike '" + (search_name or '') + "%') OR (p.comercial ilike '" + (search_name or '') + "%') OR (p.ref ilike '" + (search_name or '') + "%') OR (p.mobile ilike '" + (search_name or '') + "%')  OR (p.email ilike '" + (search_name or '') + "%')  ")

            ids = map(lambda x: x[0], cr.fetchall())
            ids = self.search(cr, uid, [('id', 'in', ids)] + args, limit=limit, context=context)
            if ids:
                return self.name_get(cr, uid, ids, context)
        return super(res_partner, self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)