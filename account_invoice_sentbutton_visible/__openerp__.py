# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Invoice Sale Link module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Account Invoice Sent Button Visible',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Show Send by EMail Button in all Invoices',
    'description': """
Account Invoice Sent Button Visible
=========================

On the customer invoices, you usually need to send invoices in other states not open. 
For that, you need to have the button active, and this is not available in the official addons.

    """,
    'author': 'Lider IT',
    'website': 'http://www.liderit.es',
    'depends': ['account'],
    'data': ['account_invoice_view.xml'],
    'installable': True,
    'active': False,
}
