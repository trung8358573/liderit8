# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2013-15 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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
#

from openerp import models, api
from openerp.tools import ustr

import logging
logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0,
            uos=False, name='', partner_id=False, lang=False,
            update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False
    ):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist=pricelist, product=product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name,
            partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        if product:
            logger.error('Entro en change product_id en variant description')
            product_obj = self.env['product.product']
            if self.user_has_groups(
                    'liderit_sale_order_line_variant_description.'
                    'liderit_group_use_product_description_per_so_line'):
                lang = self.env['res.partner'].browse(partner_id).lang
                product = product_obj.with_context(lang=lang).browse(product)
                if product.attribute_value_ids:
                    logger.error('En change product_id valor de atributos %s'%product.attribute_value_ids)
                    att_tex=ustr(product.default_code) or ''
                    att_tex += " "+ product.name_template
                    for val in product.attribute_value_ids:
                        att_tex += val.attribute_id.name +' '+val.name+' '
                    logger.error('En change product_id valor de att_tex %s'%att_tex)
                    logger.error('En change product_id valor de res %s'%res)
                    if 'value' not in res:
                        res['value'] = {}
                    res['value']['name'] = att_tex
        logger.error('En change product_id valor devuelto a res %s'%res)
        return res
