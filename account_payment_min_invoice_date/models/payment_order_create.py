# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#              (C) 2014 ACSONE SA/NV (<http://acsone.eu>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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

from openerp import api, models, fields
from datetime import datetime as dt


class payment_order_create(models.TransientModel):
    _inherit = 'payment.order.create'

    invoice_min_date = fields.Date(string='From Invoice Date')

    @api.multi
    def extend_payment_order_domain(self, payment_order, domain):
        super(payment_order_create, self).extend_payment_order_domain(
            payment_order, domain)
        # apply payment term filter
        if self.invoice_min_date:
            min_date = dt.strptime(self.invoice_min_date, "%Y-%m-%d")
            domain += [
                ('invoice.date_invoice', '>=',
                 min_date
                 )
                ]
        return True
