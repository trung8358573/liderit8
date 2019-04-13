# -*- coding: utf-8 -*-
##############################################################################
#
#    Sale Margin Report module for Odoo
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

from openerp import models, fields
import openerp.addons.decimal_precision as dp


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin_total = fields.Float(
        string='Margin', readonly=True,
        digits=dp.get_precision('Account'))

    def _select(self):
        select = super(SaleReport, self)._select()
        select += """
        ,sum(l.margin / cr.rate ) as margin_total
        """
        return select
