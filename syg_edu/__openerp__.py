# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
 
# noinspection PyStatementEffect
{
    "name" : "syg_edu",
    
    "author" : "LiderIT",
    "website" : "www.liderit.es",
    "category" : "Other",
    "licence" : "AGPL-3",
    "description": """
syg_edu
====================================
Personalizacion para SyG Educacion
                    """,
    "depends" : [
        'base', 
        'base_location',
        'liderit_ccaa',
        'account',
        'account_payment_partner',
        'liderit_partner_firstname',
        'partner_contact_department',
        'event',
        ],
    "data" : [
        "views/res_partner_view.xml",
        "views/res_colegio_view.xml",
        "views/res_profesor_view.xml",
        "views/account_voucher_view.xml",
        "data/partner_edad_cron.xml",
        ],
    "demo" : [],
    "installable": True,
    "auto_install": False,
    "application": False,
}