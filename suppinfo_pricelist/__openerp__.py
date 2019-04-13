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
    'name': 'Purchase Pricelist',
    'version': '1.0',
    "category": 'Purchase',
    'description': """
Gestiona las tarifas de compra
=============================================================
    Despues de instalar este modulo se podran visualizar
    las tarifas de compra por provedor y articulo.
    
    """,
    "author": "LiderIT",
    'maintainer': 'LiderIT',
    'website': 'http://www.liderit.es',
    "license": "AGPL-3",
    'images': [],
    'depends': ['purchase'],
    'data': [
        'suppinfo_pricelist.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
