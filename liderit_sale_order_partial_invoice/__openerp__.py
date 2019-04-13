# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Liderit Sale Order Partial Invoice",
    'description': """Partial invoicing of sale orders""",
    'version': '8.0',
    'category': 'Sale',
    'author': 'Trustcode - LiderIT',
    'license': 'AGPL-3',
    'website': 'http://www.liderit.es',
    'contributors': ['Mackilem Van der Laan Soares <mack.vdl@gmail.com>',
                     'Danimar Ribeiro <danimaribeiro@gmail.com>',
                     'Alessandro Fernandes Martini \
<alessandrofmartini@gmail.com>'
                     ],
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_partial_invoice.xml',
    ],
    'application': True,
}
