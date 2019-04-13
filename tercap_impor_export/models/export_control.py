# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Hugo Santos (<http://factorlibre.com>).
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

# from osv import osv, fields
from openerp.osv import osv, fields
from openerp import api
import openerp.addons.decimal_precision as dp
import xmlrpclib
import logging
import exporta
_logger = logging.getLogger(__name__)

class export_control(osv.osv):
    _name = "export.control"
    _description = "Parametros de control de exportacion"
    _columns = {
        'name': fields.char('Nombre de la importacion'),
        'clientes_71': fields.boolean('Clientes?'),
        'direcciones_72': fields.boolean('Direcciones?'),
        'productos_73': fields.boolean('Productos?'),
        'envases_74': fields.boolean('Envases?'),
        'iva_75': fields.boolean('Iva?'),
        'tarifas_76': fields.boolean('Tarifas?'),
        'formas_pago_77': fields.boolean('Formas de Pago?'),
        'cobros_pendientes_78': fields.boolean('Cobros Pendientes?'),
        'descuentos_cliente_producto_79': fields.boolean('Descuentos Clientes Productos?'),
        'promociones_710': fields.boolean('Promociones en Precios?'),
        'obsequios_711': fields.boolean('Obsequios por cliente y producto?'),
        'promociones_producto_712': fields.boolean('Promociones por producto?'),
        'obsequios_producto_713': fields.boolean('Obsequios por producto?'),
        'cabeceras_pedido_reparto_714': fields.boolean('Cabeceras Pedido Reparto?'),
        'lineas_pedido_reparto_715': fields.boolean('Lineas Pedido Reparto?'),
        'rutero_716': fields.boolean('Rutero?'),
        'motivos_visita_negativa_717': fields.boolean('Motivos Visita Negativa?'),
        'material_cliente_718': fields.boolean('Material - Cliente?'),
        'cliente_proveedor_719': fields.boolean('Cliente Proveedor?'),
        'proveedor_720': fields.boolean('Proveedor?'),
        'rutas_721': fields.boolean('Rutas?'),
        'vendedores_722': fields.boolean('Vendedores?'),
        'productos_exclusivos_723': fields.boolean('Productos Exclusivos?'),
        'cabeceras_carga_mercancia_724': fields.boolean('Cabeceras Cargas Mercancias?'),
        'lineas_carga_mercancia_725': fields.boolean('Lineas Cargas Mercancias?'),
        'lineas_stock_726': fields.boolean('Stock real?'),
        'lineas_stock_726V': fields.boolean('Stock virtual?'),
        'lineas_stock_726L': fields.boolean('Lotes de Productos'),
    }

#cambio de criterio del 24/6/16: ponemos a false el valor del rutero y como Administrador
#lo marcaremos a true en el formulario como valor por defecto para todos los usuarios
#asi podemos gestionar clientes que no quieren y que si usan el rutero en las exportaciones
#lo cambio tambien en otros valores que puede ser el mismo caso: stock.
    _defaults = {
        'clientes_71': True,
        'direcciones_72': True,
        'productos_73': True,
        'envases_74': False,  
        'iva_75': True,
        'tarifas_76': False,
        'formas_pago_77': True,
        'cobros_pendientes_78': True,
        'descuentos_cliente_producto_79': False,
        'promociones_710': False,
        'obsequios_711': False,
        'promociones_producto_712': False,
        'obsequios_producto_713': False,
        'cabeceras_pedido_reparto_714': False,
        'lineas_pedido_reparto_715': False,
        'rutero_716': False,
        'motivos_visita_negativa_717': False,
        'material_cliente_718': False,
        'cliente_proveedor_719': False,
        'proveedor_720': True,
        'rutas_721': True,
        'vendedores_722':  True,
        'productos_exclusivos_723':  False,
        'cabeceras_carga_mercancia_724':  False,
        'lineas_carga_mercancia_725': False,
        'lineas_stock_726': False,
        'lineas_stock_726V': False,
        'lineas_stock_726L': False,
    }


    def act_cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
 
    def cron_exportar(self, cr, uid, ids, context):
        return
    def srcen_exportar(self, cr, uid, ids, context=None):
    
        control_obj = self.pool.get('export.control') 
        obj_actividad = self.pool.get('export.control').browse(cr, uid, ids)

        #24/06/16 controlamos que no se marquen a la vez stock real y virtual
        if (obj_actividad.lineas_stock_726V == True) and (obj_actividad.lineas_stock_726 == True):
            raise osv.except_osv(('NO se puede generar a la vez el fichero de stock real y virtual. Marque una sola de las opciones.'),
                    ('Seleccione un solo tipo de stock')) 
        if (obj_actividad.clientes_71 == True):
            exporta._create_report71(self, cr, uid, ids, context=None)

        if (obj_actividad.direcciones_72 == True):
            exporta._create_report72(self, cr, uid, ids, context=None)
            
        if (obj_actividad.productos_73 == True):
            exporta._create_report73(self, cr, uid, ids, context=None)

        if (obj_actividad.envases_74 == True):
            exporta._create_report74(self, cr, uid, ids, context=None)

        if (obj_actividad.iva_75 == True):
            exporta._create_report75(self, cr, uid, ids, context=None)

        if (obj_actividad.tarifas_76 == True):
            exporta._create_report76(self, cr, uid, ids, context=None)
        
        if (obj_actividad.formas_pago_77 == True):
            exporta._create_report77(self, cr, uid, ids, context=None)
        
        if (obj_actividad.cobros_pendientes_78 == True):
            exporta._create_report78(self, cr, uid, ids, context=None)

        if (obj_actividad.descuentos_cliente_producto_79 == True):
            exporta._create_report79(self, cr, uid, ids, context=None)

        if (obj_actividad.promociones_710 == True):
            exporta._create_report710(self, cr, uid, ids, context=None)

        if (obj_actividad.obsequios_711 == True):
            exporta._create_report711(self, cr, uid, ids, context=None)

        if (obj_actividad.promociones_producto_712 == True):
            exporta._create_report712(self, cr, uid, ids, context=None)

        if (obj_actividad.obsequios_producto_713 == True):
            exporta._create_report713(self, cr, uid, ids, context=None)

        if (obj_actividad.cabeceras_pedido_reparto_714 == True):
            exporta._create_report714(self, cr, uid, ids, context=None)
        
        if (obj_actividad.lineas_pedido_reparto_715 == True):
            exporta._create_report715(self, cr, uid, ids, context=None)
        
        if (obj_actividad.rutero_716 == True):
            exporta._create_report716(self, cr, uid, ids, context=None)
        
        if (obj_actividad.motivos_visita_negativa_717 == True):
            exporta._create_report717(self, cr, uid, ids, context=None)
            
        if (obj_actividad.material_cliente_718 == True):
            exporta._create_report718(self, cr, uid, ids, context=None)
    
        if (obj_actividad.cliente_proveedor_719 == True):
            exporta._create_report719(self, cr, uid, ids, context=None)
    
        if (obj_actividad.proveedor_720 == True):
            exporta._create_report720(self, cr, uid, ids, context=None)
    
        if (obj_actividad.rutas_721 == True):
            exporta._create_report721(self, cr, uid, ids, context=None)
    
        if (obj_actividad.vendedores_722 == True):
            exporta._create_report722(self, cr, uid, ids, context=None)
    
        if (obj_actividad.cabeceras_carga_mercancia_724 == True):
            exporta._create_report724(self, cr, uid, ids, context=None)
    
        if (obj_actividad.lineas_carga_mercancia_725 == True):
            exporta._create_report725(self, cr, uid, ids, context=None)

        if (obj_actividad.lineas_stock_726 == True) and (obj_actividad.lineas_stock_726V == False) and (obj_actividad.lineas_stock_726L == False):
            exporta._create_report726(self, cr, uid, ids, context=None)

        if (obj_actividad.lineas_stock_726V == True) and (obj_actividad.lineas_stock_726 == False) and (obj_actividad.lineas_stock_726L == False):
            exporta._create_report726V(self, cr, uid, ids, context=None)

        if (obj_actividad.lineas_stock_726L == True) and (obj_actividad.lineas_stock_726V == False) and (obj_actividad.lineas_stock_726 == False):
            exporta._create_report726L(self, cr, uid, ids, context=None)

        if (obj_actividad.productos_exclusivos_723 == True):
            exporta._create_report723(self, cr, uid, ids, context=None)
            
        raise osv.except_osv(('Ficheros Exportados en formato Texto'),
                    ('Directorio  ERP')) 
        
        
        return
        
    def exportar(self, cr, uid, ids, context=None):
        par_obj = self.pool.get('expo.control')
        search_condition = [('active', '=', True)]
        ex = par_obj.search(cr, uid, search_condition )
#        _logger.error('##### AIKO ###### El string recibido es: ==>' + str(ex) + "<==")
        for e_id in ex:
            e=par_obj.browse(cr, uid, e_id ,context=context)
#            _logger.error('##### AIKO ###### El string recibido es: ==>' + str(e) + "<==")
#             exporta.create_report71(self, cr, uid, ids, context=None)
        return
class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
#         'tercap_tipo_iva': fields.selection([  
#             ('N', 'Iva sin recargo'),
#             ('E', 'Exento de Iva'),                            
#             ('R', 'Iva con recargo')], 'Tipo de Iva:'),    
#         'tercap_cod_forma_pago': fields.selection([  
#             ('0', 'Cliente de credito'),                              
#             ('1', 'Cliente de contado')], 'Codigo forma Pago:'),
        'tercap_codexclusividad':fields.char('Codigo Exclusividad', size=4), 
        'tercap_descuentogeneral': fields.float('Descuento General %'),
        'tercap_descuentopp': fields.float('Descuento Pronto Pago %'),
        'tercap_solicitarnumpedido': fields.selection([  
            ('N', 'No'),
            ('S', 'Si')], 'Solicitar el numero de pedido al cliente al hacer albaran:'),    
        'tercap_albarancontado': fields.selection([  
            ('N', 'No'),
            ('S', 'Si')], 'Indica si al cliente se le cobran los albaranes:'),    
        'tercap_albaranvalorado': fields.selection([  
            ('N', 'No'),
            ('S', 'Si')], 'Indica si los albaranes se imprimen valorados:'),    
        'tercap_tipoventa': fields.selection([  
            ('0', 'Venta Nomal'),
            ('4', 'Venta indirecta')], 'Indica si albaran emitido por otro proveedor:'),    
                
        'tercap_permitirdevoluciones': fields.selection([  
            ('S', 'Si'),
            ('N', 'No')], 'Indica si se permite retirar mercancia del cliente:'),
                          
        'tercap_imprimircopiaalb': fields.selection([  
            ('S', 'Si'),
            ('N', 'No')], 'Indica si se imprime una copia del documento de venta:'), 
#        'tercap_vendedor': fields.boolean('Vendedor'), 
        'tercap_ruta_id': fields.many2one('ruta', 'Ruta'),
        #NOVEDAD 28-6-16 GESTIONA LA RUTA DE REPARTO
        'tercap_reparto_id': fields.many2one('ruta', 'Ruta de reparto'),
        'orden_visita': fields.float('Orden de visita en la ruta y día', digits=(5,0)),

            }  
    _defaults = {
#         'tercap_cod_forma_pago': '1',
#         'tercap_tipo_iva': 'R',
        'tercap_descuentogeneral': 0,  
        'tercap_descuentopp': 0,
        'tercap_solicitarnumpedido': 'N',
        'tercap_albarancontado':'S',
        'tercap_albaranvalorado': 'S',
        'tercap_tipoventa': '0',
        'tercap_permitirdevoluciones': 'S',
        'tercap_imprimircopiaalb': 'S',
        'tercap_vendedor': False,
        'orden_visita': 0,
            } 
    
class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        'tercap_product': fields.boolean('Producto a incluir en conexion TERCAP?'),
        'tercap_unidadescaja': fields.float('Cantidad de unidades por caja'), 
        'tercap_loterequerido' : fields.selection([  
            ('N', 'No'),
            ('S', 'Si'),
            ], 'Indica si se requiere introducir o seleccionar un lote al vender o cargar el producto:'),
        'tercap_codenvase_id': fields.many2one('codi.envase', 'Codigo envase'),     
        'tercap_espesovariable' : fields.selection([  
            ('N', 'No'),
            ('S', 'Si'),
             ], 'Indica si es un producto de peso variable y requiere introducir peso al vender:'),
        'tercap_pesoestandar': fields.float('Peso estandar '),
        'tercap_desviacionpeso': fields.float('Desviacion peso '),     
    }
    _defaults = {
        'tercap_product': True,
        'tercap_unidadescaja': 1,  
        'tercap_loterequerido' : 'N', 
        'tercap_codenvase': 0,
        'tercap_espesovariable' :'N',
        'tercap_estandar': 0,
        'tercap_desviacionpeso': 0,
     }
class account_tax(osv.osv):
    _inherit = 'account.tax'
    _columns = {   
        'tercap_codiva': fields.selection([  
            ('0', 'No se trata en Tercap'),
            ('1', 'Normal'),
            ('2', 'Reducido'),
            ('3', 'Super-Reducido'),
            ('4', 'Exento'),
            ('5', 'Porcentaje Recargo Normal'),
            ('6', 'Porcentaje Recargo Reducido'),
            ('7', 'Porcentaje Recargo Superreducido'),
            ], 'Codigo de iva asignado para interfase TERCAP:'),    
        }    
    _defaults = {
        'tercap_codiva': '0'    
     }
    
class codigo_envase(osv.osv):
    _name = "codi.envase"
    _description = "tabla de envases "
    _columns = {        
        'tercap_products_ids': fields.one2many('product.template', 'tercap_codenvase_id', string='Envase'),
        'tercap_codenvase': fields.integer('Codigo de envase'),          
        'tercap_name':fields.char('Descripcion', size=50, required=True),     
        'tercap_importe':  fields.float('Importe de envase'), 
        'tercap_obsoleto': fields.boolean('Envase obsoleto en conexion TERCAP?'),     
                
      } 
    _defaults = {
        'tercap_obsoleto': False    
     }
    _sql_constraints = [('codigo_envase_tercap_codeenvase_unique','unique(tercap_codenvase)', 'Codigo envase ya existe')]
    _sql_constraints = [('codigo_envase_tercap_name_unique','unique(tercap_name)', 'Descripcion envase ya existe')]
  
class account_payment_term(osv.osv):
    _inherit = 'account.payment.term'
    _columns = { 
        'tercap_cod_forma_pago': fields.selection([  
            ('0', 'Credito'),                              
            ('1', 'Contado')], 'Codigo forma Pago TERCAP:'),
#         'tercap_creditocontado': fields.selection([  
#             ('N', 'Contado'),
#             ('S', 'Credito'),
#             ], 'Codigo para interfase TERCAP:'),    
        }    
#    _defaults = {
#        'tercap_cod_forma_pago': '1',
         #'tercap_creditocontado': 'N'    
#     }  

class payment_mode(osv.osv):
    _inherit = 'payment.mode'
    _columns = { 
        'tercap_cod_modo_pago': fields.selection([  
            ('0', 'Credito'),                              
            ('1', 'Contado')], 'Codigo forma Pago TERCAP:'), 
        'tercap_comunicate': fields.boolean('Forma de Pago para Tercap'),     
        }   

    _defaults = {
        'tercap_comunicate': True
    } 


class product_uom(osv.osv):
     _inherit = 'product.uom'
     _columns = {   
        'tercap_unit': fields.selection([  
            ('U', 'U   Unidad'),
            ('KG', 'KG   Kilo'),
            ('C', 'C   Caja'),
            ], 'Codigo unidad para interfase TERCAP:'),    
        } 
     #Manuel: 12-2-16 paro este valor por defecto, porque entonces
     #la importacion no distingue que valor es la Unidad (U)   
     #_defaults = {
     #   'tercap_unit': 'U'    
     #}  
    

class accountfiscalposition(osv.osv):
    _inherit =  'account.fiscal.position'
    _columns = {
        'tercap_tipo_iva': fields.selection([  
            ('N', 'Iva sin recargo'),
            ('E', 'Exento de Iva'),                            
            ('R', 'Iva con recargo')], 'Tipo de Iva en sistema Tercap:'),     
        }  
    #Manuel: 12-2-16 paro este valor por defecto, porque entonces
    #para la importacion todos los tipos de iva son con recargo   
    #_defaults = {
    #    'tercap_tipo_iva': 'R',
    # }  
    
#======= Ampliado por Manuel el 11-2-16 para ampliar crm.case.section ======
# Esta ampliacion de clase para poder gestionar el campo permitircambioprecio de Tercap
class crm_case_section(osv.osv):
    _inherit =  'crm.case.section'
    _columns = {
        'tercap_permitircambioprecio': fields.boolean('Permitido cambiar precios'),     
        }    
    _defaults = {
        'tercap_permitircambioprecio': True,
     }


class sale_order(osv.osv):
    _inherit =  'sale.order'
    _columns = {
        'city':fields.related('partner_id','city',type='char',readonly=True,string='Ciudad'), 
        'ruta_id':fields.related('partner_id','tercap_ruta_id',type='many2one',relation='ruta',readonly=True,string='Ruta',store=True),    
        'reparto_id': fields.many2one('ruta', 'Ruta de reparto'),
        } 

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if context==None:
            context={ }     

        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=None)
        res['value'].update({'reparto_id': False})  

        if part:
            partner = self.pool.get('res.partner').browse(cr, uid, part, context)
            if (partner.tercap_ruta_id):
                if (partner.tercap_reparto_id):
                    reparto = partner.tercap_reparto_id.id
                else:
                    reparto = partner.tercap_ruta_id.id
                res['value'].update({'reparto_id': reparto})
        return res


class stock_picking(osv.osv):
    _inherit =  'stock.picking'
    _columns = {
        'ruta_id':fields.related('partner_id','tercap_ruta_id',type='many2one',relation='ruta',readonly=True,string='Ruta',store=True),
        'dia_descanso':fields.related('partner_id','dia_descanso',type='char',readonly=True,string='Dia Descanso',store=True),    
        'section_id': fields.many2one('crm.case.section', 'Equipo de ventas', readonly=True),
        'reparto_id': fields.many2one('ruta', 'Ruta de reparto', readonly=True),
        }

#en la clase stock_move se registra la relacion del stock_picking con la ruta de reparto (igual que en sale_journal)
class stock_move(osv.osv):
    _inherit = "stock.move"

    def action_confirm(self, cr, uid, ids, context=None):
        """
            Pass the reparto ruta the picking from the sales order
        (Should also work in case of Phantom BoMs when on explosion the original move is deleted, similar to carrier_id on delivery)
        """

        res = super(stock_move, self).action_confirm(cr, uid, ids, context=context)
        #para las rutas de reparto
        procs_to_check = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.reparto_id:
                procs_to_check += [move.procurement_id]
        
        pick_obj = self.pool.get("stock.picking")
        for procR in procs_to_check:
            pickings = list(set([x.picking_id.id for x in procR.move_ids if x.picking_id and not x.picking_id.reparto_id]))
            if pickings:
                pick_obj.write(cr, uid, pickings, {'reparto_id': procR.sale_line_id.order_id.reparto_id.id}, context=context)

        #para el equipo de ventas
        procs_to_check = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.section_id:
                procs_to_check += [move.procurement_id]
        
        for procQ in procs_to_check:
            pickings = list(set([x.picking_id.id for x in procQ.move_ids if x.picking_id and not x.picking_id.section_id]))
            if pickings:
                pick_obj.write(cr, uid, pickings, {'section_id': procQ.sale_line_id.order_id.section_id.id}, context=context)

        return res
                       
        