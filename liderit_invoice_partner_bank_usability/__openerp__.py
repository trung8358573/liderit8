# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Invoice Partner Bank Usability module for Odoo
#    Copyright (C) 2013-2016 Akretion (http://www.akretion.com)
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
    'name': 'Lider IT Invoice Partner Bank Usability',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Configure a bank account by default for customer invoices',
    'description': """
Lider IT Account Invoice Partner Bank Usability
======================================

This module adds a configuration parameter on the partner bank that allows you to choose which bank account will be selected by default on customer invoices.

    """,
    'author': 'Akretion, Lider IT',
    'website': 'http://www.liderit.es',
    'depends': ['account'],
    'data': ['company_view.xml'],
    'installable': True,
}
