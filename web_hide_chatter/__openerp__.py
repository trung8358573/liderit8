# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
    "name": "Hide chatter in sheets",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA),LiderIT",
    "license": "AGPL-3",
    "summary": "Hide chatter area when displaying sheets",
    "description": """
Description
-----------
This addon hide chatter area


Acknowledgements
----------------
Icon courtesy of http://www.picol.org/ (size_width.svg)
    """,
    "category": "Tools",
    "depends": [
        'web',
    ],
    "data": [
        "view/qweb.xml",
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
