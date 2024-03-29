# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sales commissions for LiderIT',
    'version': '8.0.2.3.1',
    'author': 'LiderIT',
    "category": "Sales Management",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        'product',
        'sale'
    ],
    'contributors': [
        "Pexego",
        "Davide Corio <davide.corio@domsense.com>",
        "Joao Alfredo Gama Batista <joao.gama@savoirfairelinux.com>",
        "Sandy Carter <sandy.carter@savoirfairelinux.com>",
        "Giorgio Borelli <giorgio.borelli@abstract.it>",
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Oihane Crucelaegui <oihanecruce@gmail.com>",
        "Iván Todorovich <ivan.todorovich@gmail.com",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
        "views/sale_commission_view.xml",
        "views/sale_order_view.xml",
        "views/account_invoice_view.xml",
        "views/settlement_view.xml",
        "wizard/wizard_settle.xml",
        "wizard/wizard_invoice.xml",
        "views/report_settlement.xml",
        # "report/cc_commission_report.xml"
    ],
    # "demo": [
    #     'demo/sale_agent_demo.xml',
    # ],
    # 'test': [
    #     'test/sale_commission_demo.yml',
    # ],
    "installable": True
}
