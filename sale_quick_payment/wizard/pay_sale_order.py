# -*- coding: utf-8 -*-
##############################################################################
#
#    sale_quick_payment for OpenERP
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.osv import osv

import logging 
_logger = logging.getLogger(__name__)

class PaySaleOrder(models.TransientModel):
    _name = 'pay.sale.order'
    _description = 'Wizard to generate a payment from the sale order'

    @api.model
    def _default_journal_id(self):
        context = self.env.context
        if not context.get('active_id'):
            return False
        order = self.env['sale.order'].browse(context['active_id'])
        if order.payment_method_id:
            return order.payment_method_id.journal_id.id
        return False

    journal_id = fields.Many2one('account.journal', 'Journal',
                                 default=_default_journal_id)

    @api.model
    def _default_amount(self):
        context = self.env.context
        if not context.get('active_id'):
            return False
        return self.env['sale.order'].browse(context['active_id']).residual

    amount = fields.Float('Amount', digits=dp.get_precision('Sale Price'),
                          default=_default_amount)

    date = fields.Datetime('Payment Date', default=fields.Datetime.now)

    description = fields.Char('Description', size=64)

    @api.multi
    def pay_sale_order(self):
        """ Pay the sale order """
        self.ensure_one()
        order = self.env['sale.order'].browse(self.env.context['active_id'])

        #23-3-16 antes de registrar el pago asegurarse que no esta facturado
        #buscamos las sale.order.lines relacionadas
        sale_ord_lines = self.env['sale.order.line'].search ([('order_id','=',order.id)])
        #y comprobamos si alguna linea esta en sale_order_line_invoice_rel
        #_logger.error('##### AIKO ###### Valor de order lines en pay_sale_orderid: %s' % sale_ord_lines)
        for s in sale_ord_lines:
            #_logger.error('##### AIKO ###### Buscando en pay_sale_orderid las lineas facturadas con name: %s' % s.name)

            if (s.invoice_lines):
                raise osv.except_osv(('Error!'),('No se puede registrar el pago de un pedido ya facturado! Registre el pago en facturas.'))


        if (self.amount<0):
            _logger.error('##### AIKO ###### En pay_sale_order encuentro importe negativo: %s' % self.amount)
            amount = self.amount*(-1)
            order.add_return(self.journal_id.id,
                              amount,
                              date=self.date,
                              description=self.description)
        else:
            order.add_payment(self.journal_id.id,
                              self.amount,
                              date=self.date,
                              description=self.description)

        return True

    @api.multi
    def pay_sale_order_and_confirm(self):
        """ Pay the sale order """
        self.ensure_one()
        self.pay_sale_order()
        order = self.env['sale.order'].browse(self.env.context['active_id'])
        return order.action_button_confirm()

    @api.multi
    def pay_sale_orderid(self, sale_order, journal_id):
        """ Pay the sale order """
        self.ensure_one()
        order = self.env['sale.order'].browse(sale_order)
        #23-3-16 antes de registrar el pago asegurarse que no esta facturado
        #buscamos las sale.order.lines relacionadas
        sale_ord_lines = self.env['sale.order.line'].search ([('order_id','=',order.id)])
        #y comprobamos si alguna linea esta en sale_order_line_invoice_rel
        #_logger.error('##### AIKO ###### Valor de order lines en pay_sale_orderid: %s' % sale_ord_lines)
        for s in sale_ord_lines:
            #_logger.error('##### AIKO ###### Buscando en pay_sale_orderid las lineas facturadas con name: %s' % s.name)
            if (s.invoice_lines):
                raise osv.except_osv(('Error!'),('No se puede registrar el pago de un pedido ya facturado! Registre el pago en facturas.'))

        if (self.amount<0):
            _logger.error('##### AIKO ###### En pay_sale_orderid encuentro importe negativo: %s' % self.amount)
            amount = self.amount*(-1)
            order.add_return(journal_id,
                          amount,
                          date=self.date,
                          description=self.description)
        else:
            order.add_payment(journal_id,
                          self.amount,
                          date=self.date,
                          description=self.description)
        return True
