# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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

{
    'name': 'SyG Labels',
    'version': '0.1',
    'category': 'Other',
    'summary': 'Print Name Tags for Colegios',
    'description': """Print Name Tags (labels) for colegios using gLabels-program.
           If you want to change the layout of the document, you can do that with
        the template saved on the report record. """,
    'author': 'LiderIT',
    'website': 'http://www.liderit.es',
    'depends': ['syg_edu','report_glabels'],
    'data': ['syg_colegios_report.xml',],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
