# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
from openerp.osv import osv, fields
from openerp import tools
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

#creamos una clase para tener en una vista los datos a exporta a excel
class invoice_leader_export(osv.osv):
    _name = "invoice.leader.export"
    #auto False para que no genere una tabla, porque es una vista
    _auto = False
    _columns = {
        'n_factura': fields.char('Numero factura', readonly=True),
        'fecha_emision': fields.date('Fecha factura', readonly=True),
        'periodo': fields.char('Periodo', readonly=True),
        'period_id': fields.float('Id Periodo', readonly=True),
        'cliente': fields.char('Cliente', readonly=True),
        'cif': fields.char('CIF', readonly=True),
        'base': fields.float('Base', readonly=True),
        'iva': fields.float('IVA', readonly=True),
        'total': fields.float('Total', readonly=True),
        'imp_divisa': fields.float('Base en divisa', readonly=True),
        'divisa':fields.char('Moneda', readonly=True),
        'forma_pago': fields.char('Forma de pago', readonly=True),
        'fecha_vto': fields.date('Fecha de vencimiento', readonly=True),
        'saldo': fields.float('Saldo', readonly=True),
        'pais': fields.char('Pais', readonly=True),
        'direccion': fields.char('Direccion', readonly=True),
        'poblacion': fields.char('Poblacion', readonly=True),
        'cod_postal': fields.char('Codigo Postal', readonly=True),
        'provincia': fields.char('Provincia', readonly=True),
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }
    _order = 'fecha_emision desc, n_factura desc'


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'invoice_leader_export')
        cr.execute("""
            CREATE OR REPLACE VIEW invoice_leader_export AS (
select 
            inv.id as id,
            inv.number as n_factura, 
            inv.date_invoice as fecha_emision,
            period.name as periodo,
            period.id as period_id, 
            partner.name as cliente, 
            partner.vat as cif, 
        CASE WHEN inv.type = 'out_refund' THEN inv.cc_amount_untaxed *-1
ELSE inv.cc_amount_untaxed
END as base,
        CASE WHEN inv.type = 'out_refund' THEN inv.cc_amount_tax *-1
ELSE inv.cc_amount_tax
END as iva,
        CASE WHEN inv.type = 'out_refund' THEN inv.cc_amount_total *-1
ELSE inv.cc_amount_total
END as total,
        CASE WHEN inv.type = 'out_refund' THEN inv.amount_untaxed *-1
ELSE inv.amount_untaxed
END as imp_divisa,
            divisa.name as divisa,
            payment.name as forma_pago, 
            inv.date_due as fecha_vto,
        CASE WHEN inv.type = 'out_refund' and inv.amount_total <> 0 and inv.cc_amount_total <> 0
THEN (inv.residual / (inv.amount_total/inv.cc_amount_total)) *-1
    WHEN inv.type = 'out_invoice' and inv.amount_total <> 0 and inv.cc_amount_total <> 0
THEN (inv.residual/ (inv.amount_total/inv.cc_amount_total))
ELSE inv.residual
END as saldo,
        CASE WHEN trans.value ='' THEN country.name
ELSE trans.value
END as pais,
            partner.street as direccion, 
            partner.city as poblacion, 
            partner.zip as cod_postal, 
            state.name as provincia
from account_invoice inv join
            res_partner partner on inv.partner_id = partner.id left join
            res_currency divisa on divisa.id = inv.currency_id left join
            res_country country on country.id = partner.country_id left join
(select res_id, value from ir_translation where name = 'res.country,name' and lang = 'es_ES') trans on trans.res_id = country.id left join
            res_country_state state on state.id = partner.state_id left join
            payment_mode payment on payment.id = inv.payment_mode_id left join
            account_period period on period.id = inv.period_id
            where partner.customer and inv.type in ('out_invoice','out_refund')
            and inv.state in ('open','paid')
            )
        """)


#creamos una clase para tener en una vista los datos de detalle de las lineas facturadas
class invoice_line_leader_export(osv.osv):
    _name = "invoice.line.leader.export"
    #auto False para que no genere una tabla, porque es una vista
    _auto = False
    _columns = {
        'n_factura': fields.char('Numero factura', readonly=True),
        'fecha_emision': fields.date('Fecha factura', readonly=True),
        'periodo': fields.char('Periodo', readonly=True),
        'period_id': fields.float('Id Periodo', readonly=True),
        'cliente': fields.char('Cliente', readonly=True),
        'codigo_producto': fields.char('Código Producto', readonly=True),
        'categoria': fields.char('Categoria', readonly=True),
        'subcategoria': fields.char('Subcategoria', readonly=True),
        'producto': fields.char('Producto', readonly=True),
        'descripcion': fields.char('Descripcion', readonly=True),
        'cantidad': fields.float('Cantidad', readonly=True),
        'precio_ud': fields.float('Precio/Ud.', readonly=True),
        'base_euros': fields.float('Base €', readonly=True),
        'base_divisa': fields.float('Base Divisa', readonly=True),
        'divisa':fields.char('Moneda', readonly=True),
        'cambio': fields.float('Tasa Cambio', readonly=True),
        'pais': fields.char('Pais', readonly=True),
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }
    _order = 'fecha_emision desc, n_factura desc'


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'invoice_line_leader_export')
        cr.execute("""
            CREATE OR REPLACE VIEW invoice_line_leader_export AS (
select 
            line.id as id,
            inv.number as n_factura, 
            inv.date_invoice as fecha_emision,
            period.name as periodo, 
            period.id as period_id,
            partner.name as cliente,
            prod.default_code as codigo_producto,
            parent_cat.name as categoria,
            cat.name as subcategoria,
            prod.name_template as producto,
            line.name as descripcion,
        CASE WHEN inv.type = 'out_refund' THEN round(line.quantity*-1,2)
ELSE round(line.quantity,2)
END as cantidad,
            round(line.price_unit,4) as precio_ud,
        CASE WHEN inv.type = 'out_refund' and inv.cc_amount_total <> 0 and inv.amount_total <> 0
THEN round((line.price_subtotal / (inv.amount_total/inv.cc_amount_total))*-1,2)
 WHEN inv.type = 'out_invoice' and inv.amount_total <> 0 and inv.cc_amount_total <> 0
THEN round((line.price_subtotal / (inv.amount_total/inv.cc_amount_total)),2)
 WHEN inv.type = 'out_refund'
THEN round((line.price_subtotal)*-1,2)
ELSE round((line.price_subtotal),2)
END as base_euros,
        CASE WHEN inv.type = 'out_refund' THEN round(line.price_subtotal *-1,2)
ELSE round(line.price_subtotal,2)
END as base_divisa,
            divisa.name as divisa,
        CASE WHEN inv.cc_amount_total <> 0 and inv.amount_total <> 0 THEN
            round((inv.amount_total/inv.cc_amount_total),4) 
        ELSE 0
        END as cambio,
        CASE WHEN trans.value ='' THEN country.name
ELSE trans.value
END as pais
        from account_invoice_line line left join
            product_product prod on prod.id = line.product_id left join
            product_template tmp on tmp.id = prod.product_tmpl_id left join
            product_category cat on cat.id = tmp.categ_id left join
            product_category parent_cat on parent_cat.id = cat.parent_id join
            account_invoice inv on line.invoice_id = inv.id join
            res_partner partner on inv.partner_id = partner.id left join
            res_currency divisa on divisa.id = inv.currency_id left join
            res_country country on country.id = partner.country_id left join
(select res_id, value from ir_translation where name = 'res.country,name' and lang = 'es_ES') trans on trans.res_id = country.id left join
            res_country_state state on state.id = partner.state_id left join
            payment_mode payment on payment.id = inv.payment_mode_id left join
            account_period period on period.id = inv.period_id
            where partner.customer and inv.type in ('out_invoice','out_refund')
            and inv.state not in ('draft','cancel')
            )
        """)


#creamos otra clase para tener en una vista los datos a exporta a excel de compras
class in_invoice_leader_export(osv.osv):
    _name = "in.invoice.leader.export"
    #auto False para que no genere una tabla, porque es una vista
    _auto = False
    _columns = {
        'n_factura': fields.char('Numero factura', readonly=True),
        'fecha_emision': fields.date('Fecha factura', readonly=True),
        'periodo': fields.char('Periodo', readonly=True),
        'period_id': fields.float('Id Periodo', readonly=True),
        'cliente': fields.char('Proveedor', readonly=True),
        'cif': fields.char('CIF', readonly=True),
        'base': fields.float('Base', readonly=True),
        'iva': fields.float('IVA', readonly=True),
        'total': fields.float('Total', readonly=True),
        'forma_pago': fields.char('Forma de pago', readonly=True),
        'fecha_vto': fields.date('Fecha de vencimiento', readonly=True),
        'saldo': fields.float('Saldo', readonly=True),
        'pais': fields.char('Pais', readonly=True),
        'direccion': fields.char('Direccion', readonly=True),
        'poblacion': fields.char('Poblacion', readonly=True),
        'cod_postal': fields.char('Codigo Postal', readonly=True),
        'provincia': fields.char('Provincia', readonly=True),
        'due_date_from': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Desde Fecha'
        ),
        'due_date_to': fields.function(
            lambda *a,**k:{}, method=True, type='date', string='Hasta Fecha'
        ),
    }
    _order = 'fecha_emision desc, n_factura desc'


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'in_invoice_leader_export')
        cr.execute("""
            CREATE OR REPLACE VIEW in_invoice_leader_export AS (
select 
            inv.id as id,
            inv.number as n_factura, 
            inv.date_invoice as fecha_emision,
            period.name as periodo,
            period.id as period_id, 
            partner.name as cliente, 
            partner.vat as cif,
CASE WHEN inv.type = 'in_refund' THEN inv.amount_untaxed *-1
ELSE inv.amount_untaxed
END as base, 
CASE WHEN inv.type = 'in_refund' THEN inv.amount_tax *-1
ELSE inv.amount_tax
END as iva,
CASE WHEN inv.type = 'in_refund' THEN inv.amount_total *-1
ELSE inv.amount_total
END as total,
            payment.name as forma_pago, 
            inv.date_due as fecha_vto, 
            inv.residual as saldo, 
CASE WHEN trans.value ='' THEN country.name
ELSE trans.value
END as pais,
            partner.street as direccion, 
            partner.city as poblacion, 
            partner.zip as cod_postal, 
            state.name as provincia
from account_invoice inv join
            res_partner partner on inv.partner_id = partner.id left join
            res_country country on country.id = partner.country_id left join
(select res_id, value from ir_translation where name = 'res.country,name' and lang = 'es_ES') trans on trans.res_id = country.id left join
            res_country_state state on state.id = partner.state_id left join
            payment_mode payment on payment.id = inv.payment_mode_id left join
            account_period period on period.id = inv.period_id
            where partner.customer and inv.type in ('in_invoice','in_refund')
            )
        """)