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


{
    'name': 'Sale Margin Report LIDER',
    'version': '0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Add margin measure in Sales Analysis',
    'description': """
This module adds the measure *Margin* in the Sales Analysis pivot table.

    """,
    'author': 'Lider IT',
    'website': 'http://www.liderit.es',
    'depends': ['sale'],
    'data': ['report/sale_view.xml'],
    'installable': True,
}
