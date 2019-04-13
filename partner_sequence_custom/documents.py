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

from openerp import models, api
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def _get_next_ref(self, seq_id):
        valor_seq = self.env['ir.sequence'].next_by_id(seq_id)
        return valor_seq
        
    @api.model
    def create(self, vals):
        if vals.get('partner_type_id'):
            _logger.info("Creating partner con type  %d", vals.get('partner_type_id'))
            seq_id = self.env['res.partner.type'].browse(vals.get('partner_type_id'))
            _logger.info("Creating partner con sequence  %d", seq_id.sequence_id.id)
            # nueva_ref = self._get_next_ref(seq_id.sequence_id.id)
            nueva_ref = self._get_next_ref(seq_id.sequence_id)
            vals['ref'] = nueva_ref
            #_logger.info("Creating partner con ref  %d", nueva_ref)
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('partner_type_id'):
            if self.ref == False:
                seq_id = self.env['res.partner.type'].browse(vals.get('partner_type_id'))
                # vals['ref'] = self._get_next_ref(seq_id.sequence_id.id)
                vals['ref'] = self._get_next_ref(seq_id.sequence_id)
                vals['ref_editable'] = False
        if vals.get('ref'):
            vals['ref_editable'] = False
        return super(ResPartner, self).write(vals)

    @api.one
    def button_edit_ref(self):
        if self.ref_editable:
            self.ref_editable = False
        else:
            self.ref_editable = True

'''

    @api.onchange('partner_type_id')
    def _change_partner_type(self):
        for partner in self:
            if partner.partner_type_id:
                # seq_id = self.env['res.partner.type'].browse(partner.partner_type_id.id)
                self.ref = self._get_next_ref(partner.partner_type_id.sequence_id.id)



    def create(self, cr, uid, values, context = None):
        sequence_obj = self.pool.get('ir.sequence')
        if values['partner_type_id']:
            partner_type = self.pool.get('res.partner.type').browse(cr, uid, values['partner_type_id'])
            if partner_type_id.sequence_id:
                values['ref'] = self.pool.get('ir.sequence').next_by_id(cr, uid, partner_type_id.sequence_id.id, context = context)

        return super(ResPartner, self).create(cr, uid, values, context = context)
'''
