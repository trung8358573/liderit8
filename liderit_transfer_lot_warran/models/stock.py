# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from dateutil.relativedelta import relativedelta

import logging
logger = logging.getLogger(__name__)


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"


    @api.model
    def create(self, vals):
        # logger.error('En prod_lot on create valor context %s'%self.env.context)
        # logger.error('En prod_lot on create vals recibidos %s'%vals)
        if vals.get('product_id'):
            
            product = self.env["product.product"].browse(vals["product_id"])
            create_date = (
                'create_date' in vals and
                vals['create_date'] or fields.Datetime.from_string(
                    fields.Datetime.now()))
            
            

            if 'sup_warrant' not in self.env.context:
                warrant_limit = (
                    product.warranty and
                    (create_date +
                     relativedelta(months=int(product.warranty))))
            else:
                warrant_limit = (
                    create_date +
                    relativedelta(months=self.env.context['sup_warrant']))


        if 'product_id' in self.env.context:       
            product = self.env["product.product"].browse(self.env.context["product_id"])
            create_date = (
                'create_date' in vals and
                vals['create_date'] or fields.Datetime.from_string(
                    fields.Datetime.now()))

            if product.seller_ids:
                for sup in product.seller_ids:
                    if sup.warrant_months > 0:
                         warrant_limit = (
                    create_date +
                    relativedelta(months=sup.warrant_months))
                         break

        if warrant_limit:
                    vals.update({'warrant_limit': warrant_limit})

        return super(StockProductionLot, self).create(vals)


