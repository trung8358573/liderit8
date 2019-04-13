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
 
# noinspection PyStatementEffect
{
    "name" : "sale_by_supplier",
    
    "author" : "Lider IT",
    
    "category" : "Ventas",
    "licence" : "AGPL-3",
    "description": """
sale_by_supplier
====================================
Show sales by supplier of sold products
                    """,
    "depends" : ['sale_margin'],
    "data" : [
        'views/sale_by_supplier_view.xml',
        'security/ir.model.access.csv'
        ],
    "demo" : [],
    "installable": True,
    "auto_install": False,
    "application": False,
}