# -*- coding: utf-8 -*-
# Copyright 2014 -2017 Alex Comba - Agile Business Group
# Copyright 2014 -2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'LiderIT Sale line properties price',
    'version': '8.0.1.0.0',
    'category': 'Sales Management',
    'author': "Agile Business Group, Odoo Community Association (OCA), LiderIT",
    'website': 'https://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'sale_properties_dynamic_fields',
    ],
    'data': [
        'views/product_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True
}
