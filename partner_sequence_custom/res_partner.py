# -*- encoding: utf-8 -*-
##############################################################################
#
#    Custom module for Odoo
#    @author Alexander Rodriguez <adrt271988@gmail.com>
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
from openerp.osv import fields,osv


class ResPartnerType(osv.osv):
    _name = 'res.partner.type'

    _columns = {
        'name':fields.char('Tipo de cliente', size=30),
        'sequence_id': fields.many2one('ir.sequence','Secuencia para numeración de clientes', help="Secuencia personalizada para clientes"),
    }


class ResPartner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'partner_type_id': fields.many2one('res.partner.type','Tipo de cliente', help="Para clasificar los clientes por tipos"),
        'ref_editable': fields.boolean('Editable'),
    }

    _defaults ={
    	'ref_editable': False,
    }
