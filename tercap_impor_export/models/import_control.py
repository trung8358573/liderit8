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
from openerp.osv import osv, fields
from openerp import tools
from datetime import datetime
import importa
import voucher
import os, sys
import logging
_logger = logging.getLogger(__name__)

class import_control(osv.osv):
    _name = "import.control"
    _description = "Parametros de control de importacion"
    _columns = {
        'cabecera_81': fields.boolean('Cabecera documentos'),
        'lineas_82': fields.boolean('Lineas documentos'),
        'cobros_83': fields.boolean('Cobros realizados'),
        'cliente_nuevo_84': fields.boolean('Clientes nuevos'),
         }
    _defaults = {
        'cabecera_81': True,
        'lineas_82': True,
        'cobros_83': True,
        'cliente_nuevo_84': True, 
        } 
    def act_cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
 
    def cron_importa(self, cr, uid, ids, context):
        return
    def srcen_importa(self, cr, uid, ids, context=None):
#         _logger.error('##### AIKO ###### Se ejecuta scren importa: ==>') 
        control_obj = self.pool.get('import.control') 
        obj_actividad = self.pool.get('import.control').browse(cr, uid, ids)
        
        if (obj_actividad.cabecera_81 == True):
            importa._create_report81(self, cr, uid, ids, context=None)
         
        if (obj_actividad.lineas_82 == True):
            importa._create_report82(self, cr, uid, ids, context=None)
            
        if (obj_actividad.cobros_83 == True):
            importa._create_report83(self, cr, uid, ids, context=None)
            
        if (obj_actividad.cliente_nuevo_84 == True):
            _logger.error('##### AIKO ###### Se ejecuta importa.report84: ==>') 
            importa._create_report84(self, cr, uid, ids, context=None)
    
        return

#8-2-16 Manuel: nuevas clases y funciones para control de importaciones
class tercap_route(osv.osv):
    _name = 'tercap.route'
    _columns = {
        'name': fields.char('Ruta del directorio Tercap', required=True, default='/var/ftp/TERCAP', help='En rutas windows utilizar \ en lugar de / Ej. C:\Dir\Fichero'),
        'alcance': fields.selection([('import', 'Importacion'), ('export', 'Exportacion')],'Alcance'),
        'enmays': fields.boolean('Datos de clientes en mayúsculas'),
        'inv_nombres': fields.boolean('Alternar nombre comercial y fiscal en Tercap'),
        'cif_partner': fields.boolean('Importar clientes solo con CIF'),
        'todo_pedidos': fields.boolean('Tercap importar todo como PEDIDOS'),
        'pedido_borrador': fields.boolean('Tercap importar pedidos en estado BORRADOR'),
        'product_default_idcode': fields.boolean('Ref. interna como identificador de PRODUCTO'),
        'unico_numero': fields.boolean('Pedidos y Albaranes con mismo identificador'),
        'saldo_cobrables': fields.boolean('Solo exportar cobros si se cobran albaranes'),
        'solo_unidades': fields.boolean('Descartar unidades en cajas'),
        'lotes_pedido': fields.boolean('Gestionar lote en el pedido'),
        'gestion_descanso': fields.boolean('Gestionar dias de descanso'),
        'num_relleno':fields.float('Relleno del numero', digits=(2,0)),
        }
    _defaults = {
                 'enmays': False,
                 'inv_nombres': False,
                 'cif_partner': False,
                 'todo_pedidos': False,
                 'pedido_borrador': False,
                 'unico_numero': False,
                 'product_default_idcode': True,
                 'saldo_cobrables': False,
                 'solo_unidades': False,
                 'lotes_pedido': False,
                 'gestion_descanso': False,
                 'num_relleno': 9,
                 }
    def nuevos_to_import(self, cr, uid, ids, context=None):
        #comprobamos que tiene alcance import, oprque sino no tiene sentido importar ficheros de esa ruta
        tipo = self.browse(cr, uid, ids)
        if (tipo.alcance=='export'):
            raise osv.except_osv(('Error!'),('No se pueden importar ficheros de una ruta de exportacion.'))
        res = importa._lista_files(self, cr, uid, ids, context=None)
        #si no hay ningun fichero nuevo sacamos mensaje
        if (res==0):
            raise osv.except_osv(('No hay nuevos ficheros'),('No hay ficheros nuevos para importar en la ruta indicada.'))
        #ponemos en el return la apertura del form de files, necesitamos encontrar el id del form
        form_id = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','view.files.tree')])
        #_logger.error('##### AIKO ###### Valor de form 1 en lista_files: %s' % form_id)
        if (len(form_id)>0):
            return {
                    'name': ('Ficheros TERCAP a importar'),
                    'view_type':'form',
                    'view_mode':'tree',
                    'view_id': form_id[0],
                    'res_model':'tercap_files',
                    'type':'ir.actions.act_window',
                    #si queremos abrir en nueva pestaña:
                    #'target':'new',
                    'target': 'current',
                    'context': "{'search_default_files_no_trasf':1, 'search_default_g_by_type': 1}",
                    }

        else:
            return True
    

class tercap_files(osv.osv):
    _name = 'tercap_files'
    
    def __listfiles (self, cr, uid, ids, name, self_args, context=None):
        importa._lista_files(self, cr, uid, ids, context=None)

    _columns = {
        'name': fields.char('Nombre del fichero', required=True),
        'route_id': fields.many2one('tercap.route', 'Directorio', ondelete="cascade"),
        'traspasado': fields.boolean('Traspasado a Odoo'),
        'descartado': fields.boolean('Descartada importacion'),
        'tipo': fields.char('Tipo de fichero'),
        'fecha': fields.date('Fecha del fichero'),
        'hora': fields.char('Hora del fichero'),
        'lista_files': fields.function(__listfiles, string='Carga de Ficheros',
                        help="Campo para importacion al cargar vista lista."),
        }

    _defaults = {
                 'traspasado': False,
                 'descartado': False,
                 }

    _order = "name asc"

    def action_files_import(self, cr, uid, ids, context=None):
        #filtrar para que solo se importen ficheros no traspasados en todo caso
        search_condition = [('traspasado', '=', False),('id','in',ids),('descartado', '=', False)]
        files_tras = self.search(cr, uid, search_condition, context=None)
        #comportamientos distintos segun el tipo de fichero leido
        res = {}
        files = self.browse(cr, uid, files_tras)
        for f in files:
            #_logger.error('##### AIKO ###### Valor de f.name en files_import:%s'%f.name) 
            #_logger.error('##### AIKO ###### Valor de f.route en files_import:%s'%f.route_id.name)
            #verficar que el fichero no ha sido ya cargado
            if (not f.traspasado):
                fichero = f.name [:6]
                if (fichero.upper() == 'CLIENT'):
                    #_logger.error('##### AIKO ###### Detectado Client en files_import:%s'%f.name)
                    res = importa.carga_datos_clientes(self, cr, uid, ids, f.route_id.name, f.name, context=None)
                    if (res): 
                        #_logger.error('##### AIKO ###### Import_control: Entro en sube datos cliente con id %s'%f.id)
                        res2 = importa.sube_datos_clientes(self, cr, uid, ids, f.route_id.name, f.name, context=None)
                        importa.act_files_import(self, cr, uid, f.id, context=None)
                    else:
                        raise osv.except_osv(('Error!'),('No se han podido cargar los datos del fichero de clientes.'))
                elif (fichero.upper() == 'COBROS'):
                    #_logger.error('##### AIKO ###### Detectado Cobro en files_import:%s'%fichero)
                    res = importa.carga_datos_cobros(self, cr, uid, ids, f.route_id.name, f.name, context=None)
                    if (res>0): 
                        importa.sube_datos_cobros(self, cr, uid, ids, f.route_id.name, f.name, context=None)
                        #marcamos como cargado el fichero de cobros
                        importa.act_files_import(self, cr, uid, f.id, context=None)
                    else:
                        raise osv.except_osv(('Error!'),('No se han podido cargar los datos del fichero de cobros.'))
                elif (fichero.upper() == 'DOCCAB'):
                    #los ficheros de lineas los importamos a continuacion de las cabeceras en la misma funcion, no tienen import propia
                    #_logger.error('##### AIKO ###### Detectado Cabecera en files_import:%s'%f.name)
                    res = importa.carga_datos_docs(self, cr, uid, ids, f.route_id.name, f.name, context=None)
                    ficlineas = 'DOCLIN'+f.name [6:]
                    #relinea = importa.carga_datos_lineas(self, cr, uid, ids, f.route_id.name, ficlineas, context=None)
                    if (res>0): 
                        #_logger.error('##### AIKO ###### Import_control: Entro en sube datos cabecera con id %s'%f.id)
                        res2 = importa.sube_datos_docs(self, cr, uid, ids, f.route_id.name, f.name, context=None)
                        #ademas cuando se importa un fichero de cabecera hay que importar el de lineas asociado
                        importa.sube_datos_lineas(self, cr, uid, ids, f.route_id.name, ficlineas, context=None)
                        #marcamos como cargado el fichero de cabecera (los de lineas no se van a mostrar nunca)
                        importa.act_files_import(self, cr, uid, f.id, context=None)
                       
                        #reslin = importa.carga_datos_lineas(self, cr, uid, ids, f.route_id.name, ficlineas, context=None)
                        #if (reslin):
                        #    
                            #y hay que marcar como importado el equivalente de lineas, para eso hay que buscarlo
                        #    search_condition = [('name', '=', ficlineas)]
                        #    file_lineas = self.search(cr, uid, search_condition, context=None)
                        #    importa.act_files_import(self, cr, uid, filelineas[0], context=None)
                            #una vez importado hay que lanzar el proceso de validacion de los pedidos en res
                        
                    else:
                        raise osv.except_osv(('Error!'),('No se han podido cargar los datos del fichero de clientes.'))
                
    def action_files_discard(self, cr, uid, ids, context=None):
        #filtrar para que solo se importen ficheros no traspasados en todo caso
        search_condition = [('id','in',ids),('descartado', '=', False)]
        files_tras = self.search(cr, uid, search_condition, context=None)
        #comportamientos distintos segun el tipo de fichero leido
        res = {}
        files = self.browse(cr, uid, files_tras)
        for f in files:
            self.write (cr,uid,f.id,{'descartado':'True'},context=context)

    
class res_partner(osv.osv):
    _inherit = 'res.partner'
    #creamos un campo para registrar el codigo de Tercap de clientes creados en las maquinas para poder importar sus pedidos iniciales
    _columns = {
        'cod_tercap' :fields.float('Codigo cliente en Tercap', digits=(6,0)),
        'factura_en_dir' : fields.boolean('Facturar a las direcciones de entrega'),
        'dia_descanso' : fields.char('Dia de descanso'),
    }
    _defaults = {
        'factura_en_dir' : False
    }

#ampliamos la clase account_journal para recoger un diario que registre los cobros de Tercap
class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'cobros_tercap' : fields.boolean('Diario para registrar los cobros de Tercap'),
    }
    _defaults = {
        'cobros_tercap' : False
    }

#06-07-16 ampliamos la clase sale_journal.invoice.type para recoger un diario que registre los cobros de Tercap
class sale_journal_invoice_type(osv.osv):
    _inherit = 'sale_journal.invoice.type'
    _columns = { 
        'tercap_cod_tipo_fact': fields.selection([  
            ('0', 'Credito'),                              
            ('1', 'Contado')], 'Codigo forma Pago TERCAP:'),     
        }
    

class product_template(osv.osv):
    _inherit = 'product.template'
    #obligamos que el default_code sea unico
    
    _sql_constraints = [('default_code_unique','unique(default_code)', 'Esa referencia ya existe. No se puede duplicar una referencia interna')]

#ampliamos la clase account_move para recoger la ruta asociada a un asiento
class account_move(osv.osv):
    _inherit = 'account.move'
    _columns = {
        'tercap_ruta_id': fields.related('partner_id','tercap_ruta_id',type='many2one', relation="ruta", string="Ruta", store=True),
    }

#creamos una clase para tener en una vista la relacion entre facturas y pedidos de venta
class invoice_sale_rel(osv.osv):
    _name = "invoice.sale.rel"
    #auto False para que no genere una tabla, porque es una vista
    _auto = False
    _columns = {
        'sale_order': fields.float('Sale Order ID', readonly=True),
        'id_invoice': fields.float('Invoice ID', readonly=True),
    }
    _order = 'id_invoice'
 
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'invoice_sale_rel')
        cr.execute("""
            CREATE OR REPLACE VIEW invoice_sale_rel AS (
                select distinct 
                    line.order_id as id,
                    line.order_id as sale_order,
                    invoice.id as id_invoice
                from sale_order_line line
                join sale_order_line_invoice_rel rel
                    on line.id = rel.order_line_id
                join account_invoice_line inv_line
                    on inv_line.id = rel.invoice_id
                join account_invoice invoice
                    on invoice.id = inv_line.invoice_id
                group by line.order_id, invoice.id
            )
        """)
 
#ampliamos la clase account_move_line para recoger los movimientos que ya estan conciliados en factura
class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    _columns = {
        'pasar_a_factura': fields.boolean('Registrado el pago en factura'),
    }

    _defaults = {
        'pasar_a_factura': True,
    }



#ampliamos la clase account_invoice para asociar en facturas los pagos de pedidos
class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def action_pago_pedidos(self, cr, uid, ids, context=None):
        salesinv_obj = self.pool.get('invoice.sale.rel')
        sale_obj = self.pool.get('sale.order')
        move_obj = self.pool.get('account.move.line')
        voucher_obj = self.pool.get('account.voucher')
        invoice = self.pool.get('account.invoice')

        for id in ids:
            if (self.browse(cr, uid, id).state=='paid'):
                #_logger.error('##### AIKO ###### Se ejecuta action_pago_pedidos: Factura ya pagada')
                continue
            #_logger.error('##### AIKO ###### Se ejecuta action_pago_pedidos: Id factura : %s' %id)
            search_condition=[('id_invoice','=',id)]
            sales_invs = salesinv_obj.search(cr,uid,search_condition)
            for s in sales_invs:
                #_logger.error('##### AIKO ###### Se ejecuta action_pago_pedidos: sale_order : %s' %s)
                sale_pays = sale_obj.browse(cr,uid,s).payment_ids
                if len(sale_pays)>0:
                    #_logger.error('##### AIKO ###### Se ejecuta action_pago_pedidos: sale_pays : %s' %sale_pays)

                    for p in sale_pays:
                        #_logger.error('##### AIKO ###### Se ejecuta action_pago_pedidos: payment_id : %s' %p)
                        
                        for c in p:
                            #_logger.error('##### AIKO ###### Se ejecuta action_pago_pedidos: payment_id.id : %s' %c.id)

                            move_id = move_obj.browse(cr,uid,c.id)
                            #pasamos el dato de cobro para registrar un cobro por cada pedido de venta cobrado
                            if (move_id.debit==0) and move_id.pasar_a_factura:
                                #con la linea de debit hacemos el voucher
                                #search_condition =[('credit','=',0),('move_id','=',move_id.move_id.id)]
                                #move_debit_id = move_obj.search (cr, uid, search_condition)
                                #move_debit = move_obj.browse(cr, uid, move_debit_id)
                                #new_voucher = importa.crea_voucher (self, cr, uid, id, move_debit, context=None)
                                new_voucher = voucher.crea_voucher_withpay (self, cr, uid, id, move_id, context=None)
                                voucher_obj.write(cr, uid, [new_voucher], {'state':'draft'}, context=context)
                                #y con el dato del nuevo voucher creamos sus lineas
                                voucher.crea_lineas_voucher_withpay(self, cr, uid, id, move_id, new_voucher, context=None)

                                #con el nuevo voucher creado registramos el pago de la factura
                                #voucher_brw = voucher_obj.browse(cr,uid,new_voucher)
                                #_logger.error('##### AIKO ###### Import_control en cobro factura valor del voucher a conciliar %s'%voucher_brw)
                                #voucher_brw.signal_workflow("proforma_voucher")
                                voucher_obj.button_proforma_voucher(cr, uid, [new_voucher], context=context)
                                #marcamos la factura para no volver a asociar pagos de sus pedidos
                                self.write(cr, uid, id,{'payment_reconcile':'True'},context=context)
                                #marcamos el movimiento para no repetirlo
                                move_obj.write (cr, uid, c.id,{'pasar_a_factura':'False'},context=context)
