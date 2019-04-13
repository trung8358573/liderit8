# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Gestion-Ressources
#    (<http://www.gestion-ressources.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account Voucher for LiderIT',
    'version': '1.0',
    "category": 'Accounting & Finance',
    'description': """
Filtra el uso de proveedores en la emision de cheques de pago
==============================================================
Con este modulo en la emision de cheques solo figuran proveedores
y el importe se traduce a texto castellano en letra

    """,
    "author": "LiderIT",
    'maintainer': 'LiderIT',
    'website': 'http://www.liderit.es',
    "license": "AGPL-3",
    'images': [],
    'depends': ['account_voucher'],
    'data': [
        'account_voucher_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
