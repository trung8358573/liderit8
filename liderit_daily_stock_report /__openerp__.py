# -*- coding: utf-8 -*-
{
    'name': "lider_it_daily_stock_report",

    'summary': """ Lider IT Daily Stock Report
    """,

    'description': """
Lider IT Daily Stock Report
==================

This modules gives you a comprehensive stock report based on various filters.

Need to instal pypdf with "sudo pip install fpdf"

Features:
---------
    * Get the output in a PDF file listing Product name, EAN13 / Internal Reference and default Unit of Measure
    * Option to filter by Product and Category
    * Option to filter by Stock Location
    * Choose between different weight UoM
    * Option for Opening, Incoming and Outgoing for a given date range
    * Option for fetching Valuation also
    
Future improvements:
--------------------
    * Combined stock of selected location
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",
    'contributors': "Lider IT http://www.liderit.es",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','stock_account'],

    "external_dependencies": {"python" : ["fpdf"]},
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/daily_stock_report_view.xml',
    ],
    'price': 0.00, 
    'currency': 'EUR',
}