# -*- encoding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2013 Ld solutions
#    (<http://www.ldsolutions.es>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
# import time
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
from . import voucher

import logging 
_logger = logging.getLogger(__name__)

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'payment_reconcile': fields.boolean('Pagos de Pedidos Conciliados'),
    }

    _defaults = {
        'payment_reconcile': False,
    }


    def invoice_validate(self, cr, uid, ids, context=None):
        result = super (account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        
        salesinv_obj = self.pool.get('invoice.sale.rel')
        sale_obj = self.pool.get('sale.order')
        move_obj = self.pool.get('account.move.line')
        voucher_obj = self.pool.get('account.voucher')

        for inv_id in ids:
            if (self.browse(cr, uid, inv_id).payment_reconcile):
                continue
            search_condition=[('id_invoice','=',inv_id )]
            sales_invs = salesinv_obj.search(cr,uid,search_condition)
            for s in sales_invs:
                sale_pays = sale_obj.browse(cr,uid,s).payment_ids
                if len(sale_pays)>0:
                    for p in sale_pays:
                        for c in p:
                            move_id = move_obj.browse(cr,uid,c.id)
                            if (move_id.debit==0):
                                new_voucher = voucher.crea_voucher (self, cr, uid, inv_id, move_id, context=None)
                                voucher_obj.write(cr, uid, [new_voucher], {'state':'draft'}, context=context)
                                voucher.crea_lineas_voucher(self, cr, uid, inv_id, move_id, new_voucher, context=None)
                                voucher_brw = voucher_obj.browse(cr,uid,new_voucher)
                                #_logger.error('##### AIKO ###### Import_control en cobro factura valor del voucher a conciliar %s'%voucher_brw)
                                voucher_obj.button_proforma_voucher(cr, uid, [new_voucher], context=context)
                                #marcamos la factura para no volver a asociar pagos de sus pedidos
                                self.write(cr, uid, inv_id,{'payment_reconcile':'True'},context=context)

        return result

