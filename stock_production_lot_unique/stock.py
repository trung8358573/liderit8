# -*- encoding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError

class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    @api.one
    @api.constrains('name', 'product_id')
    def check_lot_unique(self):
        for lot in self:

            if (lot.name and lot.product_id):
                domain = [
                    ('name', 'ilike', lot.name),
                    ('product_id', '=', lot.product_id.id),
                ]
                other = self.search(domain)

                if len (other) > 1:
                    raise ValidationError(
                        _("Lot number must be unique per company and product. This product has yet this lot number register."))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
