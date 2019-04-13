# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Gestion-Ressources
#    (<http://www.gestion-ressources.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Impor Export to TERCAP',
    'version': '1.0',
    "category": 'Accounting & Finance',
    'description': """
Importa Exporta archivos de intercambio entre aplicaciones 
     de TERCAP autoventa y los sistemas ERP
===========================================================

    """,
    "author": "LiderIT",
    'maintainer': 'LiderIT',
    'website': 'http://www.liderit.es',
    "license": "AGPL-3",
    'images': [],
    #si el cliente gestiona el dto por pronto pago cambiar a esta linea comentada
    #'depends': ['account','sale', 'sales_team','sale_quick_payment','sale_early_payment'],
    #14-12-16 nuevo depends 'partner_supplier_ref (de LiderIT) para poder enviar informacion en direccion del codigo proveedor
    'depends': [
    'account',
    'account_payment',
    'account_payment_sale', 
    'account_invoice_sale_link',
    'product','sale', 'sale_journal',
    'sale_margin_uom',
    'sales_team',
    'sale_stock',
    'sale_quick_payment',
    'sale_three_discounts',
    'partner_supplier_ref'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/tercap_security.xml',
        'views/exporta_view.xml',
        'views/importa_view.xml',
        'views/res_partner_view.xml',
        'views/product_view.xml',
        'views/account_tax_view.xml',
        'views/account_fiscal_position_view.xml',
        'views/account_payment_term_view.xml',
        'views/product_uom_view.xml',
        'views/rutas_view.xml',
        'views/sale_order.xml',
        'views/confg_export_view.xml',
        'views/confg_import_view.xml',
        'views/crm_sales_view.xml',
        'views/menu.xml'
#         'wizard/exporta_view.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
