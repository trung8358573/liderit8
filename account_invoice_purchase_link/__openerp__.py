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
    'name': 'Account Invoice Purchase Link',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Add the reverse link from invoices to purchase orders',
    'description': """
Account Invoice Purchase Link
=============================

On the partner invoice report, you usually need to display the partner order number. For that, you need to have the link from invoices to purchsae orders, and this link is not available in the official addons.

This module adds a field *purchase_ids* on the object account.invoice, which is the reverse many2many field of the field *invoice_ids* of the object purchase.order. It is displayed in a dedicated tab on the invoice form view.

    """,
    'author': 'LiderIT',
    'website': 'http://www.liderit.es',
    'depends': ['purchase'],
    'data': ['account_invoice_view.xml'],
    'installable': True,
    'active': False,
}
