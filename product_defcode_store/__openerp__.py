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

{
    'name': 'Store Default Code Product',
    'version': '1.0',
    "category": 'Product',
    'description': """
Almacena el campo referencia interna del producto
=============================================================
    Despues de instalar este modulo el modelo de datos
    almacena el valor de referencia interna
    y permite ordenar las vistas por referencia interna.
    
    """,
    "author": "LiderIT",
    'maintainer': 'LiderIT',
    'website': 'http://www.liderit.es',
    "license": "AGPL-3",
    'images': [],
    'depends': ['product'],
    'data': [
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
