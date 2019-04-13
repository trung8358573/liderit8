# -*- coding: utf-8 -*-
{
    'name': "Product Minimum Price",
    'summary': """
        Specify the minimum total price for product in sale order""",
    'description': """
This module adds the functionality to control the minimum subtotal in a sales order line. The default number is set to 0. You can change this value under the product form for individual products.
    """,
    'author': "LiderIT",
    'website': "http://www.liderit.es",
    'category': 'Sales Management',
    #Change the version every release for apps.
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': [
        'sale','sale_stock', 'product',
    ],
    # always loaded
    'data': [
        'views/product_view.xml',	
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    # only loaded in test
    'test': [
    ],
}
