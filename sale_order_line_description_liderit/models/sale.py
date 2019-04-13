# -*- coding: utf-8 -*-
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp import models, api

import logging 
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)

        # _logger.error('##### AIKO ###### En line description liderit valor de res '%res)
        if product:
            product_obj = self.env['product.product']
            if self.user_has_groups(
                    'sale_order_line_description_liderit.'
                    'group_use_product_description_per_so_line'):
                # _logger.error('##### AIKO ###### En line description identificado usuario description')
                lang = self.env['res.partner'].browse(partner_id).lang
                product = product_obj.with_context(lang=lang).browse(product)
                if product.description_sale:
                    # _logger.error('##### AIKO ###### En line description utiliza desc_sale: %s' % product.description_sale)
                    if 'value' not in res:
                        res['value'] = {}
                    res['value']['name'] = product.description_sale
                else:
                    if not flag:
                        if 'value' not in res:
                            res['value'] = {}
                        # _logger.error('##### AIKO ###### En line description utiliza name: %s' % product.name)
                        res['value']['name'] = product.name

        # _logger.error('##### AIKO ###### Product id change retorna: %s' % res)
        return res
