# -*- coding: utf-8 -*-
# Copyright© 2016 ICTSTUDIO <http://www.ictstudio.eu>
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Stock Picking Type To Invoice State',
    'version': '8.0.1.0.1',
    'category': 'Stock',
    'summary': """Setup Invoice State By Picking Type
    """,
    'author': 'LiderIT',
    'license': 'AGPL-3',
    'website': 'http://www.liderit.es',
    'depends': [
        'sale_stock'
    ],
    'data': [
        'views/stock_view.xml'
    ],
}