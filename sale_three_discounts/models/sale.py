from openerp import fields, models, api
import openerp.addons.decimal_precision as dp

import logging 
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _inherit = "sale.order"

    global_discount = fields.Float(
        'Dto. Global',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )


    @api.multi
    def onchange_global_discount(self, global_discount):
        for order in self:
            for line in order.order_line:
                line.discount2 = global_discount
        return True


class res_partner(models.Model):
    _inherit = "res.partner"

    customer_discount = fields.Float(
        'Dto. de Cliente',
        digits=dp.get_precision('Discount')
    )


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    discount1 = fields.Float(
        'Discount 1 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    discount = fields.Float(
        compute='get_discount',
        store=True,
        # agregamos states vacio porque lo hereda de la definicion anterior
        states={},
    )

    
    @api.one
    @api.depends('discount1', 'discount2', 'discount3')
    def get_discount(self):
        discount_factor = 1.0
        for discount in [self.discount1, self.discount2, self.discount3]:
            discount_factor = discount_factor * ((100.0 - discount) / 100.0)
        #_logger.error('##### AIKO ###### Three discount obtiene un discount factor de %s'%discount_factor)
        #_logger.error('##### AIKO ###### Three discount ahora tiene un self discount de %s'%self.discount)
        if self.discount==False or self.discount==0:
            #_logger.error('##### AIKO ###### Three discount tiene un self.discount de cero o no existe')
            self.discount = 100.0 - (discount_factor * 100.0)
        else:
            discount_factor = discount_factor * ((100.0 - self.discount) / 100.0)
            #_logger.error('##### AIKO ###### Three discount tiene un self.discount positivo de %s'%self.discount)
            #_logger.error('##### AIKO ###### Three discount calcula un discount factor de %s'%discount_factor)
            self.discount = 100.0 - (discount_factor * 100.0)

    @api.model
    def _prepare_order_line_invoice_line(self, line):
        res = super(sale_order_line,
                    self)._prepare_order_line_invoice_line(line)
        res.update({
            'discount1': line.discount1,
            'discount2': line.discount2,
            'discount3': line.discount3
        })

        return res

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False):


        res = super(sale_order_line, self).product_id_change(
            pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag)

        result=res['value']
        #_logger.error('##### AIKO ###### Three discount los valores de res son %s'%result)

        if 'discount' in result and (result['discount']<>0):
            #_logger.error('##### AIKO ###### Three discount tiene un result discount de %s'%result['discount'])
            result['discount1'] = result['discount']

        #agregado el 8-11-16, si se ha marcado un descuento global en el cliente, se lleva a cada linea un discount2
        #_logger.error('##### AIKO ###### Three discount los valores de partner_id son %s'%partner_id)
        if partner_id:
            partner_obj = self.env['res.partner']
            for part in partner_obj.browse(partner_id):
                if part.customer_discount and part.customer_discount > 0:
                    result['discount2'] = part.customer_discount

        return res

'''
    @api.onchange('product_id', 'product_uom', 'product_uom_qty')
    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, context=None):
        res = super(sale_order_line, self).product_uom_change(cursor, user, ids,
            pricelist, product, qty=qty, uom=uom, uos=uos,name=name,partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, context=context) 
        
        result=res['value']
        #_logger.error('##### AIKO ###### Three discount los valores de res son %s'%result)
        if 'discount' in result and (result['discount']<>0):
            #_logger.error('##### AIKO ###### Three discount tiene un result discount de %s'%result['discount'])
            result['discount1'] = result['discount']

        return res
'''



