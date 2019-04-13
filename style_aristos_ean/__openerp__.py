# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: el_rodo_1 (rodo@vauxoo.com)
############################################################################
#    Migrated to Odoo 8.0 by Acysos S.L. - http://www.acysos.com
#    Adapted to Style Aristos by LiderIT S.L. http://www.liderit.es
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
    'name': 'Products Ean Generator for Style Aristos',
    'version': '1.0',
    'author': 'Acysos S.L., LiderIT, S.L.',
    'website': 'http://www.liderit.es/',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Product',
    'summary': 'Multiple create ean codes from code',
    'depends': [
            'base',
            'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ean_generator_view.xml',
    ],
    'active': False,
    'installable': True,
}
