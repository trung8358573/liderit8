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


from openerp import api, fields, models

import logging
_logger = logging.getLogger(__name__)



class res_partner(models.Model):
    _inherit = 'res.partner'

    
    def _sale_credit_get(self, cr, uid, ids, field_names, arg, context=None):
        ctx = context.copy()
        ctx['all_fiscalyear'] = True
        #query = self.pool.get('account.move.line')._query_get(cr, uid, context=ctx)
        cr.execute("""SELECT p.id, 'receivable', s.residual
                      FROM res_partner p
                      JOIN sale_order s ON (s.partner_id = p.id)
                      WHERE  p.id IN %s
                          AND s.state != 'cancel'
                          AND s.state != 'draft'
                      union all
                      SELECT p.id, 'receivable', i.residual
                      FROM res_partner p
                      JOIN account_invoice i ON (i.partner_id=p.id)
                      WHERE p.id IN %s
                          AND i.state = 'open'
                      """,
                   (tuple(ids),))
        maps = {'receivable':'credit', 'payable':'debit' }
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0)
        for pid,type,val in cr.fetchall():
            if val is None: val=0
            res[pid][maps[type]] = (type=='receivable') and val or -val
        return res


    total_credit = fields.function(_sale_credit_get, string='Total Receivable', store=True)
    
    #con_credito = fields.Char('Con Credito', size=20)


