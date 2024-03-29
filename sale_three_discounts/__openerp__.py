# -*- coding: utf-8 -*-
##############################################################################
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
    "name": "Sale Three Discounts",
    'version': '8.0.0.1.0',
    'category': 'Sales Management',
    'sequence': 14,
    'author': 'Lider I.T.',
    'website': 'www.liderit.es',
    'license': 'AGPL-3',
    'summary': '',
    "description": """
Sale Three Discounts
====================
    """,
    "depends": [
        'base',
        'sale',
        'account',
        'purchase',
    ],
    'external_dependencies': {
    },
    "data": [
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
