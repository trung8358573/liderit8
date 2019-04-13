# -*- coding: utf-8 -*-
{
    'name': "Purchase Global Discount",

    'summary': """
    """,

    'description': """
Purchase Global Discount
========================
Option to set fix and percentage discount.

Percentage Discount
-------------------
A percentage amount deducted from each line as disount

Fixed Discount
--------------
Fixed amount is divided based on subtotal and deducted from each line
    """,

    'author': "LiderIT",
    'website': "http://liderit.es",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'purchase_discount', 'product', 'sale', 'liderit_global_discount'],
    # always loaded
    'data': [
        'purchase_view.xml',
    ],
}
