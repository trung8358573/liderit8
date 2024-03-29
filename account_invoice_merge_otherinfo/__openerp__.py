# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_merge_payment,
#     an Odoo module.
#
#     account_invoice_merge_payment is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_merge_payment is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_merge_payment.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "account_invoice_merge_otherinfo",
    'summary': """
        Use invoice merge regarding fields on Account Payment Partner, Payment Term, User and Section""",
    'author': "Odoo Community Association (OCA)",
    'website': "www.liderit.es",
    'category': 'Invoicing & Payments',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_merge',
        'account_payment_partner',
    ],
    'auto_install': False
}
