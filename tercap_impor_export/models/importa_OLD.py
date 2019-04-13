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
import vatnumber
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields, orm
from openerp import api
from openerp.tools.translate import _
from openerp import tools
from openerp.tools import ustr
import csv
import glob, os, sys, stat
import unicodedata
from . import voucher
# import os, sys

from datetime import datetime


import logging 
_logger = logging.getLogger(__name__)

def _create_report81(self, cr, uid, ids, context=None):
    return
def _create_report82(self, cr, uid, ids, context=None):
    return
def _create_report83(self, cr, uid, ids, context=None):
    return
# ==================   Clientes 84 ==================================================================
def _create_report84(self, cr, uid, ids, context=None):
#     attendance_v={}
#     attendance_obj = self.pool.get('text.based.attendance')

    posicion_obj = self.pool.get('account.fiscal.position')
    pago_obj = self.pool.get('account.payment.term')
    customer_obj = self.pool.get('res.partner') 
    user = self.pool["res.users"].browse(cr, uid, uid)
    
    os.chdir("/var/ftp/TERCAP")

    for nombre in glob.glob("CLIENT*.txt"):
        f = open(nombre,'rU') 
        c = csv.reader(f, delimiter=';', skipinitialspace=True)
        for line in c:
            if line:
                if line[0] == '0000990001':
                    values = {}       
                    values['active'] = True
                    values['customer'] = True 
                    values['company_id'] = user.company_id.id 
                    #4-5 si la ruta dice que se invierten nombres comercial y fiscal lo tenemos aqui en cuenta
                    inv_names = self.pool.get('tercap.route').browse (cr,uid,1)
                    if (inv_names.inv_nombres):
                        values['name'] = ustr(line[2])
                        values['comercial'] = ustr(line[1])
                    else:
                        values['name'] = ustr(line[1])
                        values['comercial'] = ustr(line[2])
                    values['street'] = ustr(line[3])
                    values['city'] = ustr(line[4])
                    if vatnumber.check_vat(line[5]): 
                        values['vat'] = line[5]
                    search_condition = [('active', '=', True),('tercap_cod_forma_pago','=', line[6])]
                    pago_selec_obj = pago_obj.search(cr, uid, search_condition )            
                    for pago in pago_selec_obj:
                        values['property_payment_term'] = pago
                        continue
    
                    search_condition = [('active', '=', True),('tercap_tipo_iva','=', line[7]),('company_id', '=', user.company_id.id)            ]
                    posicion_selec_obj = posicion_obj.search(cr, uid, search_condition )            
                    for posicion in posicion_selec_obj:
                        values['property_account_position'] = posicion
                        continue
    
                    values['comment'] = ustr(line[8])
           
                    customer_create_id = customer_obj.create(cr,SUPERUSER_ID,values,context=None)
    
        f.close()
        base = os.path.splitext(nombre)[0]
        os.rename(nombre, base + ".pro")
    return

# ==================   Funciones revisadas Manuel 9-2-16 ================================



# ================== Necesitamos una funcion para codificar en UTF-8 el dato que viene en Win-1250
def reencode(file):
    for line in file:
        yield line.encode('utf-8')


def _lista_files (self, cr, uid, ids, context=None):
    #limitamos la busqueda de ficheros a las rutas definidas como importacion
    search_condition = [('alcance', '=', 'import')]
    #creamos los objetos que vamos a usar: el tercap_route y el tercap_files
    directory_obj = self.pool['tercap.route']
    newfiles_obj = self.pool['tercap_files']
    #filtramos en tercap_route con la condicion de que sean de import
    direct_imp_obj = directory_obj.search(cr, uid, search_condition )
    #excepcion si no se ha configurado ruta de importacion
    if (len(direct_imp_obj)==0):
        raise osv.except_osv(('Error!'),('No se ha definido ninguna ruta de importación de Tercap. Revise la configuración'))

    #recorremos las instancias que cumplan son de ruta import
    for est in direct_imp_obj:
        #cargamos los datos de cada instancia con browse
        dato = directory_obj.browse(cr, uid, est)
        #_logger.error('##### AIKO ###### Valor de dato en lista_files: %s' % dato.name)
        #accedemos a la ruta recogida en el objeto dato con el valor name
        os.chdir(dato.name)

        #29-4-16 hay que modificar permisos de los ficheros de TERCAP
        #for root, dirs, files in os.walk(dato.name):
        #    for file in files:
        #        pp=os.path.join(root, file).replace("""\\""",'/')
        #        st = os.stat(pp)
                #os.chown(pp, int(os.environ.get('SUDO_UID')), int(os.environ.get('SUDO_GID')))
                #os.chmod(pp, st.st_mode | stat.S_IWUSR|stat.S_IWGRP|stat.S_IWOTH)
        #       os.chmod(pp, st.st_mode | 0o111)


        #recorremos todos los ficheros con extension valida txt
        #y creamos un contador para comprobar si hay nuevos ficheros o no
        counter = 0
        #ponemos en un array los tipos de ficheros válidos
        fic_type = ('*.txt','*.TXT')
        #y repetimos el proceso de carga por cada tipo del array definido
        for type in fic_type:
            for nombre in glob.glob(type):
                
                #_logger.error('##### AIKO ###### Valor de nombre en lista_files: %s' % nombre)
                #_logger.error('##### AIKO ###### Valor de id_ruta en lista_files: %s' % int(dato.id))
                #creamos la variable que va a recoger el dato del nombre del fichero
                values ={}
                #comprobamos que el fichero no esta cargado anteriormente (no hace falta borrarlos del directorio)
                search_file = [('name', '=', nombre)]
                #buscamos en el objeto files si hay coincidencias de nombre
                newfile_selec_obj = newfiles_obj.search(cr, uid, search_file )
                #nueva variable para registrar el tipo de fichero
                tipo=''
                #comprobamos con len si el objeto tiene instancias o no
                if (len(newfile_selec_obj)==0):
                    #no vamos a registrar los ficheros de lineas
                    if (str(nombre)[:6] not in 'DOCLIN'):
                        #_logger.error('##### AIKO ###### Este no es un fichero de lineas: %s' % str(nombre)[:6])
                        #ademas para registrar un pedido de cabecera tiene que tener uno de lineas asociado
                        if (str(nombre)[:6] in 'DOCCAB'):
                            #_logger.error('##### AIKO ###### Este ES un fichero de cabecera: %s' % str(nombre)[:6])
                            tipo = 'Nuevos documentos'
                            ficlineas = 'DOCLIN'+ str(nombre)[6:]
                            coinciden = 0
                            for names in glob.glob(type):
                                if (names in ficlineas):
                                    #_logger.error('##### AIKO ###### El fichero de cabecera tiene lineas: %s' % ficlineas)
                                    coinciden+=1
                            if (coinciden > 0):
                                values['name'] = nombre
                                values['route_id'] = int(dato.id)
                                values['tipo'] = tipo
                                fecha_fichero = str(nombre)[16:18]+'/'+str(nombre)[14:16]+'/'+str(nombre)[10:14]
                                hora_fichero = str(nombre)[18:20]+':'+str(nombre)[20:22]+':'+str(nombre)[22:24]
                                values['hora'] = hora_fichero
                                values['fecha'] = fecha_fichero
                                #registramos el nombre del fichero en el objeto tercap_files
                                #_logger.error('##### AIKO ###### registramos fichero de cabecera: %s' % nombre)
                                newfiles_obj.create (cr,SUPERUSER_ID,values,context=None)
                                #sumamos los nuevos ficheros registrados
                                counter += 1
                        else:
                            if (str(nombre)[:6] in 'CLIENT'):
                                tipo = 'Clientes nuevos'
                            if (str(nombre)[:6] in 'COBROS'):
                                tipo = 'Pendientes de Cobro'
                            #si no es de cabecera, hacemos un registro normal
                            values['name'] = nombre
                            values['route_id'] = int(dato.id)
                            values['tipo'] = tipo
                            fecha_fichero = str(nombre)[16:18]+'/'+str(nombre)[14:16]+'/'+str(nombre)[10:14]
                            hora_fichero = str(nombre)[18:20]+':'+str(nombre)[20:22]+':'+str(nombre)[22:24]
                            values['hora'] = hora_fichero
                            values['fecha'] = fecha_fichero
                            #_logger.error('##### AIKO ###### registramos otros ficheros: %s' % nombre)
                            #registramos el nombre del fichero en el objeto tercap_files
                            newfiles_obj.create (cr,SUPERUSER_ID,values,context=None)
                            #sumamos los nuevos ficheros registrados
                            counter += 1
                    #else:
                        #_logger.error('##### AIKO ###### LOCALIZADO FICHEROS DE DOCLIN: %s' % str(nombre)[6:])
        #mensages del resultado de la importacion de ficheros
        #_logger.error('##### AIKO ###### Valor de counter en lista_files: %s' % counter)
        return counter
    
def sube_datos_clientes(self, cr, uid, ids, ruta, file, context=None):
    my_obj = self.pool.get('tercap.import.customers')
    os.chdir(ruta)
    #_logger.error('##### AIKO ###### Valor de f.name recibido:%s'%file)
    #_logger.error('##### AIKO ###### Valor de ruta recibido:%s'%ruta)
    for nombre in glob.glob(file):
        f = open(nombre,'rU') 
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        c = csv.reader(f, delimiter=";", skipinitialspace=True)

        #_logger.error('##### AIKO ###### Abierto fichero:%s'%file)
        for line in c:
            #22-3-16 verificamos que la linea no este en blanco (un salto de linea de mas)
            if (line):
                ref = fields.datetime.now()
                values = {}

                values['name']= ref
                values['codcliente']= line[0]
                values['nombrefiscal']= ustr(line[1], errors='replace')
                values['nombrecomercial']= ustr(line[2], errors='replace')
                values['direccion']= ustr(line[3], errors='replace')
                values['poblacion']= ustr(line[4], errors='replace')
                values['cifnif']= line[5]
                values['codformapago']= line[6]
                values['tipoiva']= line[7]
                if (line[8]!=''):
                   values['observaciones']= ustr(line[8], errors='replace')
                values['id_ruta'] = line[9]
                #27/6/16 pueden venir nuevos datos segun la version de TercapAV usada
                if len(line)>10:
                    if line[10]!='':
                        values['codigo_postal']=str(line[10])
                    if line[11]!='':
                        values['telefono'] = str(line[11])
                    if line[12]!='':
                        values['dia_descanso']= str(line[12])
                #01/08/16 puede venir nuevo valor con la ruta de reparto
                if len(line)>13:
                    if line[13]!='':
                        values['tercap_reparto_id']=float(int(line[13]))


                #_logger.error('##### AIKO ###### Sube datos clientes: Estos valores a registrar:%s'%values)
                newline_id = my_obj.create(cr, SUPERUSER_ID, values, context=None)
                    
        f.close()
        
    return True
        
def carga_datos_clientes (self, cr, uid, ids, ruta, file, context=None):
    posicion_obj = self.pool.get('account.fiscal.position')
    #4-5-16 cambiamos el plazo de pago por el modo de pago
    #pago_obj = self.pool.get('account.payment.term')
    modop_obj = self.pool.get('payment.mode')
    tipofac_obj = self.pool.get('sale_journal.invoice.type')
    customer_obj = self.pool.get('res.partner')
    rutaT_obj = self.pool.get('ruta') 
    user = self.pool["res.users"].browse(cr, uid, uid)
    
    os.chdir(ruta)
    #necesitamos controlar si la ruta nos pide clientes en mayusculas o no
    ruta_obj = self.pool.get('tercap.route').browse(cr, uid, 1)

    for nombre in glob.glob(file):  
        f = open(nombre,'r+') 
        #24-2-16 es necesario controlar la codificacion, solo admite UTF-8 y Tercap manda Win-1252
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        c = csv.reader(f, delimiter=";", skipinitialspace=True)

        for line in c:
            if line:
                #el identificador de nuevo cliente en Tercap es variable, no es un criterio de seleccion de nuevos clientes
                #todos los clientes en este fichero son nuevos
                #line[0] = CodCliente : lo registramos como cod_tercap en la ficha de cliente
                #line[1] = NombreFiscal
                #line[2] = NombreComercial
                #line[3] = Direccion
                #line[4] = Poblacion
                #line[5] = CIF
                #line[6] = CodFormaPago, el Modo De Pago 0=Credito, 1=Contado.
                #line[7] = TipoIVA, N=normal, R=Recargo Eq., E=exento
                #line[8] = Observaciones
                #line[9] = CodigoRuta
                #line[10] = CodigoPostal
                #line[11] = Telefono
                #line[12] = DiaDescanso del cliente
                #line[13] = CodRutaEntrega : la ruta de reparto asignada por defecto al cliente
                #novedad version 23 del 27-9-16:
                #line[14] = CodFormaPagoERP : Forma de pago del cliente segun codigos del ERP

                #19-4-16 si esta marcado en la ruta que no se importen clientes sin cif(potenciales)
                if ruta_obj.cif_partner and (line[5]=='0'):
                    #_logger.error('##### AIKO ###### Nuevo cliente detectado potencial.')
                    continue
                values = {}  
                values['cod_tercap'] = line[0]
                values['active'] = True
                values['customer'] = True
                #tenemos que marcarlos como empresa para que muestre el nombre comercial en la ficha 
                values['is_company'] = True 
                values['company_id'] = user.company_id.id 
                #4-5 si la ruta dice que se invierten nombres comercial y fiscal lo tenemos aqui en cuenta
                if (ruta_obj.inv_nombres):
                    if (line[2]==''):
                        raise osv.except_osv(('Error!'),('No hay dato de nombre, no se puede realizar la importacion de datos del cliente.'))
                    nuevo_nombre = ustr(line[2])
                    if (line[1]!='') : nuevo_comercial = ustr(line[1])

                    if ruta_obj.enmays:
                        nuevo_nombre = nuevo_nombre.upper()
                        if nuevo_comercial: nuevo_comercial = nuevo_comercial.upper() 
                    values['name'] = nuevo_nombre
                    if nuevo_comercial: values['comercial'] = nuevo_comercial
                else:
                    if (line[1]==''):
                        raise osv.except_osv(('Error!'),('No hay dato de nombre, no se puede realizar la importacion de datos del cliente.'))
                    nuevo_nombre = ustr(line[1])
                    if (line[2]!='') : nuevo_comercial = ustr(line[2])

                    if ruta_obj.enmays:
                        nuevo_nombre = nuevo_nombre.upper()
                        if nuevo_comercial: nuevo_comercial = nuevo_comercial.upper() 
                    values['name'] = nuevo_nombre
                    if nuevo_comercial: values['comercial'] = nuevo_comercial
                if (line[3]!='') : values['street'] = ustr(line[3])
                if (line[4]!='') : values['city'] = ustr(line[4])
                #le agregamos ES delante del cif porque Tercap no envia este dato
                if ((line[5]!='') and (str(line[5])[:2]!='ES')):
                    dni_es = 'ES'+ line[5] 
                elif (line[5]==''):
                    dni_es='0'
                else:
                    dni_es = line[5]
                if vatnumber.check_vat(dni_es): 
                    values['vat'] = dni_es

                search_condition = [('active', '=', True),('tercap_cod_modo_pago','=', line[6])]
                pago_selec_obj = modop_obj.search(cr, uid, search_condition )            
                if len(pago_selec_obj)>0:
                    values['customer_payment_mode'] = pago_selec_obj[0]

                search_condition = [('active', '=', True),('tercap_cod_tipo_fact','=', line[6])]
                tipofac_obj_src = tipofac_obj.search(cr, uid, search_condition )
                if len(tipofac_obj_src)>0:
                    values['property_invoice_type'] = tipofac_obj_src[0]
    
                search_condition = [('active', '=', True),('tercap_tipo_iva','=', line[7]),('company_id', '=', user.company_id.id)]
                posicion_selec_obj = posicion_obj.search(cr, uid, search_condition ) 
                if (len(posicion_selec_obj)==0):
                    _logger.error('##### AIKO ###### Alta de clientes: No se han definido las posiciones fiscales de clientes.')
                    #raise osv.except_osv(('Error!'),('No se han definido las posiciones fiscales de clientes para la aplicación de Tercap. Revise la configuración'))
                else:
                    for posicion in posicion_selec_obj:
                        values['property_account_position'] = posicion

                if (line[8]!=''):
                    values['comment'] = ustr(line[8])

                #14-7-16 usamos el valor de la ruta para encontrar el equipo de venta asociado al cliente
                search_condition = [('active', '=', True),('cod_tercap','=', int(float(line[9])))]
                rutaT_selec_obj = rutaT_obj.search(cr, uid, search_condition) 
                if (len(rutaT_selec_obj)!=0):
                    rutaT_brw_obj = rutaT_obj.browse(cr, uid, rutaT_selec_obj[0])
                    #si la ruta tiene asociado un equipo de venta, este cliente lo registramos con ese equipo
                    if (rutaT_brw_obj.cod_equipo):
                        values['section_id']=rutaT_brw_obj.cod_equipo.id

                #6-5 agregamos un valor Ind para el campo ref, necesario por informes
                values['ref'] = 'Ind'
                #27/6/16 pueden venir nuevos datos segun la version de TercapAV usada
                if len(line)>10:
                    if line[10]!='':
                        values['zip']=str(line[10])
                    if line[11]!='':
                        values['phone'] = str(line[11])
                    #solo tratamos el valor de dia de descanso si se configura para utilizarlo
                    if (ruta_obj.gestion_descanso):
                        if line[12]!='':
                            valor_dia_desc = (str(line[12]).upper()).strip()
                            #_logger.error('##### AIKO ###### Nuevo cliente dia descanso recibo:%s'%valor_dia_desc)
                            if valor_dia_desc in ['LUNES','MARTES','MIERCOLES','MIÉRCOLES','JUEVES','VIERNES','SABADO','SÁBADO','DOMINGO']:
                                values['dia_descanso']= valor_dia_desc
                                values['sale_warn']='warning'
                                values['sale_warn_msg']= 'DESCANSO '+valor_dia_desc
                                values['picking_warn']='warning'
                                values['picking_warn_msg']= 'DESCANSO '+valor_dia_desc
                            else:
                                values['dia_descanso']= 'NO TIENE'
                #01/08/16 puede venir valor de la ruta de reparto del cliente
                if len (line)>13:
                    if int(float(line[13]))!=0:
                        #buscamos el id de la ruta que corresponde con el cod_tercap recibido
                        #_logger.error('##### AIKO ###### Nuevo cliente buscando reparto:%s'%line[13])
                        search_condition = [('active', '=', True),('cod_tercap','=', int(float(line[13])))]
                        rutaT_selec_obj = rutaT_obj.search(cr, uid, search_condition) 
                        if (len(rutaT_selec_obj)!=0):
                            #_logger.error('##### AIKO ###### Nuevo cliente buscando encontrado reparto:%s'%rutaT_selec_obj[0])
                            values['tercap_reparto_id'] = rutaT_selec_obj[0]

                #27-9-16 puede venir valor de la forma de pago del cliente
                if len (line) > 14:
                    if int(float(line[14]))!=0:
                        #buscamos el id de la forma de pago que corresponde con el codigo recibido
                        #_logger.error('##### AIKO ###### Nuevo cliente buscando forma de pago:%s'%line[14])
                        search_condition = [('active', '=', True),('id','=', int(float(line[14])))]
                        pago_selec_obj = modop_obj.search(cr, uid, search_condition )
                        if (len(pago_selec_obj)!=0):
                            #_logger.error('##### AIKO ###### Nuevo cliente buscando encontrado forma de pago:%s'%pago_selec_obj[0])
                            values['customer_payment_mode'] = pago_selec_obj[0]


                #_logger.error('##### AIKO ###### Nuevo cliente a crear con estos valores:%s'%values)
                customer_create_id = customer_obj.create(cr,SUPERUSER_ID,values,context=None)
                #_logger.error('##### AIKO ###### Nuevo cliente guardado con id:%s'%customer_create_id)

                #parado hasta ver como nos llega informacion del rutero del cliente, con la ruta sola no vale
                #if (line[9]!=''):
                #    search_condition = [('cod_tercap','=',line[9]),()]
                #    ruta_obj_id = ruta_obj.search (cr, uid, search_condition)
                #    if len(ruta_obj_id<>0):
                #        values['tercap_ruta_id']= ruta_obj_id[0]
    
        f.close()

    return True

def act_files_import (self, cr, uid, ids, context=None):
    my_obj = self.pool.get('tercap_files')
    #fileup = my_obj.search(cr, uid, [('name','=',name)])
    #for f in fileup:
    #_logger.error('##### AIKO ###### Coge el id:%s'%ids)
    my_obj.write(cr, uid, ids, {'traspasado': True}, context=None)

def sube_datos_cobros(self, cr, uid, ids, ruta, file, context=None):
    my_obj = self.pool.get('tercap.import.payments')
    os.chdir(ruta)
    #_logger.error('##### AIKO ###### Valor de f.name recibido:%s'%file)
    #_logger.error('##### AIKO ###### Valor de ruta recibido:%s'%ruta)
    for nombre in glob.glob(file):
        f = open(nombre,'rU') 
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        c = csv.reader(f, delimiter=";", skipinitialspace=True)

        #_logger.error('##### AIKO ###### Abierto fichero:%s'%file)
        for line in c:
            #22-3-16 verificamos que la linea no este en blanco (un salto de linea de mas)
            if (line):
                ref = fields.datetime.now()
                values = {
                    'name': ref,
                    'codcliente': line[0],
                    'coddireccion': line[1],
                    'numdocumento': line[2],
                    'tipodocumento': line[3],
                    'fechadocumento': line[4],
                    'importedocum': line[5],
                    'importependiente': line[6],
                    'codcliealternativo': line[7],
                    'coddirealternativo': line[8],
                }
                #_logger.error('##### AIKO ###### Estos valores a registrar:%s'%values)
                newline_id = my_obj.create(cr, SUPERUSER_ID, values, context=None)
                    
        f.close()
        
def sube_datos_docs(self, cr, uid, ids, ruta, file, context=None):
    my_obj = self.pool.get('tercap.import.document')
    os.chdir(ruta)
    #_logger.error('##### AIKO ###### Valor de f.name recibido:%s'%file)
    #_logger.error('##### AIKO ###### Valor de ruta recibido:%s'%ruta)
    for nombre in glob.glob(file):
        f = open(nombre,'rU') 
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        c = csv.reader(f, delimiter=";", skipinitialspace=True)

        #_logger.error('##### AIKO ###### Abierto fichero:%s'%file)
        for line in c:
            #22-3-16 verificamos que la linea no este en blanco (un salto de linea de mas)
            if (line):
                ref = fields.datetime.now()
                values = {
                    'name': ref,
                    'numdocumento': line[0],
                    'fechadocumento': line[1],
                    'tipodocumento': line[2],
                    'serie': line[3],
                    'docespecial': line[4],
                    'codempresa': line[5],
                    'codigoruta': line[6],
                    'codvendedor': line[7],
                    'codcliente': line[8],
                    'coddireccion': line[9],
                    'fechaentrega': line[10],
                    'codclientealternativo': line[11],
                    'coddirealternativo': line[12],
                    'documentoorigen': line[13],
                    'base1': line[14],
                    'base2': line[15],
                    'base3': line[16],
                    'descuento': line[17],
                    'descuentopp': line[18],
                    'iva1': line[19],
                    'iva2': line[20],
                    'iva3': line[21],
                    'importerecargo1': line[22],
                    'importerecargo2': line[23],
                    'importerecargo3': line[24],
                    'totaldocumento': line[25],
                    'importecobrado': line[26],
                    'codmotivo': line[27],
                    'formapagoerp': line[28],
                    'codproveedor': line[29],
                }
                #_logger.error('##### AIKO ###### Estos valores a registrar:%s'%values)
                newline_id = my_obj.create(cr, SUPERUSER_ID, values, context=None)
        
        f.close()

def comprueba_clientes (self, cr, uid, ids, ruta, file, context=None):
    hay = True
    partner_obj = self.pool.get('res.partner')
    os.chdir(ruta)
    for nombre in glob.glob(file):   
        f = open(nombre,'rU') 
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        c = csv.reader(f, delimiter=";", skipinitialspace=True)

        #24-2-16 antes de importar datos comprobar que los datos de clientes relacionados estan importados
        for l in c:
            if l:
                ter_codcliente = int(float(l[8]))if l[8] else  '0'

                partner_condition = [('cod_tercap', '=', ter_codcliente)]
                partner_obj_id = partner_obj.search(cr, uid, partner_condition)
                if (len(partner_obj_id)==0):
                    partner_condition = [('id', '=', ter_codcliente)]
                    partner_obj_id2 = partner_obj.search(cr, uid, partner_condition)
                    if (len(partner_obj_id2)==0):
                      hay = False  

        f.close()

    return hay


def comprueba_cliente (self, cr, uid, cod_cliente, context=None):
    partner_obj = self.pool.get('res.partner')
    hay = True
    partner_condition = [('cod_tercap', '=', cod_cliente)]
    partner_obj_id = partner_obj.search(cr, uid, partner_condition)
    if (len(partner_obj_id)==0):
        partner_condition = [('id', '=', cod_cliente)]
        partner_obj_id2 = partner_obj.search(cr, uid, partner_condition)
        if (len(partner_obj_id2)==0):
            hay = False

    return hay



def genera_factura (self, cr, uid, sale_id, date_order, numfactura, cobro, total, pago, context=None):
    ids = []
    ids.append (sale_id)
    #_logger.error('##### AIKO ###### Genera_factura envia el dato de sale order %s'%ids)

    
    sale_obj = self.pool.get('sale.order')
    sale_line_obj = self.pool.get('sale.order.line')
    invoice_obj = self.pool.get('account.invoice')
    inv_line_obj = self.pool.get('account.invoice.line')
    journal_obj = self.pool.get('account.journal')
    voucher_obj = self.pool.get('account.voucher')
    voucher_line_obj = self.pool.get('account.voucher.line')

    for id in ids:
        sale_obj_id = sale_obj.browse(cr,uid,id)
        valfac ={}
        valfac['partner_id'] = sale_obj_id.partner_id.id
        #if (sale_obj_id.partner_id.tax_ids):
        #    valfac['fiscal_position'] = sale_obj_id.partner_id.tax_ids.id
        valfac['account_id'] = sale_obj_id.partner_id.property_account_receivable.id
        #_logger.error('##### AIKO ###### Genera_factura valor de ruta de cliente %s'%sale_obj_id.partner_id.tercap_ruta_id)
        #_logger.error('##### AIKO ###### Genera_factura valor de journal %s'%sale_obj_id.partner_id.tercap_ruta_id.journal_id.id)
        if (sale_obj_id.partner_id.tercap_ruta_id.journal_id.id):
            valfac['journal_id'] = sale_obj_id.partner_id.tercap_ruta_id.journal_id.id
        valfac['origin'] = sale_obj_id.name
        valfac['reference'] = sale_obj_id.name
        valfac['number'] = numfactura
        valfac['internal_number'] = numfactura
        valfac['invoice_number'] = numfactura
        valfac['date_invoice'] = date_order
        if (sale_obj_id.partner_id.property_account_position):
            valfac['fiscal_position'] = sale_obj_id.partner_id.property_account_position.id
        sale_ids=[]
        sale_ids.append (id)
        valfac['sale_ids'] = [(6, 0, sale_ids)]
        #21-12-16 agregamos el modo de pago en la factura
        if pago!=0:
            valfac['payment_mode_id'] = pago
        #_logger.error('##### AIKO ###### Genera_factura valores para factura %s'%valfac)

        new_invoice_id = invoice_obj.create(cr,SUPERUSER_ID,valfac,context=None)
        #_logger.error('##### AIKO ###### Genera_factura resultado de crear factura %s'%new_invoice_id)

        if(new_invoice_id):
            search_condition = [('order_id','=',id)]
            inv_lines = sale_line_obj.search(cr,uid,search_condition)
            for il in inv_lines:
                sl_ln_ob = sale_line_obj.browse(cr,uid,il)
                vallines = {}
                vallines['invoice_id'] = new_invoice_id
                vallines['name'] = sl_ln_ob.name
                vallines['origin'] = sale_obj_id.name
                vallines['uos_id'] = sl_ln_ob.product_uom.id
                vallines['product_id'] = sl_ln_ob.product_id.id
                if (sl_ln_ob.product_id.property_account_income):
                    vallines['acccount_id'] = sl_ln_ob.product_id.property_account_income.id
                else:
                    vallines['account_id'] = sl_ln_ob.product_id.categ_id.property_account_income_categ.id
                vallines['price_unit'] = sl_ln_ob.price_unit
                vallines['quantity'] = sl_ln_ob.product_uom_qty
                vallines['discount1'] = sl_ln_ob.discount
                vallines['discount'] = sl_ln_ob.discount
                vallines['partner_id'] = sale_obj_id.partner_id.id
                taxes=[]
                for tax in sl_ln_ob.tax_id:
                    taxes.append (tax.id)
                vallines['invoice_line_tax_id'] = [(6, 0, taxes)]
                #_logger.error('##### AIKO ###### Genera_factura valores para linea %s'%vallines)
                new_inv_line_id = inv_line_obj.create(cr,SUPERUSER_ID,vallines,context=None)
                asocia_lineas_factura (self,cr,uid,new_inv_line_id,il)

        invoice_obj.button_compute(cr,uid,[new_invoice_id],context=context,set_total=True)
        invoice_obj.action_move_create(cr,uid,[new_invoice_id],context=context)
        #invoice_obj.action_number(cr,uid,new_invoice_id,context=context)
        invoice_obj.invoice_validate(cr,uid,[new_invoice_id],context=context)

        # add the invoice to the sales order's invoices and state as done
        valsinv={}
        valsinv['invoice_ids'] = (4, new_invoice_id)
        valsinv['state'] = 'done'
        asoc = sale_obj.write(cr, uid, sale_id, valsinv, context=context)
        #_logger.error('##### AIKO ###### Genera_factura asociar a factura nos da %s'%asoc)


        #queda pendiente recibir un cobro si hay importe cobrado de la factura y registrar el pago
        invoice = invoice_obj.browse(cr,uid,new_invoice_id)
        if cobro > 0:
            #lo primero ajustamos el pago, si es completo al importe de la factura para evitar diferencias de centimos
            cobroaj = 0
            if cobro == total:
                cobroaj = invoice.residual
            else:
                cobroaj = cobro

            #generamos un recibo voucher con valores
            new_voucher_id = voucher.crea_voucher(self, cr, uid, new_invoice_id, cobroaj, context=context)
            #registramos las lineas de ese recibo
            voucher.crea_lineas_voucher(self, cr, uid, new_invoice_id, cobroaj, new_voucher_id, context=context)

            #con el nuevo voucher creado registramos el pago de la factura
            voucher_brw = voucher_obj.browse(cr,uid,new_voucher_id)
            #_logger.error('##### AIKO ###### Genera_factura valor del voucher a conciliar %s'%voucher_brw)
            voucher_brw.signal_workflow("proforma_voucher")

            #si el importe del pago es el total damos por pagada la factura
            if cobro == total:
                invoice_obj.write(cr,uid,new_invoice_id,{'state':'paid'},context=None)

        
    #_logger.error('##### AIKO ###### Genera_factura obtiene al final el dato %s'%new_invoice_id)
            
        
def carga_datos_docs (self, cr, uid, ids, ruta, file, context=None):
    #paramos esta comprobacion al principio para hacerla en cada linea y decidir si se carga o no el pedido
    '''
    hay_cliente = comprueba_clientes(self, cr, uid, ids, ruta, file, context=None)
    if (hay_cliente==False):
        #si no se encuentra el cliente ni por id ni por cod_tercap, es que hay que importar antes el fichero de clientes
        raise osv.except_osv(('Error!'),('No existe dato del cliente para registrar el documento. Debe cargar antes los datos del fichero de clientes.'))
    '''

    posicion_obj = self.pool.get('account.fiscal.position')
    #pago_obj = self.pool.get('account.payment.term')
    #21-12-16 se cambia por el modo de pago:
    pago_obj = self.pool.get('payment.mode')
    eqvtas_obj = self.pool.get('crm.case.section') 
    user = self.pool["res.users"].browse(cr, uid, uid)
    pedido_obj = self.pool.get('sale.order')
    partner_obj = self.pool.get('res.partner')
    pay_obj = self.pool.get('pay.sale.order')
    journal_obj = self.pool.get('account.journal')
    tercapruta_obj = self.pool.get('tercap.route').browse(cr, uid, 1)
    #12-5-16 necesitamos tercap_import_document para comprobar duplicaciones
    tercap_impdoc = self.pool.get('tercap.import.document')
    #30-6-16 necesitamos las rutas para localizar rutas de reparto
    reparto_obj = self.pool.get('ruta')


    #comprobamos que en configuracion se ha asociado un diario para registrar los cobros de Tercap
    search_condition = [('cobros_tercap','=',True)]
    journal_obj_id = journal_obj.search (cr, uid, search_condition )
    if (len(journal_obj_id)==0):
        raise osv.except_osv(('Error!'),('No se ha definido un diario para el registro de cobros de Tercap. Revise la configuración')) 

    
    os.chdir(ruta)
    for nombre in glob.glob(file):   
        f = open(nombre,'rU') 
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        c = csv.reader(f, delimiter=";", skipinitialspace=True)

        for line in c:
            if line:

                #_logger.error('##### AIKO ###### Entro en carga_datos_docs para el fichero %s'%file)
                
                #line [0] = NumDocumento
                #line [1] = FechaDocumento
                #line [2] = TipoDocumento
                #line [3] = Serie
                #line [4] = DocEspecial: 0 = Con IVA
                #line [5] = CodEmpresa = 1
                #line [6] = CodigoRuta
                #line [7] = CodVendedor
                #line [8] = CodCliente
                #line [9] = CodDireccion
                #line [10] = FechaEntrega
                #line [11] = CodClienteAlternativo
                #line [12] = CodDireccionAlternativo
                #line [13] = Documento Origen
                #line [14] = Base1 (Base al tipo de IVA general == 21%)
                #line [15] = Base2 (Base al tipo de IVA reducido == 10%)
                #line [16] = Base3 (Base al tipo de IVA super-reducido == 4%)
                #line [17] = Descuento
                #line [18] = Descuento ProntoPago
                #line [19] = Cuota1 (Cuota al tipo de IVA general == 21%)
                #line [20] = Cuota2 (Cuota al tipo de IVA reducido == 10%)
                #line [21] = Cuota3 (Cuota al tipo de IVA super-reducido == 4%)
                #line [22] = R.Eq.1 (Recargo al tipo de IVA general == 21%)
                #line [23] = R.Eq.2 (Recargo al tipo de IVA reducido == 10%)
                #line [24] = R.Eq.3 (Recargo al tipo de IVA super-reducido == 4%)
                #line [25] = Importe Total Documento
                #line [26] = Importe Total Cobrado
                #line [27] = CodMotivo: 0 = Venta; solo para documentos NO VENTA, tipo 10; no tratados.
                #line [28] = FormaPagoERP (segun códigos (ids) de Formas de Pago exportados)
                #line [29] = CodProveedor, en documentos de venta indirecta; no tratado.
                #line [30] = CodRutaEntrega (según códigos (ids) de Rutas exportados: la ruta de reparto)

                #antes de tratar datos pasamos las cadenas numericas a valores
                ter_numdoc = int(float(line[0]))if line[0] else  ' '
                ter_dateorder = line[1]
                ter_tipodoc = int(float(line[2]))if line[2] else  ' '
                ter_codvend = int(float(line[7]))if line[7] else  ' '
                ter_codcliente = int(float(line[8]))if line[8] else  '0'
                ter_direntrega = int(float(line[9]))if line[9] else  '0'
                ter_fechaentrega = str(line[10])
                ter_base1 = float(line[14])if line[14] else  '0'
                ter_base2 = float(line[15])if line[15] else  '0'
                ter_base3 = float(line[16])if line[16] else  '0'
                ter_dto = float(line[17])if line[17] else  '0'
                ter_dtopp = float(line[18])if line[18] else  '0'
                ter_iva1 = float(line[19])if line[19] else  '0'
                ter_iva2 = float(line[20])if line[20] else  '0'
                ter_iva3 = float(line[21])if line[21] else  '0'
                ter_recargo1 = float(line[22])if line[22] else  '0'
                ter_recargo2 = float(line[23])if line[23] else  '0'
                ter_recargo3 = float(line[24])if line[24] else  '0'
                ter_totaldoc = float(line[25])if line[25] else  '0'
                ter_cobrado = float(line[26])if line[26] else  '0'
                ter_paytermid = int(float(line[28]))if line[28] else  ' '

                #16-6-16 comprobamos ahora aqui si hay cliente para cargar este pedido o no
                hay_cliente = comprueba_cliente(self, cr, uid, ter_codcliente, context=None)
                if (hay_cliente==False):
                    continue

                name_pedido =''

                #tendremos que crear nuevo pedido si el documento = 8, o si es 0 albaran o 1 factura y no existe
                es_nuevo = 0
                #if ter_tipodoc == 0 or ter_tipodoc == 1:
                #    docs_reps = (['name','=',ter_numdoc])
                #    cambia_doc = pedido_obj.search(cr, uid, docs_reps)
                #    if (len(cambia_doc)>0):
                #        es_nuevo = 1

                if ter_tipodoc == 8 or (ter_tipodoc == 0 and es_nuevo == 0) or (ter_tipodoc == 1 and es_nuevo == 0):
                    #_logger.error('##### AIKO ###### En carga datos DOCS cumple tipo 8 o tipo 0 y 1 en nuevos docs')
                    values = {}    
                    #el pedido lo ponemos en estado enviado para luego lanzar el proceso de aceptacion de estos pedidos   
                    values['state'] = 'sent'
                    #si es un albaran ponemos order_policy = picking:
                    #if ter_tipodoc == 0:
                    #    values['order_policy'] = 'picking'
                    #modificado el criterio anterior el 10-3-16 pondremos manual para emitir facturas desde pedidos y no desde albaranes
                    values['order_policy'] = 'manual'
                    #cogemos la serie y el numero para identificar el pedido
                    name_pedido=''
                    #13-5-16 obviamos los pedidos que vengan con numero 0 de Tercap
                    if (ter_numdoc==0):
                        continue
                    relleno = int(tercapruta_obj.num_relleno)
                    #comprobamos si el documento tiene un numero de serie en line[3]
                    if (line[3]): 
                        if (ter_tipodoc == 0):#si es un albaran lo nombramos como AT albaran Tercap
                            name_pedido = 'AT-'+line[3]+line[0].zfill(relleno)
                        elif (ter_tipodoc == 1):#si es una factura primero creamos el pedido como tf factura Tercap
                            #13-7-16 usamos tf porque al comparar la cadena las minusculas tienen un Ascci mas alto, asi no hay problemas
                            #con las series que pueda estar usando Odoo en sus facturas y no da problemas de fechas al emitir la factura
                            name_pedido = 'tf-'+line[3]+line[0].zfill(relleno)
                        else:#si no sera un pedido lo creamos como PT pedido Tercap
                            name_pedido = 'PT-'+line[3]+line[0].zfill(relleno)
                    else:
                        if (ter_tipodoc == 0):#si es un albaran lo nombramos como AT albaran Tercap
                            name_pedido = 'AT-'+line[0].zfill(relleno)
                        elif (ter_tipodoc == 1):#si es una factura primero creamos el pedido como tf factura Tercap
                            name_pedido = 'tf-'+line[0].zfill(relleno)
                        else:#si no sera un pedido lo creamos como PT pedido Tercap
                            name_pedido = 'PT-'+line[0].zfill(relleno)
                    #CONTROL PARA NO RECIBIR UN PEDIDO CON NUMERO YA REGISTRADO
                    #12-5-16 pasamos a controlar esto en las lineas de tercap_import_document
                    #search_condition = [('name','=', name_pedido)]
                    #pedido_repetido = pedido_obj.search(cr, uid, search_condition)

                    #search_condition = [('numdocumento','=', line[0]),('codcliente','=', line[8]),('serie','=', line[3])]
                    #tercap_impdoc_obj = tercap_impdoc.search(cr,uid,search_condition)
                    #if (len(pedido_repetido)!=0):
                    #    msg_txt = 'El número de pedido de Tercap '+tercap_impdoc_obj[0]+' está repetido. No se puede realizar la importación de datos. Revise la configuración de la aplicación de Tercap y comunique la situación a soporte de Lider para rectificar el fichero de datos a importar'
                    #    raise osv.except_osv(('Error!'),(msg_txt))

                    #if (len(tercap_impdoc_obj)!=0):
                        #_logger.error('##### AIKO ###### En carga datos DOCS documento repetido:%s'%tercap_impdoc_obj[0])
                        #continue   

                    values ['name'] = name_pedido
                    #21-4-16 se modifica la forma en que se controla fecha prevista
                    #registramos como fecha del pedido la prevista de solicitud y asi en albaranes se traspasa 
                    #como fecha prevista de entrega y se filtran por aqui las entregas planificadas
                    #values['date_order'] = line[1] 
                    if (line[10]):
                        values['date_order'] = line[10]
                    else:
                        values['date_order'] = line[1]
                    #el id de la ruta de momento no lo tratamos
                    #codigoru = float(int(line[6]))
                    #ruta_obj = self.pool.get('tercap.route')
                    #search_condition = [('active', '=', True),('cod_tercap','=', codigoru)]
                    #ruta_selec_obj = ruta_obj.search(cr, uid, search_condition )            
                    #for ruta in ruta_selec_obj:
                    #    values['???_id'] = ruta
                    #    break

                    #el campo comercial lo vinculamos al equipo de ventas en section_id
                    search_condition = [('active', '=', True),('id','=', ter_codvend)]
                    eqvtas_selec_obj = eqvtas_obj.search(cr, uid, search_condition )            
                    for eqvtas in eqvtas_selec_obj:
                        values['section_id'] = eqvtas
                        #continue
                        #17-11-16 modificado para asociar el comercial al pedido
                        eqvtas_brw = eqvtas_obj.browse(cr, uid, eqvtas)
                        #_logger.error('##### AIKO ###### En carga datos DOCS se obtiene comercial:%s'%eqvtas_brw.user_id.id)
                        if eqvtas_brw.user_id:
                            values['user_id'] = eqvtas_brw.user_id.id

                    #24-2-16 desde esta fecha se agrega una opcion de busqueda en clientes
                    #para poder registrar pedidos de nuevos clientes
                    partner_condition = [('cod_tercap', '=', ter_codcliente)]
                    partner_obj_id = partner_obj.search(cr, uid, partner_condition)
                    if (len(partner_obj_id)>0):
                        id_partner = partner_obj.browse(cr, uid, partner_obj_id[0])
                        values['partner_id']= id_partner.id
                        #en este caso no podemos utilizar una direccion de facturacion por ser el cliente nuevo
                        #ni de entrega
                    else:
                        partner_condition = [('id', '=', ter_codcliente)]
                        partner_obj_id2 = partner_obj.search(cr, uid, partner_condition)
                        if (len(partner_obj_id2)>0):
                            id_partner = partner_obj.browse(cr, uid, partner_obj_id2[0])
                            values['partner_id']= ter_codcliente
                            #incluir direccion de facturacion segun marca de cliente (partner_invoice_id)
                            #para esto miramos si esta marcado en cliente la opcion factura_en_dir
                            #si no cumple no hace falta hacer nada: coge por defecto la principal
                            if(id_partner.factura_en_dir):
                                values['partner_invoice_id']=ter_direntrega
                            #incluir direccion de entrega (partner_shipping_id)
                            if (ter_direntrega!=0): values['partner_shipping_id'] = ter_direntrega
                    
                    #preparado para el caso que se quiera controlar fecha prevista
                    #como necesita del modulo sale_order_dates de momento queda comentado
                    #y desde el 21-4-16 se opta por utilizar otro camino, ver mas arriba
                    #if (line[10]):
                    #    values['requested_date'] = line[10] 
                    if (line[13]):
                        values['origin'] = line[13]
                    total_untaxed = ter_base1+ter_base2+ter_base3
                    values['amount_untaxed'] = total_untaxed
                    total_tax = ter_iva1+ter_iva2+ter_iva3+ter_recargo1+ter_recargo2+ter_recargo3
                    values['amount_tax'] = total_tax
                    #comprobamos si hay recargo de equivalencia para poner la posicion fiscal
                    if ((ter_recargo1+ter_recargo2+ter_recargo3) > 0):
                        search_condition = [('active', '=', True),('tercap_tipo_iva','=', 'R'),('company_id', '=', user.company_id.id)]
                        posicion_selec_obj = posicion_obj.search(cr, uid, search_condition )
                        if (len (posicion_selec_obj)==0):
                         raise osv.except_osv(('Error!'),('No se ha definido la posicion fiscal para clientes de Tercap. Revise la configuración'))

                        for posicion in posicion_selec_obj:
                            values['fiscal_position'] = posicion
                            continue
                    values['amount_total'] = ter_totaldoc

                    #la variable modo de pago la pasamos a la factura
                    pago=0
                    if (line[28]):
                        search_condition = [('active', '=', True),('id','=', ter_paytermid)]
                        pago_selec_obj = pago_obj.search(cr, uid, search_condition )            
                        for pago in pago_selec_obj:
                            #values['payment_term'] = pago
                            values['payment_mode_id'] = pago
                            continue
                    #para tratar el descuento por pronto pago si esta instalado el modulo
                    #sale-early_payment, comentado de momento hasta su uso: se pasa como un dto normal a la linea
                    #values['early_payment_discount']=ter_dtopp

                    #NOVEDAD 28-6-16: se cambia el valor de ruta_id para que no este vinculado al cliente
                    #o sea, el cliente puede tener una ruta y el pedido para reparto cambiarse a otra
                    #y damos valor para la ruta de reparto que aparece nueva
                    #de momento le asociamos la del cliente mientras Tercap no informe la ruta de reparto en el pedido
                    if id_partner.tercap_ruta_id:
                    	values['ruta_id']= id_partner.tercap_ruta_id.id

                    #30-6-16 nuevo campo para las rutas de reparto en el fichero de Tercap
                    if len(line)>30:
                        #localizamos la ruta por el valor de cod_tercap que es lo que se exporta como id de la ruta
                        if line[30]<>'':
                            search_condition=[('cod_tercap','=',line[30])]
                            reparto_src = reparto_obj.search(cr,uid,search_condition)
                            if len(reparto_src)>0:
                                values['reparto_id']= reparto_obj.browse(cr,uid,reparto_src[0]).id
                            else:
                            	if id_partner.tercap_ruta_id:
                            		values['reparto_id']= id_partner.tercap_ruta_id.id

                    #_logger.error('##### AIKO ###### En carga datos DOCS se obtiene la lista de valores:%s'%values)
                    order_id = pedido_obj.create(cr,SUPERUSER_ID,values,context=None)

                    # a continuacion con este id habría que cargar las las lineas del pedido
                    #cambiamos el fichero para coger el de lineas
                    ficlineas = 'DOCLIN'+f.name [6:]
                    #tenemos que pasar en la funcion el descuento de cabecera para ponerlo en lineas
                    #16-5-16 por si el campo de descuento se pasa tambien dtopp:
                    #01-08-16 tenemos que pasar el id_cliente por si hay que registrar un precio de promocion
                    tiene_lineas = carga_datos_lineas(self, cr, uid, values['partner_id'], ter_numdoc, ter_tipodoc, order_id, ruta, ficlineas,ter_dto,ter_dtopp,name_pedido, ter_direntrega, context=None)
                    #_logger.error('##### AIKO ###### En carga datos DOCS tiene_lineas con valor %s'%tiene_lineas)
                    #01-08-16 si tiene lineas nos comunico nueva tarifa no podemos cargar el fichero hasta que exista la tarifa
                    if (tiene_lineas == 99):
                        #no se pueden registrar precios si la tarifa no esta creada: habria que leer primero el fichero
                        #solo para ver las tarifas que seria necesario crear, cerrarlo y volver a abrirlo para cargar el pedido
                        part_name = partner_obj.browse(cr, uid, values['partner_id']).name
                        #_logger.error('##### AIKO ###### En carga datos DOCS asociar tarifa a cliente %s'%part_name)
                        msg_txt = 'Tiene que crear antes la tarifa para el cliente '+part_name+'. No se puede cargar el fichero'
                        raise osv.except_osv(('Error!'),(msg_txt))
                        #POR HACER: crear la tarifa para el cliente si es que no existe una.

                    if (tiene_lineas == 1):
                        _logger.error('##### AIKO ###### En carga datos DOCS pedido con lineas de abono %s'%ter_numdoc)
                        #POR HACER: crear un albaran de entrada de las lineas de abono (v. retornar_pedido)


                    #13-5-16 si no encuentra lineas sigue al siguiente pedido:
                    if (tiene_lineas==0):
                        _logger.error('##### AIKO ###### En carga datos DOCS no se encuentran lineas')
                        continue
                    #por ultimo damos por confirmado el pedido:
                    #3-5-16 si esta marcado en el directorio de importacion
                    if (tercapruta_obj.pedido_borrador==False):
                        retconf = self.pool.get('sale.order').action_button_confirm(cr, uid, order_id, context=context)
                        #_logger.error('##### AIKO ###### En carga datos DOCS al confirmar se obtiene %s'%retconf)
                        #3-5-16 buscamos el albaran generado y reescribimos su numero para que sea igual que el del pedido
                        #siempre que este asi marcado en el directorio de importacion
                        if (retconf and tercapruta_obj.unico_numero):
                            renumerar_albaran (self, cr, uid, name_pedido, context=None)
                    #seguimos para albaranes nuevos además cogemos el name_pedido para buscar el picking asociado y darle salida
                    if (ter_tipodoc == 0 or ter_tipodoc == 1) and not tercapruta_obj.todo_pedidos and not tercapruta_obj.pedido_borrador:
                        albaranar_pedido (self, cr, uid, name_pedido, context=None)

                    #1-3-16 gestionamos cobros en pedidos o albaranes, para eso tenemos que crear un objeto pay.sale.order
                    if (ter_tipodoc != 1 and ter_cobrado>0):
                        #22-3-16 localizado problema con decimales en albaranes (pedidos)
                        #al ser un campo calculado no tenemos forma de reescribirlo
                        #pero al menos si esta pagado entero dejamos el pendiente a cero para que no queden pendiente 1 centimo
                        if (ter_cobrado == ter_totaldoc):
                            #buscamos el pendiente del pedido y pasamos el valor del pendiente
                            pte_pedido = pedido_obj.browse (cr, uid, order_id).residual
                            #_logger.error('##### AIKO ###### En registro de pago se pasa el pendiente total: %s'%pte_pedido)
                            registrar_cobro (self, cr, uid, ter_numdoc, pte_pedido, journal_obj_id, order_id, 'False', context=None)
                        else:
                            registrar_cobro (self, cr, uid, ter_numdoc, ter_cobrado, journal_obj_id, order_id, 'False', context=None)
                    #y seguimos para facturas: tendremos el albaran y hay que facturarlo
                    if (ter_tipodoc == 1) and not tercapruta_obj.todo_pedidos and not tercapruta_obj.pedido_borrador:
                        #_logger.error('##### AIKO ###### En carga datos DOCS entro en emision de factura para el pedido: %s'%order_id)
                        if (line[3]): 
                            numfactura = 'tf-'+unicode(line[3])+unicode(line[0]).zfill(relleno)
                        else:
                            numfactura = 'tf-'+unicode(line[0]).zfill(relleno)
                        #pasamos el dato de cobro, por si es necesario registrar un pago
                        genera_factura(self, cr, uid, order_id, ter_dateorder, numfactura, ter_cobrado, ter_totaldoc, pago, context=None)
                    

        f.close()
    return True
        
def sube_datos_lineas(self, cr, uid, ids, ruta, file, context=None):
    my_obj = self.pool.get('tercap.import.lines')
    os.chdir(ruta)
    #_logger.error('##### AIKO ###### Valor de f.name recibido:%s'%file)
    #_logger.error('##### AIKO ###### Valor de ruta recibido:%s'%ruta)
    for nombre in glob.glob(file):
        f = open(nombre,'rU')
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        c = csv.reader(f, delimiter=";", skipinitialspace=True)

        #_logger.error('##### AIKO ###### Abierto fichero:%s'%file)
        for line in c:
            if line:
                ref = fields.datetime.now()
                values = {
                    'name': ref,
                    'numdocumento': line[0],
                    'fechadocumento': line[1],
                    'tipodocumento': line[2],
                    'numlinea': line[3],
                    'tipolinea': line[4],
                    'codproducto': line[5],
                    'descripcion': ustr(line[6]),
                    'unidadventa': line[7],
                    'lote': ustr(line[8]),
                    'cantidad': line[9],
                    'cajas': line[10],
                    'pesounidad': line[11],
                    'pesototal': line[12],
                    'precio': line[13],
                    'descuento1': line[14],
                    'descuento2': line[15],
                    'precioneto': line[16],
                    'preciomanual': line[17],
                    'iva': line[18],
                    'recargo': line[19],
                    'importeiva': line[20],
                    'importerecargo': line[21],
                    'codprovalternativo': line[22],
                    'tipodescuento1': line[23],
                    'tipodescuento2': line[24],
                    'preciocoste': line[25],
                }
                #_logger.error('##### AIKO ###### Estos valores a registrar:%s'%values)
                newline_id = my_obj.create(cr, SUPERUSER_ID, values, context=None)
                    
        f.close()
        
def carga_datos_lineas(self, cr, uid, partner_id, numdoc, tipodoc, order_id, ruta, file, dto_cab, dto_pp, name_pedido, ter_direntrega, context=None):
    #posicion_obj = self.pool.get('account.fiscal.position')
    uom_obj = self.pool.get('product.uom')
    product_obj = self.pool.get('product.product')
    tax_obj = self.pool.get('account.tax')
    pedido_obj = self.pool.get('sale.order.line')
    properties = self.pool.get('ir.property')
    res_clientes = self.pool.get('res.partner')
    product_lists = self.pool.get('product.pricelist')
    version_obj = self.pool.get('product.pricelist.version')
    price_item = self.pool.get('product.pricelist.item')

    user = self.pool['res.users'].browse(cr, uid, uid)

    #9-9-16: localizamos el directorio y como tiene definido el valor de product_default_idcode
    directory_obj = self.pool.get('tercap.route').browse (cr,uid,1)
    codigo_default = directory_obj.product_default_idcode

    #11-11-16: para incluir tratamiento de lotes que se comunican desde Tercap
    #necesitamos el objeto stock_production_lot para localizar el lote con ese nombre para el producto
    lote_obj = self.pool.get('stock.production.lot')
    
    os.chdir(ruta)
    for nombre in glob.glob(file):
        fln = open(nombre,'rU')
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        cln = csv.reader(fln, delimiter=";", skipinitialspace=True)

        res = -99
        for lines in cln:
            if lines:
                #lines [0] = NumDocumento
                #lines [1] = FechaDocumento; se utiliza la de cabecera
                #lines [2] = TipoDocumento
                #lines [3] = NumLinea
                #lines [4] = TipoLinea: 1=venta, 2=regalo, 4=retirada mercancia
                #
                #lines [5] = CodProducto; este no se usa, es uno interno de Tercap
                #modificado el 9-9-16: ahora puede contener el identificador del producto
                #lines [5] = CodProducto: puede ser el id en Odoo del producto

                #lines [6] = Descripcion
                #lines [7] = Unidad Venta (U, Kg, C)
                #lines [8] = Lote
                #lines [9] = Cantidad
                #lines [10] = Cajas
                #lines [11] = Peso Unidad; no se trata
                #lines [12] = Peso Total ... valor para unidad si Ud. Venta es Kg
                #lines [13] = Precio Bruto por unidad de producto
                #lines [14] = Descuento1
                #lines [15] = Descuento2
                #lines [16] = Precio neto Unitario tras descuentos
                #lines [17] = Indica si el precio esta fijado manualmente
                #lines [18] = Tipo de IVA aplicable a la linea
                #lines [19] = Tipo de Recargo aplicable a la linea
                #lines [20] = Importe del IVA de la linea
                #lines [21] = Importe del Recargo de la linea
                #
                #lines [22] = CodProducto Alternativo: es el id en Odoo del producto
                #modificado el 9-9-16: ahora pasa a estar en el campo 5
                #lines [22] = CodProducto Alternativo: es el default code en su caso

                #lines [23] = Tipo Dto1 : vacío o %
                #lines [24] = Tipo Dto2: vacío, % o P (euros)
                #lines [25] = Precio coste; no se trata
                #novedad 1/8/16 para controlar los precios que es necesario actualizar en Odoo
                #lines [26] = EsPrecioVendedor: S indica nuevo precio, N omitir


                #_logger.error('##### AIKO ###### En carga datos LINEAS valor de order_id:%s'%order_id)
                #_logger.error('##### AIKO ###### En carga datos LINEAS valor lines[0]:%s'%float(int(lines[0])))
                #antes de tratar datos pasamos las cadenas numericas a valores
                ter_numdoc = int(float(lines[0]))if lines[0] else  ' '
                ter_tipodoclin = int(float(lines[2]))if lines[2] else  ' '
                ter_numlinea = int(float(lines[3]))if lines[3] else  '10'
                ter_tipolinea = int(float(lines[4]))if lines[4] else  '1'
                #21-31-16 el id nos llega ahora en CodProvAlternativo: campo 22
                #ter_codproducto = int(float(lines[5]))if lines[5] else  '0'
                #_logger.error('##### AIKO ###### En carga datos LINEAS valor para descripcion:%s'%lines[6])
                ter_descripcion = ustr(lines[6]) if lines[6] else  'Sin descripcion'
                #modificacion del 9-9-16: el codigo pasa a estar en el campo 5 y en el 22 recibiremos el Default Codigo
                #si asi se desmarca en el directorio, si se deja en True, se mantiene al reves
                if codigo_default:
                    ter_codproducto = int(float(lines[22]))if lines[22] else  '0'
                else:
                    ter_codproducto = int(float(lines[5]))if lines[5] else  '0'
                #11-11-16: incluir tratamiento de lotes que se comunican desde Tercap
                #buscar en stock_production_lot para el producto el lote con ese nombre
                #e incluirlo en la linea de venta en el campo lot_id, suponemos que no se repite el nombre de lote
                ter_lote = ustr(lines[8]) if lines[8] else  '0'

                ter_cantidad = float(lines[9])if lines[9] else  '0'
                ter_cajas = int(float(lines[10]))if lines[10] else  '0'
                ter_kilos = int(float(lines[12]))if lines[12] else  '0'
                ter_precioud = float(lines[13])if lines[13] else  '0'
                ter_dto1 = float(lines[14])if lines[14] else  '0'
                ter_dto2 = float(lines[15])if lines[15] else  '0'
                #vamos a usar el precio neto para hacer sumatorio del pedido para el pronto pago
                ter_precioneto = float(lines[16])if lines[16] else  '0'
                ter_tpiva = float(lines[18])if lines[18] else  '0'
                ter_tprecargo = float(lines[19])if lines[19] else  '0'
                #_logger.error('##### AIKO ###### Comprobando valores NumDocLinea:%s'%ter_numdoc)
                #_logger.error('##### AIKO ###### Comprobando valores NumDocRecibido:%s'%numdoc)

                #tenemos que filtrar por numero de documento y tipo de documento igual que el de origen
                if ter_tipodoclin == tipodoc and ter_numdoc == numdoc:
                    _logger.error('##### AIKO ###### En carga datos LINEAS registro linea coincidentes: %s'%numdoc)
                    
                    values = {}
                    #el pedido lo ponemos en estado borrador para luego lanzar el proceso de aceptacion de estos pedidos
                    #las lineas no tienen estado sent, asi que dejamos draft   
                    values['state'] = 'draft'
                    values['invoiced'] = 0
                    #cogemos el order_id que nos pasa la funcion para identificar el pedido
                    values['order_id'] = order_id
                    values['sequence'] = ter_numlinea

                    #buscamos el tipo de iva para usarlo mas adelante
                    tax_condition = [('amount','=',(ter_tpiva/100)),('tercap_codiva','!=','0')]
                    tax_obj_id = tax_obj.search(cr, uid,tax_condition)
                    #si no hay coincidentes mensaje para configurar impuestos
                    if (len (tax_obj_id)==0):
                        msg_txt = 'IVA: No se ha definido el tipo de impuesto en Tercap para el valor '+ter_tpiva/100+'. Revise la configuración de impuestos'
                        raise osv.except_osv(('Error!'),(msg_txt))
                        #raise osv.except_osv(('Error!'),('Iva Normal: No se han definido todos los tipos de impuesto para la aplicación de Tercap. Revise la configuración de impuestos'))

                    if (ter_codproducto!=0):
                        #_logger.error('##### AIKO ###### En carga datos LINEAS busco id producto: %s'%ter_codproducto)
                        search_condition = [('id', '=', ter_codproducto)]
                        idprod = product_obj.search(cr, uid, search_condition)
                        if (len (idprod)==0):
                            msg_txt = 'Se ha producido una excepción de producto. El producto '+ter_descripcion+' parece que no existe en Odoo.'
                            raise osv.except_osv(('Error!'),(msg_txt))
                            #raise osv.except_osv(('Error!'),('Se ha producido una excepción de producto no esperada. Contacte con el servicio de soporte de Odoo.'))

                        caja_prod = product_obj.browse(cr, uid, idprod)

                        #tenemos que prevenir las devoluciones con unidades en negativo
                        #si es negativo no usamos el product_id, solo descripcion modificada
                        if (ter_cantidad<0):
                            values['name'] = 'Devolucion de '+ ter_descripcion 
                        else:
                            values['product_id'] = ter_codproducto
                            if (caja_prod.default_code): 
                                values['name'] = '['+caja_prod.default_code+'] '+ ter_descripcion
                            else:
                                values['name'] = ter_descripcion

                        #para determinar la unidad de medida hay que comprobar si hay cifra de cajas significativa
                        #10-6-16 salvo si marcamos que solo se use unidad de medida Unidades
                        inv_names = self.pool.get('tercap.route').browse (cr,uid,1)
                        valor_uom_id = 0
                        '''
                        #28-4-16 para saber si son cajas, unidades o kilos ahora usamos el campo lines[7] C, U, KG
                        if (inv_names.solo_unidades):
                            search_condition = [('tercap_unit', '=', 'U')]
                        else:
                            search_condition = [('tercap_unit', '=', lines[7])]
                        uom_id = uom_obj.search(cr, uid, search_condition)
                        if (len (uom_id)==0):
                             raise osv.except_osv(('Error!'),('No se han definido todas las unidades de medida para la aplicación de Tercap. Revise la configuración'))

                        categ_uom = uom_obj.browse(cr, uid, uom_id[0])
                        '''
                        #cambio del 21-07-16 cogemos la categoria de la uom que tiene registrada el producto en Odoo
                        if (inv_names.solo_unidades):
                            search_condition = [('tercap_unit', '=', 'U')]
                        else:
                            search_condition = [('id', '=', caja_prod.uom_id.id)]
                        uom_id = uom_obj.search(cr, uid, search_condition)
                        if (len (uom_id)==0):
                            raise osv.except_osv(('Error!'),('No se han definido todas las unidades de medida para la aplicación de Tercap. Revise la configuración'))

                        categ_uom = uom_obj.browse(cr, uid, uom_id[0])
                        factor_caja = 0

                        if (lines[7]=='C'):
                            factor_caja = (ter_cajas/ter_cantidad)
                            factor_condition = [('category_id', '=', categ_uom.category_id.id),('factor','=',factor_caja)]
                            caja_id = uom_obj.search(cr, uid, factor_condition)
                            if (len(caja_id)>0):
                                values['product_uom'] = caja_id[0]
                                valor_uom_id = caja_id[0]
                                #21-9-16 pero tenemos que tener en cuenta la ud de medida para poner bien el precio de coste
                                #el precio de coste standard_price viene en la ud. de venta del producto
                                values['purchase_price'] = caja_prod.standard_price*1/factor_caja
                            else:
                                raise osv.except_osv(('Error!'),('No se ha definido una unidad de medida compuesta (uds x caja) en Odoo. Cree la unidad para un factor %s'%factor_caja))
                        else:
                            #28-4-16 si no son cajas cogemos el uom_id del producto en cuestion
                            values['product_uom'] = caja_prod.uom_id.id
                            valor_uom_id = caja_prod.uom_id.id
                            values['purchase_price'] = caja_prod.standard_price

                        #10-6-16 en todo caso si marcamos que solo se use unidad de medida Unidades
                        
                        if (inv_names.solo_unidades):
                            values['product_uom'] = caja_prod.uom_id.id
                            valor_uom_id = caja_prod.uom_id.id
                            values['purchase_price'] = caja_prod.standard_price

                        #si la venta viene en cajas usamos el valor de tercap_unidadescaja
                        #if (ter_cajas!=ter_cantidad and ter_tipolinea!=4):
                        #if (ter_cajas!=ter_cantidad):
                        if (lines[7]=='C'):
                            values['product_uom_qty']= ter_cajas
                        #elif (ter_cajas!=ter_cantidad and ter_tipolinea==4):
                        #    values['product_uom_qty'] = ter_cajas*(-1)
                        else:
                            #si son Kg como unidades cogemos el peso total, si son unidades, las unidades
                            #esto lo paramos hasta ver como llega un archivo con kilos
                            if (lines[7]=='KG'):
                                #values['product_uom_qty'] = ter_kilos
                                values['product_uom_qty'] = ter_cantidad
                            else:
                                values['product_uom_qty'] = ter_cantidad

                        #los precios tenemos que distinguir si se trabaja con IVA incluido
                        #para controlar el tipo de iva del producto
                        search_condition = [('id', '=', caja_prod.taxes_id.id)]
                        tpiva = tax_obj.search(cr, uid, search_condition)
                        if (len (tpiva)==0):
                         raise osv.except_osv(('Error!'),('Ficha Producto: No se ha definido el impuesto en todos los productos de uso en la aplicación de Tercap. Revise la configuración de productos'))

                        tipoimp = tax_obj.browse(cr, uid, tpiva[0])
                        #si los precios son con iva descontamos el tipo de iva
                        if (tipoimp.price_include):
                            #hay que tener en cuenta si la venta es en unidades o en cajas
                            #28-4-16 la identificacion por lines[7]
                            if(lines[7]=='C'):
                                values['price_unit'] = (ter_precioud * ter_cantidad / ter_cajas) / (1 + tipoimp.amount)
                            else:
                                values['price_unit'] = ter_precioud / (1 + tipoimp.amount)
                        else:
                            #hay que tener en cuenta si la venta es en unidades o en cajas
                            #28-4-16 la identificacion por lines[7]
                            if(lines[7]=='C'):
                                #_logger.error('##### AIKO ###### En carga datos LINEAS entro en price unit para cajas:%s'%(ter_precioud * ter_cantidad / ter_cajas))
                                values['price_unit'] = ter_precioud * ter_cantidad / ter_cajas
                            else:
                                values['price_unit'] = ter_precioud
                        #para registrar el iva asociado le pasamos el valor tax_obj_id anterior
                        #tenemos que comprobar si hay recargo de equivalencia
                        if (ter_tprecargo==0):
                            values['tax_id']=[(6, 0, tax_obj_id)]
                        else:
                            #si hay valor tenemos que buscar el id y crear un array con los dos ivas
                            tax_condition = [('amount','=',(ter_tprecargo/100)),('tercap_codiva','!=','0')]
                            tax_rec_id = tax_obj.search(cr, uid, tax_condition)
                            if (len (tax_rec_id)==0):
                                raise osv.except_osv(('Error!'),('Iva Recargo: No se han definido todos los tipos de impuesto para la aplicación de Tercap. Revise la configuración de impuestos'))

                            taxes =[tax_obj_id[0],tax_rec_id[0]]
                            values['tax_id']=[(6, 0, taxes)]

                        #tratamiento de descuentos es primero aplicar dto1 en porcentaje
                        #y luego dto2 en porcentaje o en cantidad sobre precio
                        #16-5-16 cambiamos la formula para calcular los descuentos y no usamos discount2
                        if (ter_dto2!=0):
                            if (lines[24]=='P'):
                                #si el descuento es en euros calculamos el porcentaje que representa
                                ter_dto2 = ter_dto2/ter_precioud*100
                        discount_factor = 1.0
                        for discount in [ter_dto1, ter_dto2, dto_cab, dto_pp]:
                            discount_factor = discount_factor * ((100.0 - discount) / 100.0)
                        values['discount'] = 100.0 - (discount_factor * 100.0)
                        values['discount1'] = values['discount']
                        #30-6-16 hay otro caso: el tipo de linea de regalo, que no recoge un dto del 100
                        if (ter_tipolinea==2):
                            values['discount'] = 100.0
                            values['discount1'] = values['discount']

                        #21-3-16 si hay lineas de devolucion ponemos res a 1
                        if (ter_tipolinea==4):
                            res = 1
                        #29-4-16 tenemos que registrar tb el product_uos_qty igual al product_uom_qty
                        values['product_uos_qty'] = values['product_uom_qty']

                        #11-11-16: incluir tratamiento de lotes que se comunican desde Tercap
                        #buscar en stock_production_lot para el producto el lote con ese nombre
                        #e incluirlo en la linea de venta en el campo lot_id
                        new_lote_id = 0
                        #si Tercap envía 0 en el campo lote, creamos un lote '0000' y usamos ese lote
                        _logger.error('##### AIKO ###### En carga datos LINEAS valor ter_lote %s'%ter_lote)
                        if int(ter_lote)==0:
                            _logger.error('##### AIKO ###### En carga datos LINEAS valor sin lote fijado %s'%ter_lote)
                            ter_lote = '0000'
                        
                        search_condition = [('product_id', '=', ter_codproducto),('name', 'ilike', ter_lote)]
                        lote_id = lote_obj.search(cr, uid, search_condition)
                        if len(lote_id)==0:
                            _logger.error('##### AIKO ###### En carga datos LINEAS no se encuentra lote_id para %s'%ter_lote)
                            _logger.error('##### AIKO ###### En carga datos LINEAS no se encuentra product_id %s'%ter_codproducto)
                            #hay que crear un lote para el producto con el nombre recibido
                            new_lote_id = crear_lote (self, cr, uid, ter_codproducto, ter_lote, context=None)
                            
                        if (new_lote_id==0) :
                            values['lot_id'] = lote_id[0]
                        else:
                            values['lot_id'] = new_lote_id
                        _logger.error('##### AIKO ###### En carga datos LINEAS valor lote_id %s'%values['lot_id'])

                        #01/08/16 puede venir nuevo valor con la ruta de reparto
                        if len(lines)>26:
                            if lines[26]!='N':#si vale N no hay que registrar nada
                                #buscamos un price_surcharge ya registrado y activo para este cliente y producto
                                #lo primero localizar la tarifa para ese id cliente en ir_property
                                search_condition=[('name','=','property_product_pricelist'),('res_id','like',partner_id)]
                                prop_pricelist = properties.search (cr, uid, search_condition)
                                #variable para saber si se encuentra alguna version de tarifa activa o no
                                #dos valores posibles -1=no hay tarifa de cliente o no esta vigente, 0= hay tarifa vigente
                                active_version = -1

                                if len(prop_pricelist) !=0:
                                    
                                    for pl in prop_pricelist:
                                        #el campo value_reference contiene el id de la tarifa aplicable para este cliente tras la coma
                                        text_pricelist = properties.browse(cr,uid,pl).value_reference
                                        price_coma = text_pricelist.find(',')+1
                                        text_pricelist = text_pricelist[price_coma:]
                                        text_pricelist = int(text_pricelist)
                                        #con el dato del product_pricelist buscamos el product_pricelist_version_id
                                        search_condition = [('pricelist_id','=',text_pricelist)]
                                        version_obj_sr = version_obj.search(cr,uid,search_condition)
                                        for version in version_obj_sr:
                                            #obtenemos el date_start y date_end de la version
                                            version_obj_dates = version_obj.browse(cr,uid,version)
                                            if version_obj_dates.date_start:
                                                desdef = datetime.strptime(version_obj_dates.date_start, '%Y-%m-%d')
                                            else:
                                                desdef = datetime.now()
                                            hoy = datetime.now()
                                            if version_obj_dates.date_end:
                                                hastaf = datetime.strptime(version_obj_dates.date_end, '%Y-%m-%d')
                                            else:
                                                hastaf = datetime.now()
                                            #_logger.error('##### AIKO ###### En carga datos LINEAS valor desdef %s'%desdef)
                                            #_logger.error('##### AIKO ###### En carga datos LINEAS valor hastaf %s'%hastaf)
                                            #_logger.error('##### AIKO ###### En carga datos LINEAS valor hoy %s'%hoy)
                                            if desdef <= hoy and hastaf >= hoy:
                                                #recogemos que al menos una version esta activa
                                                active_version = 0
                                                #buscamos ahora en items con el id de la version y el id del producto y con price_surcharge
                                                search_condition = [('price_version_id','=',version),('product_id','=',ter_codproducto)]
                                                #_logger.error('##### AIKO ###### En carga datos LINEAS condicion de precio con valores %s'%search_condition)
                                                price_item_obj = price_item.search(cr,uid,search_condition)
                                                #nos queda el caso de que no hay un valor y tenemos que registrar un nuevo precio de promocion
                                                if len(price_item_obj)==0:
                                                    #_logger.error('##### AIKO ###### En carga datos LINEAS encontrado promocion para registrar nuevo precio CON TARIFA')
                                                    #caso A: existe una version de tarifa vigente para el cliente
                                                    crear_item_tarifa (self, cr, uid, version, ter_codproducto, ter_precioneto, context=None)
                                                else:
                                                    for prices in price_item_obj:
                                                        #_logger.error('##### AIKO ###### En carga datos LINEAS encontrado promocion para modificar:%s'%prices)
                                                        #editamos el valor de esta fila para registrar el nuevo precio neto como precio promocion
                                                        #y anulamos cualquier otra referencia de descuento, cantidad minima, margenes, etc.
                                                        valsitem={}
                                                        valsitem['price_surcharge'] = ter_precioneto
                                                        valsitem['price_discount'] = -1.0
                                                        valsitem['price_round'] = 0
                                                        valsitem['price_min_margin'] = 0
                                                        valsitem['price_max_margin'] = 0
                                                        valsitem['min_quantity'] = 0
                                                        price_item.write(cr,uid,prices,valsitem,context=context)
                                    
                                if active_version == -1:
                                    #si llegamos aqui con valor -1, no hay version activa para este cliente
                                    #caso B-1: no existe ninguna version de tarifa para el cliente
                                    #caso B-2: no existe una version de tarifa vigente para el cliente

                                    #tanto en un caso como en otro, no es posible registrar un precio nuevo sin tarifa
                                    res = 99
                    else:
                        msg_txt = 'Error de producto: Una linea del pedido '+numdoc+' contiene un producto no codificado. No se puede realizar la importación del fichero. Modifique el pedido en Tercap.'
                        raise osv.except_osv(('Error!'),(msg_txt))
  
                    _logger.error('##### AIKO ###### En carga datos LINEAS se obtiene la lista de valores:%s'%values)
                    _logger.error('##### AIKO ###### En carga datos LINEAS el valor de res es:%s'%res)
                    pedido_obj_id = pedido_obj.create(cr,SUPERUSER_ID,values,context=None) 

                    #21-3-16 la linea es de tipo 4 (devoluciones) tenemos que generar un movimiento de almacen de esas unidades
                    #tenemos que pasar en la funcion el product_id, su nombre para identificar el movimiento, el product_uom_qty y el product_uom (ud o kg)  
                    #15-9-16: esto no podemos hacerlo aqui, genera un albaran por cada linea y si hay dos se duplica la referencia
                    #if (ter_cantidad < 0):
                    #    qty_devol = ter_cantidad * (-1)
                    #    retornar_pedido (self, cr, uid, ter_codproducto, ter_descripcion, qty_devol, valor_uom_id, name_pedido, ter_direntrega, context=None)     
                else:
                    #si no coinciden los datos de una linea la despreciamos y seguimos leyendo el fichero
                    continue
                    #res = 0
            else:
                #_logger.error('##### AIKO ###### En carga datos LINEAS ponemos res a 0 porque no hay lineas en el fichero')
                res = 0
        fln.close()
    #21-3-16 si devolvemos res = 0 no hay lineas o no coincide el num.pedido, si hay lineas de devolucion devolvemos 1, si hay nueva tarifa su id, si no devolvemos -99
    #_logger.error('##### AIKO ###### En carga datos LINEAS salimos con valor de res:%s'%res)
    return res

 
def desmarca_inv_lines (self, cr, uid, sale_id, context=None):
    ids = []
    ids.append (sale_id)
    #_logger.error('##### AIKO ###### Desmarca_inv_lines envia el dato de sale order %s'%ids)

    sale_obj = self.pool.get('sale.order')
    sale_line_obj = self.pool.get('sale.order.line')

    for id in ids:
        search_condition = [('order_id','=',id)]
        sale_line_obj_id = sale_line_obj.search(cr,uid,search_condition)
        #_logger.error('##### AIKO ###### Desmarca_inv_lines entra en las lineas %s'%sale_line_obj_id)
        if len(sale_line_obj_id)>0:
            for line in sale_line_obj_id:
                valor_lineas = sale_line_obj.browse(cr,uid,line).sequence
                #_logger.error('##### AIKO ###### Desmarca_inv_lines invoiced false en la secuencia %s'%valor_lineas)
            sale_line_obj.write(cr, uid, sale_line_obj_id, {'invoiced':0}, context=None)

def albaranar_pedido (self, cr, uid, name_pedido, context=None):
    picking_obj = self.pool.get('stock.picking')
    search_condition = [('origin', '=', name_pedido)]
    #_logger.error('##### AIKO ###### Buscando el albaran de facturacion de la orden:%s'%name_pedido)
    picking_obj_id = picking_obj.search(cr, uid, search_condition)
    if (len(picking_obj_id)!=0):   
        picking_obj.force_assign(cr, uid, picking_obj_id, context=None)
        picking_obj.do_enter_transfer_details(cr, uid, picking_obj_id, context=None)
        picking_obj.action_done(cr, uid, picking_obj_id, context=None)
    #else:
        #_logger.error('##### AIKO ###### No se encuentra en stock.picking el origen:%s'%name_pedido)

def renumerar_albaran (self, cr, uid, name_pedido, context=None):
    picking_obj = self.pool.get('stock.picking')
    search_condition = [('origin', '=', name_pedido)]
    #_logger.error('##### AIKO ###### Buscando renumerar albaran de facturacion de la orden:%s'%name_pedido)
    picking_obj_id = picking_obj.search(cr, uid, search_condition)
    if (len(picking_obj_id)!=0):   
        picking_obj.write(cr, uid, picking_obj_id, {'name':name_pedido},context=None)
    else:
        _logger.error('##### AIKO ###### No se encuentra en stock.picking el origen:%s'%name_pedido)


def retornar_pedido (self, cr, uid, ter_codproducto, ter_descripcion, qty_devol, valor_uom_id, name_pedido, ter_direntrega, context=None):
    #21-3-16 esta funcion para registrar entrada en almacen de productos devueltos
    #necesitamos designar un almacen de salida y otro de destino de los existentes
    whare_obj = self.pool.get('stock.location')
    #para el origen buscamos la location con usage = customer
    search_condition =[('usage','=','customer')]
    whare_obj_cust = whare_obj.search (cr, uid, search_condition)
    if len(whare_obj_cust)==0:
        raise osv.except_osv(('Error!'),('No se ha definido un almacén para clientes. Revise la configuración de almacenes'))
    #para destino utilizamos el de stock de la empresa
    search_condition =[('name','ilike','stock')]
    whare_obj_dest = whare_obj.search (cr, uid, search_condition)
    if len(whare_obj_dest)==0:
        raise osv.except_osv(('Error!'),('No se ha definido un almacén de STOCK. Revise la configuración de almacenes'))
    move_obj = self.pool.get('stock.move')
    #buscamos un tipo de movimiento de entrada en almacen
    picking_type_obj = self.pool.get('stock.picking.type')
    search_condition =[('code','like','incoming'),('default_location_dest_id','=',whare_obj_cust[0])]
    picking_type_id = picking_type_obj.search (cr, uid, search_condition)
    if len(picking_type_id)==0:
        raise osv.except_osv(('Error!'),('No se ha definido un almacén para recepción de mercancía. Revise la configuración de almacenes'))
    values = {}
    values ['product_id'] = ter_codproducto
    values ['product_uom_qty'] = qty_devol
    values ['product_uos_qty'] = qty_devol
    values ['product_uom'] = valor_uom_id
    values ['product_uos'] = valor_uom_id
    values ['location_id'] = whare_obj_cust[0]
    values ['location_dest_id'] = whare_obj_dest[0]
    values ['picking_type_id'] = picking_type_id[0]
    values ['name'] = 'Devolucion '+ter_descripcion
    values ['origin'] = name_pedido
    values ['partner_id'] =  ter_direntrega

    #creamos el stock-move
    move_obj_id = move_obj.create (cr,SUPERUSER_ID,values,context=None) 
    #_logger.error('##### AIKO ###### En retornar pedido creado nuevo movimiento de stock:%s'%move_obj_id)
    #una vez creado ejecutamos action_done
    retpedido = move_obj.action_done(cr, uid, move_obj_id, context=context)
    #_logger.error('##### AIKO ###### No se encuentra en stock.picking el origen:%s'%name_pedido)


def registrar_cobro (self, cr, uid, ter_numdoc, ter_cobrado, journal_obj_id, order_id, date_pay, context=None):
    pay_obj = self.pool.get('pay.sale.order')
    valpagos={}
    #_logger.error('##### AIKO ###### En registrar cobro encuentro pago en pedido:%s'%ter_numdoc)
    valpagos['amount'] = ter_cobrado
    if date_pay!='False':
        valpagos['date']= date_pay
    else:
        valpagos['date']= fields.datetime.now()
    #23-3-16 no pasamos valor description para que tome el numero de asiento que toque
    #valpagos['description'] = 'Cobro Tercap de documento '+ str(ter_numdoc)
    nuevo_pago = pay_obj.create(cr,SUPERUSER_ID,valpagos,context=None)
    if (nuevo_pago):
        #_logger.error('##### AIKO ###### En registrar cobro se ha registrado un cobro con id:%s'%nuevo_pago)
        pago_id = pay_obj.browse(cr, uid, nuevo_pago, context=None)
        pago_id.pay_sale_orderid(order_id, journal_obj_id)

def registrar_cobro_factura (self, cr, uid, acc_invoice_id, ter_cobrado, ter_pendiente, context=None):
    acc_invoice = self.pool.get ('account.invoice')
    voucher_obj = self.pool.get('account.voucher')
    conciliar = 0

    if ter_pendiente==0:
        acc_inv_sel = acc_invoice.browse(cr, uid, acc_invoice_id)
        cobro = acc_inv_sel.residual
    else:
        cobro = ter_cobrado
    #si el residual de la factura queda a cero, marcamos la factura para no volver a asociar pagos de sus pedidos
    if (acc_inv_sel.residual-cobro)==0:
        conciliar = 1
    new_voucher_id = voucher.crea_voucher(self, cr, uid, acc_invoice_id, cobro, context=context)
    #registramos las lineas de ese recibo
    voucher.crea_lineas_voucher(self, cr, uid, acc_invoice_id, cobro, new_voucher_id, context=context)
    #con el nuevo voucher creado registramos el pago de la factura
    voucher_obj.button_proforma_voucher(cr, uid, [new_voucher_id], context=context)
    #si el residual de la factura queda a cero, marcamos la factura para no volver a asociar pagos de sus pedidos
    if conciliar==1:
        acc_invoice.write(cr, uid, acc_invoice_id,{'payment_reconcile':'True'},context=context)



def carga_datos_cobros (self, cr, uid, ids, ruta, file, context=None):
    #no hace falta esta comprobacion, se hace luego en el codigo al leer el fichero
    #hay_cliente = comprueba_clientes(self, cr, uid, ids, ruta, file, context=None)
    #if (hay_cliente==False):
        #si no se encuentra el cliente ni por id ni por cod_tercap, es que hay que importar antes el fichero de clientes
    #    raise osv.except_osv(('Error!'),('No existe dato del cliente para registrar el documento. Debe cargar antes los datos del fichero de clientes.'))
    
    journal_obj = self.pool.get('account.journal')
    #comprobamos que en configuracion se ha asociado un diario para registrar los cobros de Tercap
    search_condition = [('cobros_tercap','=',True)]
    journal_obj_id = journal_obj.search (cr, uid, search_condition )
    if (len(journal_obj_id)==0):
        raise osv.except_osv(('Error!'),('No se ha definido un diario para el registro de cobros de Tercap. Revise la configuración')) 

    sale_ord = self.pool.get('sale.order')
    sale_ord_lines = self.pool.get('sale.order.lines')
    sale_inv_rel = self.pool.get('sale.order.invoice.rel')
    acc_invoice = self.pool.get ('account.invoice')
    datos_cli = self.pool.get('res.partner')
    voucher_obj = self.pool.get('account.voucher')

    rescobro = 0
    os.chdir(ruta)
    for nombre in glob.glob(file):
        #_logger.error('##### AIKO ###### En carga datos cobros encuentro fichero:%s'%file)
        fln = open(nombre,'rU') 
        #c = csv.reader(f, delimiter=';', skipinitialspace=True)
        cln = csv.reader(fln, delimiter=";", skipinitialspace=True)

        for lines in cln:
            if lines:
                #lines[0] = Codigo Cliente
                #lines[1] = Codigo Direccion
                #lines[2] = Numero Documento
                #lines[3] = Tipo Documento
                #lines[4] = Fecha Documento
                #lines[5] = Importe Documento (importe cobrado)
                #lines[6] = Importe Pendiente; 0 indica que está cobrado completo
                #lines[7] = Cod Cliente Alternativo (no se usa)
                #lines[8] = Cod Direc. Alternativo (no se usa)

                #_logger.error('##### AIKO ###### En carga datos cobros leo fichero:%s'%lines)
                #3-5-16 buscamos el partner para facilitar la busqueda del documento
                search_condition = [('cod_tercap','=',lines[0])]
                datos_cli_sr = datos_cli.search (cr, uid, search_condition)
                if (len(datos_cli_sr)==0):
                    #si como cod_tercap no localizamos puede que este por id cliente
                    #_logger.error('##### AIKO ###### En carga datos cobros no encuentro cliente con cod_tercap:%s'%lines[0])
                    search_condition = [('id','=',lines[0])]
                    datos_cli_sr = datos_cli.search (cr, uid, search_condition)
                    if (len(datos_cli_sr)==0):
                        raise osv.except_osv(('Error!'),('No hay datos de cliente. Falta un registro de cliente del fichero de cobros.'))

                #creamos un res_search para localizar el documento por numero y tipo:
                res_search = 3
                #si queda en valor 3 no localiza ni factura ni pedido con ese numero:
                #lines[3] nos dice el tipo de documento: 0 es albaran, 1 es factura, 8 es pedido (no se informa de pedidos ptes de cobro)
                if (int(float(lines[3]))==0) or (int(float(lines[3]))==8):
                    search_condition = [('name','ilike',ustr(lines[2])),('partner_id','=',datos_cli_sr[0]),('residual','>',0.0)]
                    #_logger.error('##### AIKO ###### En carga datos cobros busco pedido:%s'%search_condition)
                    sale_ord_id = sale_ord.search (cr, uid, search_condition)
                    if(len (sale_ord_id)!=0):
                        #devolvemos cero para indicar que hemos encontrado pedido / albaran coincidente
                        res_search = 0
                elif (int(float(lines[3]))==1):
                    search_condition = [('number','=',ustr(lines[2])),('partner_id','=',datos_cli_sr[0]),('state','=','open')]
                    acc_invoice_id = acc_invoice.search (cr, uid, search_condition)
                    if(len (acc_invoice_id)!=0):
                        #devolvemos uno para indicar que hemos encontrado factura coincidente
                        res_search = 1
                    #15-12-16: puede que nos llegue un cobro con numero de tercap en lugar de numero de Odoo
                    else:
                        iden_doc = 'tf%'+ ustr(lines[2])
                        search_condition = [('number','ilike',iden_doc),('partner_id','=',datos_cli_sr[0]),('state','=','open')]
                        #_logger.error('##### AIKO ###### En carga datos cobros busco factura:%s'%search_condition)
                        acc_invoice_id = acc_invoice.search (cr, uid, search_condition)
                        if(len (acc_invoice_id)!=0):
                            #devolvemos uno para indicar que hemos encontrado factura coincidente
                            res_search = 1

                #si no hay coincidencias seguimos a otra linea
                if (res_search==3):
                    _logger.error('##### AIKO ###### En carga datos cobros no encuentro documento:%s'%search_condition)
                    rescobro+=1
                    continue
                elif (res_search==1):
                    #en este punto registrar el cobro de una factura
                    #_logger.error('##### AIKO ###### En carga datos cobros encontramos factura:%s'%search_condition)
                    #con el dato de la factura creamos un pago
                    if float(lines[6])==0:
                        acc_inv_sel = acc_invoice.browse(cr, uid, acc_invoice_id)
                        cobro = acc_inv_sel.residual
                    else:
                        cobro = float(lines[5])
                    new_voucher_id = voucher.crea_voucher(self, cr, uid, acc_invoice_id, cobro, context=context)
                    #registramos las lineas de ese recibo
                    voucher.crea_lineas_voucher(self, cr, uid, acc_invoice_id, cobro, new_voucher_id, context=context)
                    #_logger.error('##### AIKO ###### En carga datos cobros encontramos factura creamos voucher:%s'%new_voucher_id)
                    #con el nuevo voucher creado registramos el pago de la factura
                    voucher_obj.button_proforma_voucher(cr, uid, [new_voucher_id], context=context)
                    if float(lines[6])==0:
                        #si no queda pendiente, marcamos la factura para no volver a asociar pagos de sus pedidos
                        acc_invoice.write(cr, uid, acc_invoice_id,{'payment_reconcile':'True'},context=context)
                        acc_invoice.write(cr, uid, acc_invoice_id,{'state':'paid'},context=context)
                        #_logger.error('##### AIKO ###### En carga datos cobros encontramos factura conciliada:%s'%new_voucher_id)
                    rescobro+=1
                elif (res_search==0):
                    #llegados a este punto (es un pedido) registrar el cobro del pedido siempre que no este ya facturado
                    #para saber si esta facturado usamos la tabla sale_order_invoice_rel
                    #para usar ese modelo tenemos que apoyarnos en cr.execute, si no no lo identifica
                    cr.execute('SELECT id from sale_order where id not in (select distinct order_id from sale_order_invoice_rel) and id =%s'%sale_ord_id[0])
                    order_invoice_id = cr.fetchall()
                    #_logger.error('##### AIKO ###### En carga datos cobros valor del cr.execute:%s'%len(order_invoice_id))
                    if len(order_invoice_id)==0:
                        #aqui habria que buscar la factura de ese pedido para registrar el pago en la factura, no en el pedido
                        #_logger.error('##### AIKO ###### En carga datos cobros encontramos pedido ya facturado:%s'%sale_ord_id[0])
                        #buscamos la factura en que esta el pedido
                        cr.execute('SELECT  invoice_id from sale_order_invoice_rel WHERE order_id =%s'%sale_ord_id[0])
                        invoice_rel_id = cr.fetchall()
                        #y verificar que la factura no esta ya pagada por completo
                        acc_invoice_paid = acc_invoice.browse(cr, uid, invoice_rel_id[0])
                        if acc_invoice_paid.residual ==0:
                            #_logger.error('##### AIKO ###### En carga datos cobros factura ya cobrada:%s'%invoice_rel_id[0])
                            continue
                        #_logger.error('##### AIKO ###### En carga datos cobros invoice_rel_id:%s'%invoice_rel_id[0])
                        #_logger.error('##### AIKO ###### En carga datos cobros pago factura rel valor cobro:%s'%float(lines[5]))
                        #_logger.error('##### AIKO ###### En carga datos cobros pago factura rel valor pendiente:%s'%float(lines[6]))
                        registrar_cobro_factura (self, cr, uid, invoice_rel_id[0], float(lines[5]), float(lines[6]), context=context)
                        rescobro+=1
                    else:
                        #_logger.error('##### AIKO ###### En carga datos cobros valor de sale order:%s'%sale_ord_id[0])
                        sale_order_sel = sale_ord.browse(cr, uid, sale_ord_id[0])
                        #comprobamos que tenga pendiente en Odoo, si no tiene ignoramos este cobro
                        if (sale_order_sel.residual==0):
                            #_logger.error('##### AIKO ###### En carga datos cobros pedido sin pendiente:%s'%sale_ord_id[0])
                            rescobro+=1
                            continue
                        #evitamos importes negativos de momento
                        if (float(lines[5])<0):
                            #_logger.error('##### AIKO ###### En carga datos cobros cobrado importe negativo:%s'%sale_ord_id[0])
                            continue
                        #si el importe cobrado es mayor que el residual, pasamos el importe pendiente, no el cobro
                        if (sale_order_sel.residual < float(lines[5])):
                            ter_cobrado = sale_order_sel.residual
                        else:
                            ter_cobrado = float(lines[5])
                        #y si Tercap da por cobrado el total del documento, pasamos el residual
                        if float(lines[6])==0:
                            ter_cobrado = sale_order_sel.residual
                        #_logger.error('##### AIKO ###### En carga datos cobros traspaso ter_cobrado:%s'%ter_cobrado)
                        ter_numdoc = sale_order_sel.name
                        #_logger.error('##### AIKO ###### En carga datos cobros traspaso ter_numdoc:%s'%ter_numdoc)
                        #tomamos los 10 primeros caracteres para no coger la hora, solo el dia
                        dia_pago = str(lines[4])[:10]
                        #_logger.error('##### AIKO ###### En carga datos cobros traspaso dia_pago:%s'%dia_pago)
                        registrar_cobro (self, cr, uid, ter_numdoc, ter_cobrado, journal_obj_id, sale_ord_id[0], dia_pago, context=None)
                        rescobro+=1
    return rescobro
 

def crear_item_tarifa (self, cr, uid, version, product_id, net_price, context=None):
    price_item = self.pool.get('product.pricelist.item')

    val_prices={}
    val_prices['base']=1
    val_prices['price_version_id']= version
    val_prices['product_id']= product_id
    val_prices['price_surcharge'] = net_price
    val_prices['price_discount'] = -1
    price_item.create (cr, SUPERUSER_ID, val_prices, context=context)
    #_logger.error('##### AIKO ###### En crea_item_tarifa creada nuevo valor con valores %s'%val_prices)

    return True

def crear_lote (self, cr, uid, product_id, lot_name, context=None):
    lot_object = self.pool.get('stock.production.lot')

    val_lote={}
    val_lote['name']=lot_name
    val_lote['product_id']= product_id
    val_lote['ref'] = 'tercap_import_'+lot_name
    reslote = lot_object.create (cr, SUPERUSER_ID, val_lote, context=context)
    #_logger.error('##### AIKO ###### En crear_lote creado nuevo lote con valores %s'%val_lote)

    return reslote

def asocia_lineas_factura (self, cr, uid, inv_line_id, sale_line_id, context=None):
    #_logger.error('##### AIKO ###### En asocia_lineas_factura valores recibidos para sale , inv %s,%s'%(sale_line_id,inv_line_id)
    cr.execute("INSERT INTO sale_order_line_invoice_rel (order_line_id, invoice_id) VALUES (%s,%s)",(sale_line_id,inv_line_id))
