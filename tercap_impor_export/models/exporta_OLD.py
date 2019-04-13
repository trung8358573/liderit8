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

import logging
import time
import datetime
from datetime import timedelta
from openerp.tools import ustr
import unicodedata

from openerp.osv import fields, orm, osv


_logger = logging.getLogger(__name__)

#         71. Clientes   =====================================================>
def _create_report71(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('res.partner')
#Revision Manuel 24-2-16 solo exportar clientes, no sus direcciones que van en el siguiente fichero 72
    search_condition = [('active', '=', True),('customer','=', True),('parent_id','=',False)]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
#Revision Manuel 18-2-16: quitar las comillas dobles en clientes, direcciones y productos y poner '',
#si no da error en Tercap. Usamos en las cadenas afectadas .replace("\"","\'")

#modificacion de 15-4-16 por el caso Legado donde usan nombre comercial sobre nombre fiscal
#de estar marcado en la ruta de importacion que se inviertan los nombres comercial y fiscal
#cambian de posicion en el fichero
    inv_names = self.pool.get('tercap.route').browse (cr,uid,1)

    
    output = ''
    for cliente in part_selec_obj:
        line = par_obj.browse(cr, uid, cliente)
        codcliente= str(line.id).zfill(9)
#debemos usar unicode en lugar de str para que coja la cadena con la codificacion adecuada
#si usamos str tendremos problemas con acentos, enies, etc.
        nombrefiscal = unicode(line.name.ljust(50)[:50]).replace("\"","\'") if line.name else  ' '
#21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        nombrefiscal = nombrefiscal.replace(";",",")
        if (line.comercial):
            nombrecomercial = unicode(line.comercial.ljust(50)[:50]).replace("\"","\'")
        else:
            nombrecomercial = unicode(line.name.ljust(50)[:50]).replace("\"","\'") if line.name else  ' '
#21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        nombrecomercial = nombrecomercial.replace(";",",")
        direccion=unicode(line.street.ljust(50)[:50]).replace("\"","\'") if line.street else  ' '
#21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        direccion = direccion.replace(";",",")
        poblacion=line.city.ljust(50)[:50] if line.city else ' '
#21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        poblacion = unicode(poblacion).replace(";",",")
        codpostal=line.zip.ljust(10)[:10] if line.zip else ' '
        provincia= line.state_id.name.ljust(30)[:30] if line.state_id.name else  ' '
#21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        provincia = unicode(provincia).replace(";",",")
        telefono=unicode(line.phone).ljust(30)[:30] if line.phone else ' '
        cifnif=unicode(line.vat).ljust(20)[:20] if line.vat else ' '
        codformapago= line.property_payment_term.tercap_cod_forma_pago  if line.property_payment_term.tercap_cod_forma_pago else '1'
        #27-4-16 cambiamos el criterio para pasar el id del Modo de pago de la ficha de cliente en lugar del plazo de pago
        #codformapagoerp= line.property_payment_term.name.ljust(20)[:20] if line.property_payment_term.name else ' '
        codformapagoerp= unicode(line.customer_payment_mode.id).zfill(10) if line.customer_payment_mode else ' '
        tipoiva= line.property_account_position.tercap_tipo_iva if line.property_account_position.tercap_tipo_iva else 'R'
        codtarifa= line.property_product_pricelist.name.ljust(4)[:4] if line.property_product_pricelist.name else ' '
        codexclusividad= line.tercap_codexclusividad.ljust(4)[:4] if line.tercap_codexclusividad else ' '
        descuentogeneral= unicode(line.tercap_descuentogeneral).zfill(10)
        descuentopp=unicode(line.tercap_descuentopp).zfill(10)
        creditomaximo=line.credit_limit if line.credit_limit else 0
        #observaciones=unicode(line.comment).replace("\"","\'") or ' '
        #17-6-16 para eliminar los saltos de linea en las observaciones
        if line.comment:
            observaciones = ' '.join(unicode((line.comment).replace("\"","\'")).splitlines())
        else:
            observaciones = ''
        solicitarnumpedido= line.tercap_solicitarnumpedido if  line.tercap_solicitarnumpedido else 'N'
        albarancontado= line.tercap_albarancontado  if line.tercap_albarancontado else 'N'
        albaranvalorado=line.tercap_albaranvalorado  if line.tercap_albaranvalorado else 'S'
        codcliealternativo=unicode(line.ref).ljust(20)[:20] if line.ref else ' '
        tipoventa= line.tercap_tipoventa if line.tercap_tipoventa else  '0'
        codigoproveedor='0000'
        permitirdevoluciones= line.tercap_permitirdevoluciones if line.tercap_permitirdevoluciones else 'S'
        imprimircopiaalb= line.tercap_imprimircopiaalb  if line.tercap_imprimircopiaalb   else 'S'
        #nuevo valor 1-8-16 para la ruta por defecto de reparto del cliente
        codrutaentrega = unicode(line.tercap_reparto_id.cod_tercap).zfill(4) if line.tercap_reparto_id else '0000'
        
#modificacion del 15-4-16 por el orden de nombres visto arriba
        if (inv_names.inv_nombres):
            fields_fields_71 = [
            codcliente,
            nombrecomercial.rstrip(),
            nombrefiscal.rstrip(),
            direccion.rstrip(),
            poblacion.rstrip(),
            codpostal.rstrip(),
            provincia.rstrip(),
            telefono.rstrip(),
            cifnif.rstrip(),
            codformapago,
            codformapagoerp,
            tipoiva.rstrip(),
            codtarifa.rstrip(),
            codexclusividad.rstrip(),
            descuentogeneral,
            descuentopp,
            creditomaximo,
            observaciones.rstrip(),
            solicitarnumpedido,
            albarancontado,
            albaranvalorado,
            codcliealternativo.rstrip(),
            tipoventa,
            codigoproveedor,
            permitirdevoluciones,
            imprimircopiaalb,
            #nuevo valor 01-08-16:
            codrutaentrega, 
            ]
        else:
            fields_fields_71 = [
            codcliente,
            nombrefiscal.rstrip(),
            nombrecomercial.rstrip(),
            direccion.rstrip(),
            poblacion.rstrip(),
            codpostal.rstrip(),
            provincia.rstrip(),
            telefono.rstrip(),
            cifnif.rstrip(),
            codformapago,
            codformapagoerp,
            tipoiva.rstrip(),
            codtarifa.rstrip(),
            codexclusividad.rstrip(),
            descuentogeneral,
            descuentopp,
            creditomaximo,
            observaciones.rstrip(),
            solicitarnumpedido,
            albarancontado,
            albaranvalorado,
            codcliealternativo.rstrip(),
            tipoventa,
            codigoproveedor,
            permitirdevoluciones,
            imprimircopiaalb, 
             #nuevo valor 01-08-16:
            codrutaentrega,
            ]				  
        #_logger.error('##### AIKO ###### En 71 clientes valores a registrar:%s'%fields_fields_71)
        fields_71 = ';'.join(['%s' % one_field for one_field in fields_fields_71])
#        output += fields_71.encode('UTF-8') + '\n'
        output += fields_71.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/CLIENTE'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return

#         72. Direcciones   ==================================================>
def _create_report72(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('res.partner')
    search_condition = [('active', '=', True),('customer','=', True),('parent_id','=', False)]
    part_selec_obj = par_obj.search(cr, uid, search_condition )

#modificacion de 15-4-16 por el caso Legado donde usan nombre comercial sobre nombre fiscal
#de estar marcado en la ruta de importacion que se inviertan los nombres comercial y fiscal
#cambian de posicion en el fichero
    inv_names = self.pool.get('tercap.route').browse (cr,uid,1)
       
    #Revision Manuel 18-2-16: quitar las comillas dobles en clientes, direcciones y productos y poner '', 
    #si no da error en Tercap. Usamos en las cadenas afectadas .replace("\"","\'")                          
    output = ''
    for cliente in part_selec_obj:
        line = par_obj.browse(cr, uid, cliente)
        
        coddireccion = str(line.id).zfill(9) 
        codcliente= str(line.id).zfill(9)

        #nombrecomercial = unicode(line.name.ljust(50)[:50]).replace("\"","\'") if line.name else  ' ' 
        #modificado el 5-4-16 aqui el nombre comercial y no el name
#modificado el 15-4-16 por si se quiere invertir el nombre comercial y fiscal como en Legado
        if (inv_names.inv_nombres):
            nombrecomercial = unicode(line.name.ljust(50)[:50]).replace("\"","\'") if line.name else  ' '
        else:
            if (line.comercial): 
                nombrecomercial = unicode(line.comercial.ljust(50)[:50]).replace("\"","\'")
            else:
                nombrecomercial = unicode(line.name.ljust(50)[:50]).replace("\"","\'")


        #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        nombrecomercial = nombrecomercial.replace(";",",")
        direccion=unicode(line.street.ljust(50)[:50]).replace("\"","\'") if line.street else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        direccion = direccion.replace(";",",")
        poblacion=line.city.ljust(50)[:50] if line.city else ' '
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        poblacion = unicode(poblacion).replace(";",",")
        codpostal=line.zip.ljust(10)[:10] if line.zip else ' '
        provincia= line.state_id.name.ljust(30)[:30] if line.state_id.name else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        provincia = unicode(provincia).replace(";",",")
        telefono=line.phone.ljust(30)[:30] if line.phone else ' '  
        codformapago= line.property_payment_term.tercap_cod_forma_pago  if line.property_payment_term.tercap_cod_forma_pago else '1'
        codtarifa= line.property_product_pricelist.name.ljust(4)[:4] if line.property_product_pricelist.name else ' '
        codexclusividad= line.tercap_codexclusividad.ljust(4)[:4] if line.tercap_codexclusividad else ' '
        creditomaximo=line.credit_limit if line.credit_limit else 0
        #observaciones=line.comment or ' '
        #17-6-16 para eliminar los saltos de linea en las observaciones
        if line.comment:
            observaciones = ' '.join(unicode((line.comment).replace("\"","\'")).splitlines())
        else:
            observaciones = ''
        codcliealternativo=line.ref.ljust(20)[:20] if line.ref else ' '
        coddiralternativo = ' '
        tipocliente= ' '
        codigoproveedor='0000'
        permitirdevoluciones= line.tercap_permitirdevoluciones if line.tercap_permitirdevoluciones else 'S'
        #nuevo valor 1-8-16 para la ruta por defecto de reparto del cliente
        codrutaentrega = unicode(line.tercap_reparto_id.cod_tercap).zfill(4) if line.tercap_reparto_id else '0000'
        
              
        fields_fields_72 = [
        coddireccion,
        codcliente,
        nombrecomercial.rstrip(),  
        direccion.rstrip(),
        poblacion.rstrip(),
        codpostal.rstrip(),
        provincia.rstrip(),
        telefono.rstrip(),
        codformapago.rstrip(),
        codtarifa.rstrip(),
        codexclusividad.rstrip(),
        creditomaximo,
        observaciones.rstrip(),
        codcliealternativo.rstrip(),
        coddiralternativo,
        tipocliente,
        codigoproveedor,
        permitirdevoluciones,
        #nuevo valor 01-08-16:
        codrutaentrega,
                              ]
        
        fields_72 = ';'.join(['%s' % one_field for one_field in fields_fields_72])
        output += fields_72.encode('CP1252') + '\n'


#13-5-16 y exportamos las que no son clientes pero son direcciones de entrega
#    search_condition = [('active', '=', True),('parent_id','!=', False)]
#03-10-16 pero solo las que sean del tipo 'delivery', solo interesan direcciones de entrega no de facturacion
    search_condition = [('active', '=', True),('parent_id','!=', False),('type','=','delivery')]
    part_selec_obj = par_obj.search(cr, uid, search_condition )

    for cliente in part_selec_obj:
        line = par_obj.browse(cr, uid, cliente)
        #si el padre no es cliente, no cogemos esta fila
        if line.parent_id.customer==False:
            continue
        coddireccion = str(line.id).zfill(9) 
        codcliente= str(line.parent_id.id).zfill(9)

#modificado el 15-4-16 por si se quiere invertir el nombre comercial y fiscal como en Legado
        if (inv_names.inv_nombres):
            nombrecomercial = unicode(line.name.ljust(50)[:50]).replace("\"","\'") if line.name else  ' '
        else:
            if (line.comercial): 
                nombrecomercial = unicode(line.comercial.ljust(50)[:50]).replace("\"","\'")
            else:
                nombrecomercial = unicode(line.name.ljust(50)[:50]).replace("\"","\'")

        #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        nombrecomercial = nombrecomercial.replace(";",",")
        direccion=unicode(line.street.ljust(50)[:50]).replace("\"","\'") if line.street else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        direccion = direccion.replace(";",",")
        poblacion=line.city.ljust(50)[:50] if line.city else ' '
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        poblacion = unicode(poblacion).replace(";",",")
        codpostal=line.zip.ljust(10)[:10] if line.zip else ' '
        provincia= line.state_id.name.ljust(30)[:30] if line.state_id.name else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        provincia = unicode(provincia).replace(";",",")
        telefono=line.phone.ljust(30)[:30] if line.phone else ' '  
        codformapago= line.property_payment_term.tercap_cod_forma_pago  if line.property_payment_term.tercap_cod_forma_pago else '1'
        codtarifa= line.property_product_pricelist.name.ljust(4)[:4] if line.property_product_pricelist.name else ' '
        codexclusividad= line.tercap_codexclusividad.ljust(4)[:4] if line.tercap_codexclusividad else ' '
        creditomaximo=line.credit_limit if line.credit_limit else 0
        #observaciones=line.comment or ' '
        #17-6-16 para eliminar los saltos de linea en las observaciones
        if line.comment:
            observaciones = ' '.join(unicode((line.comment).replace("\"","\'")).splitlines())
        else:
            observaciones = ''
        codcliealternativo=line.ref.ljust(20)[:20] if line.ref else ' '
        coddiralternativo = ' '
        tipocliente= ' '
        codigoproveedor='0000'
        permitirdevoluciones= line.tercap_permitirdevoluciones if line.tercap_permitirdevoluciones else 'S'
        #nuevo valor 1-8-16 para la ruta por defecto de reparto del cliente
        codrutaentrega = unicode(line.tercap_reparto_id.cod_tercap).zfill(4) if line.tercap_reparto_id else '0000'
        
        
        fields_fields_72P = [
        coddireccion,
        codcliente,
        nombrecomercial.rstrip(),  
        direccion.rstrip(),
        poblacion.rstrip(),
        codpostal.rstrip(),
        provincia.rstrip(),
        telefono.rstrip(),
        codformapago.rstrip(),
        codtarifa.rstrip(),
        codexclusividad.rstrip(),
        creditomaximo,
        observaciones.rstrip(),
        codcliealternativo.rstrip(),
        coddiralternativo,
        tipocliente,
        codigoproveedor,
        permitirdevoluciones,
        #nuevo valor 01-08-16:
        codrutaentrega,
                              ]
        
        fields_72P = ';'.join(['%s' % one_field for one_field in fields_fields_72P])
        output += fields_72P.encode('CP1252') + '\n'
        
    filename = '/var/ftp/ERP/DIRECCION'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return

#         73. Productos   ====================================================>
def _create_report73(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('product.product')
    search_condition = [('active', '=', True),('tercap_product','=', True),('sale_ok','=', True)]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
    #ampliado por Manuel el 12-2-16 para controlar precios con y sin iva incluido
    tax_obj = self.pool.get('account.tax')
    #ampliado el 9-9-16 para controlar el tipo de codigo de producto al exportar
    #localizamos el directorio de importacion y como tiene definido el valor de product_default_idcode
    directory_obj = self.pool['tercap.route']
    search_condition = [('alcance', '=', 'import')]
    direct_imp_obj = directory_obj.search(cr, uid, search_condition)
    codigo_default = directory_obj.browse(cr, uid, direct_imp_obj[0]).product_default_idcode
                                 

    #Revision Manuel 18-2-16: quitar las comillas dobles en clientes, direcciones y productos y poner '', 
    #si no da error en Tercap. Usamos en las cadenas afectadas .replace("\"","\'")
    output = ''
    for producto in part_selec_obj:
        line = par_obj.browse(cr, uid, producto)
        #21-3-16 cambio criterio para nombre, se coge solo name y default code va al codigo de producto
        #comprobamos que default_code sea un numerico 
        #para no repetir con ids de Odoo limitamos a los 8 primeros valores
        #modificado el 9-9-16 para controlar el tipo de valor a exportar, si es True pasamos como codproducto el default code
        #y el id lo pasamos en el codprodalternativo (solucion original del 21-3-16); si no el default code se comunica como
        #codprovalternativo, que permite default_code no numéricos y el id de Odoo se transmite en codproducto.
        if codigo_default:
            codproducto= unicode(line.default_code).strip()
            if ((line.default_code) and (len (codproducto)<9) and (codproducto.isdigit()) and (int(codproducto) < 99999999)):
                codproducto= codproducto.zfill(9)
            else:
                #_logger.error('##### AIKO ###### En 73 productos valor de ref interna no numerico:%s'%codproducto)
                #si no es un numero enviamos el id sumando 900 000 000 para que no se repitan con default_code
                codproducto= 900000000 + (line.id)
            #para asegurarnos que enviamos el id siempre, en todo caso lo registramos en CodAlternativo:
            codprodalternativo= str(line.id).zfill(9)
        #modificacion del 9-9-16: vamos a enviar en codprodalternativo el default_code si asi esta marcado
        #y en codproducto el id de Odoo. Tercap permite buscar por ambos campos
        #y asi resolvemos que en codproducto no podemos pasar codigos alfanumericos de productos
        else:
            codproducto= str(line.id).zfill(9)
            if line.default_code:
                codprodalternativo= unicode(line.default_code).strip()
            else:
                codprodalternativo =''


        #descripcion= unicode(line.name.ljust(50)[:50]).replace("\"","\'") if line.name else  ' ' 
        #14-3 modificamos para mostrar la referencia interna en el nombre del producto
        #strproducto =  "["+unicode(line.default_code).strip()+"] " + unicode(line.name).strip()
        #21-3-16 dejamos solo la descripcion, porque la ref interna de haberla va en CodProducto
        #09-11-16 tenemos que tener en cuenta si hay una descripcion de venta para pasar ese valor como descripcion
        if line.product_tmpl_id.description_sale:
            strproducto = unicode(line.product_tmpl_id.description_sale).strip()
        else:
            strproducto = unicode(line.name_template).strip()

        
        descripcion= unicode(strproducto.ljust(50)[:50]).replace("\"","\'") if line.name_template else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        descripcion = descripcion.replace(";",",")
        unidadventa= line.uom_id.tercap_unit.ljust(10)[:10] if line.uom_id.tercap_unit else  'U' 
        unidadescaja= str(line.tercap_unidadescaja).zfill(9) 
        if line.taxes_id:
            codiva= line.taxes_id[0].tercap_codiva if line.taxes_id[0].tercap_codiva else '1'
        else:
            codiva = '1'
        loterequerido= line.tercap_loterequerido if line.tercap_loterequerido else 'N'
        codenvase= str(line.tercap_codenvase_id.tercap_codenvase).zfill(9) if line.tercap_codenvase_id else '0'
        espesovariable= line.tercap_espesovariable if line.tercap_espesovariable else 'N'
        pesoestandar= str(line.tercap_pesoestandar).zfill(10)
        desviacionpeso= str(line.tercap_desviacionpeso).zfill(10)
        #para controlar el tipo de iva del producto
        search_condition = [('id', '=', line.taxes_id.id)]
        tpiva = tax_obj.search(cr, uid, search_condition)
        if (len(tpiva)==0):
            raise osv.except_osv(('Error!'),('No se ha definido el tipo de iva aplicable al producto %s'%descripcion))
        tipoimp = tax_obj.browse(cr, uid, tpiva[0])
        #si los precios son con iva descontamos el tipo de iva
        if (tipoimp.price_include):
            preciosin = line.list_price / (1+tipoimp.amount)
            precioventa= str(preciosin).zfill(10)
        else:
            precioventa= str(line.list_price).zfill(10)
        ean13= line.ean13 if line.ean13 else ' '
          
        codproveedor= str(line.seller_ids[0].id).zfill(10) if line.seller_ids else '0'   

        #27-9-16 exportamos informacion de precio minimo y maximo segun version 23 de integracion
        precio_min = str(line.min_price).zfill(10) if line.min_price else '0'
        precio_max = str(line.max_price).zfill(10) if line.max_price else '999999'

            
        fields_fields_73 = [                   
        codproducto,
        descripcion.rstrip(),  
        unidadventa.rstrip(),  
        unidadescaja,
        codiva,
        loterequerido,
        codenvase,
        espesovariable,
        pesoestandar,
        desviacionpeso,
        precioventa,
        ean13,
        codprodalternativo.rstrip(),  
        codproveedor,
        precio_min,
        precio_max,                     
                              ]
        
        fields_73 = ';'.join(['%s' % one_field for one_field in fields_fields_73])
        output += fields_73.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/PRODUCTO'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return   
#=========================74 Envases ========================================>
def _create_report74(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('codi.envase')
    search_condition = [('tercap_obsoleto','=', False)]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
                                 

    output = ''
    for envase in part_selec_obj:
        line = par_obj.browse(cr, uid, envase)
        
        codenvase= str(line.tercap_codenvase).zfill(9)   
        descripcion= line.tercap_name.ljust(50)[:50] if line.tercap_name else  ' ' 
        importe= str(line.tercap_importe).zfill(10)
        
            
        fields_fields_74 = [                            
        codenvase,
        descripcion.rstrip(),
        importe,           
         ]
        
        fields_74 = ';'.join(['%s' % one_field for one_field in fields_fields_74])
        output += fields_74.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/ENVASE'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return

#========================= 75 IVA ========================================>
def _create_report75(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('account.tax')
    search_condition = [('tercap_codiva','!=', '0')]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
                                 

    output = ''
    ivan = 0
    recn= 0
    ivar = 0 
    recr = 0
    ivas = 0
    recs = 0
    #Modificado el 7-4-16 segun correo de Tercap: valores con 9 digitos, no 10 como hasta ahora
    for iva in part_selec_obj:
        line = par_obj.browse(cr, uid, iva)
        valor_tipo = line.amount*100
        valor_tipo = format(valor_tipo, '.1f')
        valor_str = str(valor_tipo).zfill(9)
        #_logger.error('##### AIKO ###### En 75 datos para valor del id de iva:%s'%line.tercap_codiva)
        #_logger.error('##### AIKO ###### En 75 datos para valor del tipo de iva:%s'%valor_tipo)
        #_logger.error('##### AIKO ###### En 75 datos con una cadena:%s'%valor_str)
        if line.tercap_codiva == '1' and  line.type == 'percent':
            ivan= valor_str
        if line.tercap_codiva == '5' and  line.type == 'percent':
            recn= valor_str
        if line.tercap_codiva == '2' and  line.type == 'percent':
            ivar= valor_str
        if line.tercap_codiva == '6' and  line.type == 'percent':
            recr= valor_str   
        if line.tercap_codiva == '3' and  line.type == 'percent':
            ivas= valor_str  
        if line.tercap_codiva == '7' and  line.type == 'percent':
            recs= valor_str     
   
    fields_fields_75 = [ 
    ivan,
    recn,
    ivar, 
    recr,
    ivas,
    recs,                                                                            
     ]
    fields_75 = ';'.join(['%s' % one_field for one_field in fields_fields_75])
    output += fields_75.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/IVA'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return
#=========================76 Tarifas  ========================================
def _create_report76(self, cr, uid, ids, context=None):
#  Sin definir 
    return
#==========================77 Formas de Pago   ================================
def _create_report77(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    #27-4-16 aqui pasamos a enviar los modos de pago en lugar de los plazos de pago
    #par_obj = self.pool.get('account.payment.term')
    par_obj = self.pool.get('payment.mode')
    search_condition = [('active','=', True),('tercap_comunicate','=', True)]
    part_selec_obj = par_obj.search(cr, uid, search_condition)
                                 

    output = ''
    for forma in part_selec_obj:
        line = par_obj.browse(cr, uid, forma)
        
        codformapagoerp= str(line.id).zfill(10)        
        descripcion= line.name.ljust(50)[:50] if line.name else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        descripcion = unicode(descripcion).replace(";",",")
        #27-4-16 cambiamos este criterio para reconocer los modos de pago de contado y credito
        #if line.tercap_cod_forma_pago == '0':
        #    escredito = 'S'
        #elif line.tercap_cod_forma_pago == '1':
        #    escredito = 'N'
        #else:     
        #    escredito = 'N'        
#         escredito =  line.tercap_creditocontado if line.tercap_creditocontado else 'N'

        #27-4-16 para saber si es de contado buscamos a traves del journal_id asociado
        if line.journal.type =='cash':
            escredito = 'N'
        else:
            escredito = 'S'

        codtarifa = '    '
            
        fields_fields_77 = [               
        codformapagoerp,        
        descripcion.rstrip(),
        escredito,
        codtarifa,                  
         ]
        
        fields_77 = ';'.join(['%s' % one_field for one_field in fields_fields_77])
        output += fields_77.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/FPAGO'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return
#============================= 78 cobros pendientes   =========================

def _create_report78(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('account.invoice')
    search_condition = [('state','=','open'),('residual','!=',0),'|',('type','=','out_invoice'),('type','=','out_refund')]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
#modificacion de 11-5-16 por el caso Panta que solo quiere exportar saldo en los clientes
#que tengan marcado en Tercap que se le cobran los albaranes
    inv_names = self.pool.get('tercap.route').browse (cr,uid,1)

                                 
    output = ''
    for factura in part_selec_obj:
        line = par_obj.browse(cr, uid, factura)

        if(inv_names.saldo_cobrables and line.partner_id.tercap_albarancontado=='N'):
            continue

        cocliente= str(line.partner_id.id).zfill(9)
        #coddireccion=str(line.partner_id.id).zfill(9) 
        if (line.partner_id.parent_id):
            coddireccion=str(line.partner_id.parent_id.id).zfill(9)  
        else:
            coddireccion=str(line.partner_id.id).zfill(9)                           
        numdocumento=line.number.ljust(20)[:20] if line.number else  ' ' 
        tipodocumento='1'
        if line.type == 'out_invoice': tipodocumento='1'
        if line.type == 'out_refund': tipodocumento='3'
        fechadocumento = datetime.datetime.strptime(line.date_invoice, '%Y-%m-%d')
        importedocum= str(line.amount_total).zfill(10)
        importependiente= str(line.residual).zfill(10)
        codcliealternativo='    '
        coddirealternativo='    '
 
        fields_fields_78 = [               
        cocliente,
        coddireccion,  
        numdocumento.rstrip(), 
        tipodocumento,
        fechadocumento,
        importedocum,
        importependiente,
        codcliealternativo,
        coddirealternativo,  
         ]
        
        fields_78 = ';'.join(['%s' % one_field for one_field in fields_fields_78])
        output += fields_78.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'

    #===== Manuel 01-03-2016 ampliamos al caso de pedidos con cobros pendientes  ===========
    sale_obj = self.pool.get('sale.order')
    #10-3-16 aumentamos a que no este facturada, con line_ids.invoice_lines = false
    sale_line_obj = self.pool.get ('sale.order.line')
    '''
    search_condition = [('invoice_lines','=',False)]
    sale_line_ids = sale_line_obj.search(cr, uid, search_condition)
    sale_not_invoiced=[]
    new_id = 0
    for sale_line in sale_line_ids:
        sale_line_brow = sale_line_obj.browse(cr, uid, sale_line)
        if (sale_line_brow.order_id.id!=new_id):
            sale_not_invoiced.append (sale_line_brow.order_id.id)
            new_id = sale_line_brow.order_id.id
    if (len(sale_not_invoiced)!=0):
        #_logger.error('##### AIKO ###### En 78 datos para sale_not_inoviced:%s'%sale_not_invoiced)
        search_condition = [('residual','>',0),('state','=','manual'),('id','in',sale_not_invoiced)]
        #search_condition = [('residual','>',0),('state','!=','draft')]
    else:
        search_condition = [('residual','>',0),('state','=','manual')]
    sale_selec_obj = sale_obj.search(cr, uid, search_condition)
    '''
    cr.execute('SELECT id from sale_order where residual <> 0 and state = \'manual\' and id not in (select distinct order_id from sale_order_invoice_rel)')
    sale_selec_obj = cr.fetchall()
    for pedido in sale_selec_obj:
        linea = sale_obj.browse(cr, uid, pedido)

        if(inv_names.saldo_cobrables and linea.partner_id.tercap_albarancontado=='N'):
            continue
        
        cocliente= str(linea.partner_id.id).zfill(9)
        if (linea.partner_id.parent_id):
            coddireccion=str(linea.partner_id.parent_id.id).zfill(9)  
        else:
            coddireccion=str(linea.partner_id.id).zfill(9)                     
        numdocumento=linea.name.ljust(20)[:20] if linea.name else  ' ' 
        #si el pedido es de tipo PT marcamos documento pedido, 
        #y si no siempre documento albaran (importados AT y hechos en Odoo)
        if ustr(linea.name).startswith("PT"):
            tipodocumento='8'
        else:
            tipodocumento='0'
        fechadocumento = datetime.datetime.strptime(linea.date_order, '%Y-%m-%d %H:%M:%S')
        importedocum= str(linea.amount_total).zfill(10)
        importependiente= str(linea.residual).zfill(10)
        codcliealternativo='    '
        coddirealternativo='    '
 
        fields_fields_78P = [               
        cocliente,
        coddireccion,  
        numdocumento.rstrip(), 
        tipodocumento,
        fechadocumento,
        importedocum,
        importependiente,
        codcliealternativo,
        coddirealternativo,  
         ]
        #_logger.error('##### AIKO ###### En 78 datos para la linea fields:%s'%fields_fields_78P)
        fields_78P = ';'.join(['%s' % one_field_p for one_field_p in fields_fields_78P])
        output += fields_78P.encode('CP1252') + '\n'
        
    filename = '/var/ftp/ERP/COBRO'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return
#================ 79 Descuento por cliente y producto =========================

def _create_report79(self, cr, uid, ids, context=None):
#  Creado el 3-5-16
    if context is None:
        context = {}
    prop_obj = self.pool.get('ir.property')
    search_condition = [('name','like','property_product_pricelist')]
    prop_selec_obj = prop_obj.search(cr, uid, search_condition)
    version_obj = self.pool.get('product.pricelist.version')
    price_item = self.pool.get('product.pricelist.item')
    partner_obj = self.pool.get('res.partner')

    #localizamos el directorio de importacion y como tiene definido el valor de product_default_idcode
    directory_obj = self.pool['tercap.route']
    search_condition = [('alcance', '=', 'import')]
    direct_imp_obj = directory_obj.search(cr, uid, search_condition)
    codigo_default = directory_obj.browse(cr, uid, direct_imp_obj[0]).product_default_idcode

    output = ''
    #con esto lo primero que tenemos es la relacion entre tarifas y clientes
    #tenemos que extraer el valor numérico que hay en la cadena despues de la coma
    for pr_list in prop_selec_obj:
        text_partner = prop_obj.browse(cr,uid,pr_list).res_id
        if (text_partner):
            price_coma = text_partner.find(',')+1
        else:
            continue
        text_partner = text_partner[price_coma:]
        partner_id = partner_obj.browse(cr, uid, int(text_partner))
        #_logger.error('##### AIKO ###### En 79 tarifas encuentro el partner:%s'%text_partner)

        text_pricelist = prop_obj.browse(cr,uid,pr_list).value_reference
        if (text_pricelist):
            price_coma = text_pricelist.find(',')+1
            text_pricelist = text_pricelist[price_coma:]
            text_pricelist = int(text_pricelist)
            #_logger.error('##### AIKO ###### En 79 tarifas encuentro la tarifa:%s'%text_pricelist)
        else:
            raise osv.except_osv(('Error!'),('No se ha definido la tarifa de venta para el cliente %s'%partner_id.name))
        
        #con el dato del product_pricelist buscamos el product_pricelist_version_id
        search_condition = [('pricelist_id','=',text_pricelist)]
        version_obj_sr = version_obj.search(cr,uid,search_condition)
        for version in version_obj_sr:
            #_logger.error('##### AIKO ###### En 79 tarifas encuentro version de product_pricelist_version:%s'%version)
            #obtenemos el date_start y date_end de la version para mas adelante
            version_obj_dates = version_obj.browse(cr,uid,version)
            desdef = version_obj_dates.date_start
            hastaf = version_obj_dates.date_end
            #con el id de la version de la tarifa hacemos un for en los item solo si se basan en PVP
            search_condition = [('price_version_id','=',version),('base','=',1),('product_id','!=',False)]
            price_item_obj = price_item.search(cr,uid,search_condition)
            for prices in price_item_obj:
                #_logger.error('##### AIKO ###### En 79 tarifas encuentro item en product_pricelist_item:%s'%prices)
                line = price_item.browse(cr,uid,prices)
                cocliente = str(text_partner).zfill(9)
                #_logger.error('##### AIKO ###### En 79 tarifas encuentro default_code de product:%s'%line.product_id.default_code)
                #11-10-16 si se desmarca codigo_default se utiliza el id como identificador de producto
                if codigo_default==False:
                    codproducto= str(line.product_id.id).zfill(9)
                else:
                    if (line.product_id.default_code)<>'':
                        codproducto= unicode(line.product_id.default_code).strip()
                        if (len (codproducto)<9) and (codproducto.isdigit()) and (int(codproducto) < 99999999):
                            codproducto= codproducto.zfill(9)
                        else:
                            codproducto= 900000000 + (line.product_id.id)
                    else:
                        codproducto= 900000000 + (line.product_id.id)

                
                if desdef:
                    fechainicio = desdef
                else:
                    fechainicio = datetime.datetime.now().strftime("%Y-%m-%d")
                if hastaf:
                    fechafin = hastaf
                else:
                    fechafin = (datetime.datetime.now()+ datetime.timedelta(days=1825)).strftime("%Y-%m-%d")
                #prescindimos de las tarifas no vigentes
                fdesde = datetime.datetime.strptime(fechainicio, '%Y-%m-%d')
                fhasta = datetime.datetime.strptime(fechafin, '%Y-%m-%d')
                if fhasta < datetime.datetime.now() or fdesde > datetime.datetime.now():
                    continue
                if (float(line.price_discount<>0)):
                    tipodto = '%'
                    #evitamos registrar los que dejan el precio a cero para poner un precio especial
                    if abs(line.price_discount)==1:
                        continue
                    valor = float(line.price_discount) * (-100)
                else:
                    continue

                codclialt =''
                codprovalt=''
                                     
                fields_fields_79 = [               
                cocliente,        
                codproducto,
                tipodto,
                valor, 
                fechainicio,
                fechafin,
                codclialt,
                codprovalt,
                 ]
                #_logger.error('##### AIKO ###### En 79 registrando valores:%s'%fields_fields_79)
                fields_79 = ';'.join(['%s' % one_field for one_field in fields_fields_79])
                output += fields_79.encode('CP1252') + '\n'

        
    filename = '/var/ftp/ERP/DESCUENTO'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return
#==================== 710 Promociones  ========================================

def _create_report710(self, cr, uid, ids, context=None):
#  Creado el 6-6-16
    if context is None:
        context = {}
    prop_obj = self.pool.get('ir.property')
    search_condition = [('name','like','property_product_pricelist')]
    prop_selec_obj = prop_obj.search(cr, uid, search_condition)
    version_obj = self.pool.get('product.pricelist.version')
    price_item = self.pool.get('product.pricelist.item')
    partner_obj = self.pool.get('res.partner')
    #localizamos el directorio de importacion y como tiene definido el valor de product_default_idcode
    directory_obj = self.pool['tercap.route']
    search_condition = [('alcance', '=', 'import')]
    direct_imp_obj = directory_obj.search(cr, uid, search_condition)
    codigo_default = directory_obj.browse(cr, uid, direct_imp_obj[0]).product_default_idcode

    output = ''
    #con esto lo primero que tenemos es la relacion entre tarifas y clientes
    #tenemos que extraer el valor numérico que hay en la cadena despues de la coma
    for pr_list in prop_selec_obj:
        text_partner = prop_obj.browse(cr,uid,pr_list).res_id
        if (text_partner):
            price_coma = text_partner.find(',')+1
        else:
            continue
        text_partner = text_partner[price_coma:]
        partner_id = partner_obj.browse(cr, uid, int(text_partner))
        #_logger.error('##### AIKO ###### En 710 tarifas encuentro el partner:%s'%text_partner)

        text_pricelist = prop_obj.browse(cr,uid,pr_list).value_reference
        if (text_pricelist):
            price_coma = text_pricelist.find(',')+1
            text_pricelist = text_pricelist[price_coma:]
            text_pricelist = int(text_pricelist)
            #_logger.error('##### AIKO ###### En 710 tarifas encuentro la tarifa:%s'%text_pricelist)
        else:
            raise osv.except_osv(('Error!'),('No se ha definido la tarifa de venta para el cliente %s'%partner_id.name))

        
        #caso improbable: una direccion de entrega no debe tener una tarifa especial, no registramos este dato
        if partner_id.parent_id:
            continue
        #con el dato del product_pricelist buscamos el product_pricelist_version_id
        search_condition = [('pricelist_id','=',text_pricelist)]
        version_obj_sr = version_obj.search(cr,uid,search_condition)
        for version in version_obj_sr:
            #_logger.error('##### AIKO ###### En 710 tarifas encuentro version de product_pricelist_version:%s'%version)
            #obtenemos el date_start y date_end de la version para mas adelante
            version_obj_dates = version_obj.browse(cr,uid,version)
            desdef = version_obj_dates.date_start
            hastaf = version_obj_dates.date_end
            #con el id de la version de la tarifa hacemos un for en los item solo si se basan en PVP
            search_condition = [('price_version_id','=',version),('base','=',1),('product_id','!=',False)]
            price_item_obj = price_item.search(cr,uid,search_condition)
            for prices in price_item_obj:
                #_logger.error('##### AIKO ###### En 710 tarifas encuentro item en product_pricelist_item:%s'%prices)
                line = price_item.browse(cr,uid,prices)

                cocliente = str(text_partner).zfill(9)
                codireccion = cocliente

                #_logger.error('##### AIKO ###### En 710 tarifas encuentro default_code de product:%s'%line.product_id.default_code)
                #11-10-16 si esta desmarcada la opción de default code identificativo, como codproducto sera siempre el id
                if codigo_default==False:
                    codproducto= str(line.product_id.id).zfill(9)
                else:
                    if (line.product_id.default_code)<>'':
                        codproducto= unicode(line.product_id.default_code).strip()
                        if (len (codproducto)<9) and (codproducto.isdigit()) and (int(codproducto) < 99999999):
                            codproducto= codproducto.zfill(9)
                        else:
                            codproducto= 900000000 + (line.product_id.id)
                    else:
                        codproducto= 900000000 + (line.product_id.id)
                
                if desdef:
                    fechainicio = desdef
                else:
                    fechainicio = datetime.datetime.now().strftime("%Y-%m-%d")
                if hastaf:
                    fechafin = hastaf
                else:
                    fechafin = (datetime.datetime.now()+ datetime.timedelta(days=1825)).strftime("%Y-%m-%d")
                #prescindimos de las tarifas no vigentes
                fdesde = datetime.datetime.strptime(fechainicio, '%Y-%m-%d')
                fhasta = datetime.datetime.strptime(fechafin, '%Y-%m-%d')
                if fhasta < datetime.datetime.now() or fdesde > datetime.datetime.now():
                    continue
                if (float(line.price_discount<>0)):
                    tipodto = 'N'
                    #solo registramos los que dejan el precio a cero para poner un precio especial
                    if abs(line.price_discount)==1:
                        valor = float(line.price_surcharge)
                    else:
                        continue
                else:
                    continue

                codclialt =''
                coddiralt =''
                codprovalt=''
                                     
                fields_fields_710 = [               
                cocliente,  
                codireccion,      
                codproducto,
                tipodto,
                valor, 
                fechainicio,
                fechafin,
                codclialt,
                coddiralt,
                codprovalt,
                 ]
                #_logger.error('##### AIKO ###### En 710 registrando valores:%s'%fields_fields_710)
                fields_710 = ';'.join(['%s' % one_field for one_field in fields_fields_710])
                output += fields_710.encode('CP1252') + '\n'

                #pero esto mismo hay que repetirlo para todos los clientes que sean hijos de este partner
                search_condition = [('parent_id','=',partner_id.id)]
                parent_id_srch = partner_obj.search(cr, uid, search_condition)
                for cli in parent_id_srch:
                    partner_brw = partner_obj.browse(cr, uid, cli)
                    codireccion = str(partner_brw.id).zfill(9)

                    fields_fields_710 = [               
                    cocliente,  
                    codireccion,      
                    codproducto,
                    tipodto,
                    valor, 
                    fechainicio,
                    fechafin,
                    codclialt,
                    coddiralt,
                    codprovalt,
                     ]
                    #_logger.error('##### AIKO ###### En 710 registrando valores:%s'%fields_fields_710)
                    fields_710 = ';'.join(['%s' % one_field for one_field in fields_fields_710])
                    output += fields_710.encode('CP1252') + '\n'

        
    filename = '/var/ftp/ERP/PROMOCION'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return
#======================= 711 Obsequios ========================================

def _create_report711(self, cr, uid, ids, context=None):
#  Sin definir 
    return
#===================== 7XX             ========================================
def _create_report712(self, cr, uid, ids, context=None):
#  Sin definir 
    return
#====================== 7XX             ========================================
def _create_report713(self, cr, uid, ids, context=None):
#  Sin definir 
    return

#==================== 714 cabecera reparto       ===============================
def _create_report714(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('sale.order')
    search_condition = [('state','=', 'manual')]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
                                 

    output = ''
    for saleorder in part_selec_obj:
        line = par_obj.browse(cr, uid, saleorder)
        
        numdocumento= str(line.id).zfill(20)  
        fechadocumento= datetime.datetime.now().strftime("%Y-%m-%d")
        tipodocumento= '8'
        codempresa= str(line.company_id.id).zfill(9) if  line.company_id.id  else  '1'

        #codigoruta= str(line.partner_id.tercap_ruta_id.id).zfill(4) if  line.partner_id.tercap_ruta_id.id  else '0000'
        #Manuel modificado el 28-3-16 para tomar el valor de codigo de Ruta de Tercap
        codigoruta= str(line.partner_id.tercap_ruta_id.cod_tercap).zfill(4) if  line.partner_id.tercap_ruta_id.cod_tercap  else '0000'
        #Manuel 11-2-16 cambiamos el campo de res.partner comercial al de crm.case.section de equipo de ventas
        #codvendedor= str(line.partner_id.user_id.id).zfill(9)  if  line.partner_id.user_id.id else '000000000'
        codvendedor= str(line.section_id.id).zfill(9)  if  line.section_id else '000000000'              
        codcliente= str(line.partner_id.id).zfill(9)
        coddireccion='000000000'
        fechaentrega= datetime.datetime.now().strftime("%Y-%m-%d")
        codcliealternativo = ' '
        coddirealternativo = ' '
        documentoorigen= ' '
        base1 = str(line.amount_untaxed).zfill(10)
        base2= 0000000000
        base3= 0000000000
        descuento= 0000000000
        descuentopp= 0000000000
        iva1= str(line.amount_tax).zfill(10)
        iva2= 0000000000
        iva3= 0000000000
        importerecargo1= 0000000000
        importerecargo2= 0000000000
        importerecargo3= 0000000000
        totaldocumento= str(line.amount_total).zfill(10)
        
 
            
        fields_fields_714 = [                            
        numdocumento,
        fechadocumento,    
        tipodocumento,   
        codempresa,       
        codigoruta,     
        codvendedor,              
        codcliente,       
        coddireccion,     
        fechaentrega,      
        codcliealternativo,
        coddirealternativo,
        documentoorigen,    
        base1,     
        base2,
        base3,    
        descuento,   
        descuentopp, 
        iva1,   
        iva2,   
        iva3,    
        importerecargo1,   
        importerecargo2,    
        importerecargo3,   
        totaldocumento,
         ]
        
        fields_714 = ';'.join(['%s' % one_field for one_field in fields_fields_714])
        output += fields_714.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/PEDIDOCAB'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()    
    return
#=================== 715 lineas pedido reparto        ==========================
def _create_report715(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('sale.order')
    lin_obj = self.pool.get('sale.order.line')
    
    search_condition = [('state','=', 'manual')]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
    #ampliado por Manuel el 12-2-16 para controlar precios con y sin iva incluido
    tax_obj = self.pool.get('account.tax')

    output = ''
    num = 0
    for saleorder in part_selec_obj:
        sale = par_obj.browse(cr, uid, saleorder)
        if sale.order_line:
            #for line in lin_selec_obj:
            for orderline in lin_obj.search(cr, uid, [('id','=', sale.id)] ):
                line = lin_obj.browse(cr, uid, orderline)
                
                numdocumento= str(sale.id).zfill(20)  
                fechadocumento= datetime.datetime.now().strftime("%Y-%m-%d")
                tipodocumento= '8'
                numlinea = str(num + 1).zfill(9)
                tipodelinea='1'
                codproducto=  str(line.product_id.id).zfill(9)
                descripcion= line.product_id.name.ljust(50)[:50] if line.product_id.name else ' '
                unidadventa = line.product_uos.tercap_unit if  line.product_uos.tercap_unit else 'U'
                lote = '    '
                cantidad = str(line.product_uom_qty).zfill(10) if line.product_uom_qty else '0'
                cajas = str(line.product_uom.factor_inv).zfill(10) if line.product_uom.factor_inv else '1'
                pesounidad = str(line.th_weight).zfill(10) if line.th_weight else '0'
                pesototal = str(line.th_weight * line.product_uom_qty).zfill(10)
                #para controlar el tipo de iva del producto
                search_condition = [('id', '=', line.product_id.taxes_id.id)]
                tpiva = tax_obj.search(cr, uid, search_condition)
                if (len(tpiva)==0):
                    raise osv.except_osv(('Error!'),('No se ha definido el tipo de iva aplicable al producto %s'%descripcion))
                tipoimp = tax_obj.browse(cr, uid, tpiva[0])
                #si los precios son con iva descontamos el tipo de iva
                if (tipoimp.price_include):
                    preciosin = line.price_unit / (1+tipoimp.amount)
                    precio= str(preciosin).zfill(10)
                else:
                    precio= str(line.price_unit).zfill(10) if line.price_unit else '0'
                
                descuento1 = str(line.discount).zfill(10) if line.discount else '0'
                descuento2='0'
                precioneto=str(line.price_subtotal).zfill(10) if line.price_subtotal else '0'
                preciomanal='N'
                iva = 0
                recargo = 0
                importeiva = 0
                importerecargo = 0 
                if line.tax_id:
                    for t in line.tax_id:
                        if t.tercap_codiva == '1': 
                            iva = str(t.amount*100).zfill(10)
                            importeiva= str(line.price_subtotal * t.amount or 0.0).zfill(10) 
                        elif  t.tercap_codiva == '5': 
                            recargo = str(t.amount*100).zfill(10) 
                            importerecargo= str(line.price_subtotal * t.amount or 0.0).zfill(10) 
                codproalternativo= '   '
                  
                fields_fields_715 = [                            
                numdocumento,  
                fechadocumento,
                tipodocumento,
                numlinea,
                tipodelinea,
                codproducto,
                descripcion.rstrip(), 
                unidadventa,
                lote,
                cantidad,
                cajas,
                pesounidad,
                pesototal,
                precio,
                descuento1,
                descuento2,
                precioneto,
                preciomanal,
                iva,
                recargo,
                importeiva,
                importerecargo,
                codproalternativo,
                ]
        
                fields_715 = ';'.join(['%s' % one_field for one_field in fields_fields_715])
                output += fields_715.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/PEDIDOLIN'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return
#=================== 716 Rutero              ==================================
def _create_report716(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('ruta')
    search_condition = [('tercap_incluir', '=', True)]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
 
    output = ''
    for ruta in part_selec_obj:
        visita = 0                          
        line = par_obj.browse(cr, uid, ruta)
        if line.partner_rutas_ids:
            for c in line.partner_rutas_ids: 
                #Manuel modificado el 28-3-16 para usar el codigo de ruta de Tercap
                #codruta= str(line.id).zfill(4)
                codruta= str(line.cod_tercap).zfill(4)
                codcliente= str(c.id).zfill(9)
                coddireccion = str(c.id).zfill(9)
                diavisita = str(line.dias_visita).zfill(9) if line.dias_visita else '000000000'
                #19-4-16 se gestiona un nuevo campo en la ficha de cliente: el orden de visita en el dia
                if (c.orden_visita<>0):
                    ordenvisita = str(int(c.orden_visita)).zfill(9)
                else: 
                    ordenvisita = str(visita + 1).zfill(9)               
                frecuencia = line.frecuencia if line.frecuencia else 'S'
                codclialternativo = ' '
                coddirealternativo = ' '
    
                fields_fields_716 = [
                codruta,
                codcliente,
                coddireccion,
                diavisita,
                ordenvisita,
                frecuencia,
                codclialternativo,
                coddirealternativo,                   
                              ]       
                fields_716 = ';'.join(['%s' % one_field for one_field in fields_fields_716])
                output += fields_716.encode('CP1252') + '\n'
        
    filename = '/var/ftp/ERP/RUTERO'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return
#============================= 7XX             ========================================
def _create_report717(self, cr, uid, ids, context=None):
#  Sin definir 
    return

#============================= 7XX             ========================================
def _create_report718(self, cr, uid, ids, context=None):
#  Sin definir 
    return

#============================= 7XX             ========================================
def _create_report719(self, cr, uid, ids, context=None):
#  Sin definir 
    return

#======================= 720 Proveedor  =======================================
def _create_report720(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('res.partner')
    search_condition = [('active', '=', True),('supplier','=', True)]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
                                 

    output = ''
    for proveedor in part_selec_obj:
        line = par_obj.browse(cr, uid, proveedor)
        codproveedor= str(line.id).zfill(10) 
        nombrecomercial = unicode(line.name.ljust(50)[:50]).replace("\"","\'") if line.name else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        nombrecomercial = nombrecomercial.replace(";",",")
        direccion=unicode(line.street.ljust(50)[:50]).replace("\"","\'") if line.street else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        direccion = direccion.replace(";",",")
        poblacion=line.city.ljust(50)[:50] if line.city else ' '
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        poblacion = unicode(poblacion).replace(";",",")
        codpostal=line.zip.ljust(5)[:5] if line.zip else '00000'
        provincia= line.state_id.name.ljust(25)[:25] if line.state_id.name else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        provincia = unicode(provincia).replace(";",",")
        cifnif=line.vat.ljust(10)[:10] if line.vat else ' '
        usarcodprocliente='N'


        fields_fields_720 = [
        codproveedor,
        nombrecomercial.rstrip(),  
        direccion.rstrip(),  
        poblacion.rstrip(),  
        codpostal, 
        provincia.rstrip(),  
        cifnif, 
        usarcodprocliente,              
                              ]
        
        fields_720 = ';'.join(['%s' % one_field for one_field in fields_fields_720])
        output += fields_720.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/PROVEEDORES'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return

#===================== 721 rutas       ========================================
def _create_report721(self, cr, uid, ids, context=None):
    if context is None:
        context = {}

    par_obj = self.pool.get('ruta')
    #search_condition = [('tercap_incluir', '=', True)]
    #part_selec_obj = par_obj.search(cr, uid, search_condition )

    output = ''

    #06-04-16 variable para exportar solo las rutas de Tercap de distinto codigo
    cr.execute("""SELECT DISTINCT cod_tercap FROM ruta WHERE tercap_incluir order by cod_tercap""")
    dist_ruta = cr.fetchall()
#    _logger.error('##### AIKO ###### En 721 rutas obtengo valor de dist_ruta:%s'%dist_ruta)

    for dist in dist_ruta:
#        _logger.error('##### AIKO ###### En 721 rutas obtengo valor de cod_tercap:%s'%dist)
        search_condition =[('cod_tercap','in',dist)]
        line_ser = par_obj.search(cr,uid,search_condition)
        if len(line_ser)==0:
            break
        line = par_obj.browse(cr, uid, line_ser[0])
#        _logger.error('##### AIKO ###### En 721 rutas entro en objeto:%s'%line)

        #Manuel 28-3-16 modificado para usar el codigo Tercap de la ruta
        #codruta= str(line.id).zfill(4)

        codruta= str(line.cod_tercap).zfill(4)
        #6-4-16 se toma el mismo valor del codigo de tercap para la descripcion  
        #descripcion= unicode(line.descripcion.ljust(50)[:50]).replace("\"","\'") if line.descripcion else  ' ' 
        descripcion = str(line.descripcion)
        #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        descripcion = descripcion.replace(";",",")
        tipo= line.tipo if line.tipo else 'R' 
        #29-3-16 se traspasa el dato del equipo de ventas en lugar del vendedor
        #cod_vendedor=str(line.cod_vendedor.id).zfill(9) if line.cod_vendedor.id else '000000000' 
        cod_vendedor=str(line.cod_equipo.id).zfill(9) if line.cod_equipo else '000000000'
        clave_config=str(line.clave_config).ljust(10)[:10] if line.clave_config else '          ' 
        permitir_venta_lotes= line.permitir_venta_lotes if line.permitir_venta_lotes  else 'S'
        permitir_venta_cajas=  line.permitir_venta_cajas  if  line.permitir_venta_cajas   else 'S'
        cajas_por_defecto=  line.cajas_por_defecto if line.cajas_por_defecto else  'N'
        Permitir_cambio_precio= line.Permitir_cambio_precio  if  line.Permitir_cambio_precio  else  'S'
        aviso_riesgo=  line.aviso_riesgo if  line.aviso_riesgo   else 'N'
        permitir_cambio_pago= line.permitir_cambio_pago if line.permitir_cambio_pago else 'S'
        aplicar_dto_sincab= line.aplicar_dto_sincab if line.aplicar_dto_sincab  else  'N'
        permitir_cliente_nuevo= line.permitir_cliente_nuevo  if line.permitir_cliente_nuevo else  'S'
        permite_cambio_vendedor= line.permite_cambio_vendedor  if  line.permite_cambio_vendedor   else 'S'
        aplicar_cond_retiradas= line.aplicar_cond_retiradas if  line.aplicar_cond_retiradas   else 'S'
        pedir_lote_retiradas= line.pedir_lote_retiradas if line.pedir_lote_retiradas  else 'N'
        permitir_cobros= line.permitir_cobros if  line.permitir_cobros   else 'S'
        ecotasa_en_precio=  line.ecotasa_en_precio if line.ecotasa_en_precio   else  'N'
        ecotasa_en_regalos=  line.ecotasa_en_regalos if line.ecotasa_en_regalos   else 'N'
        ecotasa_sin_cab= line.ecotasa_sin_cab if  line.ecotasa_sin_cab  else 'N'
        perguntar_tipo_doc= line.perguntar_tipo_doc  if line.perguntar_tipo_doc  else   'N' 
        pedir_peso_en_linea= line.pedir_peso_en_linea  if line.pedir_peso_en_linea   else 'S'
        permitir_venta_sin_stock= line.permitir_venta_sin_stock if  line.permitir_venta_sin_stock  else 'S'
        permitir_descarga_parcial= line.permitir_descarga_parcial  if line.permitir_descarga_parcial else 'S'
        imprimir_albaran_con_iva= line.imprimir_albaran_con_iva if line.imprimir_albaran_con_iva  else 'S'
        imprimir_cabecera= line.imprimir_cabecera if  line.imprimir_cabecera else  'S'
        imprimir_corregido= line.imprimir_corregido  if line.imprimir_corregido else 'N'
        imprimir_anulado= line.imprimir_anulado if line.imprimir_anulado else  'N' 
        orden_productos= line.orden_productos if  line.orden_productos else  'N'
        es_proveedor_mayorista= line.es_proveedor_mayorista if line.es_proveedor_mayorista else 'N'
        
  
        fields_fields_721 = [
        codruta,  
        descripcion.rstrip(),    
        tipo,            
        cod_vendedor, 
        clave_config,     
        permitir_venta_lotes,   
        permitir_venta_cajas,
        cajas_por_defecto,            
        Permitir_cambio_precio,
        aviso_riesgo,                    
        permitir_cambio_pago,    
        aplicar_dto_sincab,             
        permitir_cliente_nuevo,
        permite_cambio_vendedor,
        aplicar_cond_retiradas,       
        pedir_lote_retiradas,
        permitir_cobros,           
        ecotasa_en_precio,
        ecotasa_en_regalos,            
        ecotasa_sin_cab,             
        perguntar_tipo_doc,             
        pedir_peso_en_linea,               
        permitir_venta_sin_stock,
        permitir_descarga_parcial,
        imprimir_albaran_con_iva,         
        imprimir_cabecera,              
        imprimir_corregido,           
        imprimir_anulado,          
        orden_productos,              
        es_proveedor_mayorista,                               
                              ]       
        fields_721 = ';'.join(['%s' % one_field for one_field in fields_fields_721])
        output += fields_721.encode('CP1252') + '\n'
#        _logger.error('##### AIKO ###### En 721 rutas tengo linea:%s'%output)
#            output += sale_invoice + '\n'
       
    filename = '/var/ftp/ERP/RUTAS'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return


#==============================================================================
''' MODIFICADO POR MANUEL 11-2-16 PARA USAR EQUIPOS DE VENTAS
#======================== 722 vendedores ======================================
def _create_report722(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('res.partner')
    search_condition = [('active', '=', True),('tercap_vendedor','=', True)]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
 
    output = ''
    for vendedor in part_selec_obj:
        line = par_obj.browse(cr, uid, vendedor)
        codvendedor= str(line.id).zfill(9) 
        nombre = line.name.ljust(50)[:50] if line.name else  ' ' 
        permitircambioprecio='S'
  
        fields_fields_722 = [
        codvendedor, 
        nombre.rstrip(), 
        permitircambioprecio,
                              ]       
        fields_722 = ';'.join(['%s' % one_field for one_field in fields_fields_722])
        output += fields_722.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/VENDEDORES'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return
'''
#================Mod. 11-2-16 722 vendedores(equipos de vtas) ==================
def _create_report722(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('crm.case.section')
    search_condition = [('active', '=', True)]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
 
    output = ''
    for equipo in part_selec_obj:
        line = par_obj.browse(cr, uid, equipo)
        codvendedor= str(line.id).zfill(9) 
        nombre = unicode(line.name.ljust(50)[:50]).replace("\"","\'") if line.name else  ' ' 
         #21-3-16 agregamos una sustitucion adicional para evitar el caracter ;
        nombre = nombre.replace(";",",")
        #desde 11-2-16 modificado el modelo de crm.case.section para que incluya este campo
        #permitircambioprecio='S'
        if (line.tercap_permitircambioprecio):
            permitircambioprecio='S'
        else:
            permitircambioprecio='N'
            
        fields_fields_722 = [
        codvendedor, 
        nombre.rstrip(), 
        permitircambioprecio,
                              ]       
        fields_722 = ';'.join(['%s' % one_field for one_field in fields_fields_722])
        output += fields_722.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/VENDEDORES'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return

#======================= 7XX             ======================================
def _create_report723(self, cr, uid, ids, context=None):
#  Sin definir 
    return

#===================== 724 cabeceras de cargas =================================
def _create_report724(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('sale.order')
    search_condition = [('state','=', 'manual')]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
                                 

    output = ''
    for saleorder in part_selec_obj:
        line = par_obj.browse(cr, uid, saleorder)
        
        numdocumento= str(line.id).zfill(20)  
        fechadocumento= datetime.datetime.now().strftime("%Y-%m-%d")
        tipodocumento= '5'
        codempresa= str(line.company_id.id).zfill(9) if  line.company_id.id  else  '1'
        #Manuel modificado el 28-3-16 para usar el codigo de ruta de Tercap
        #codigoruta= str(line.partner_id.tercap_ruta_id.id).zfill(4) if  line.partner_id.tercap_ruta_id.id  else '0000'
        codigoruta= str(line.partner_id.tercap_ruta_id.cod_tercap).zfill(4) if  line.partner_id.tercap_ruta_id.cod_tercap  else '0000'
        codvendedor= str(line.partner_id.user_id.id).zfill(9)  if  line.partner_id.user_id.id else '000000000'            
        codcliente= str(line.partner_id.id).zfill(9)
        coddireccion='000000000'
        fechaentrega= datetime.datetime.now().strftime("%Y-%m-%d")
        codcliealternativo = ' '
        coddirealternativo = ' '
        documentoorigen= ' '
        base1 = str(line.amount_untaxed).zfill(10)
        base2= 0000000000
        base3= 0000000000
        descuento= 0000000000
        descuentopp= 0000000000
        iva1= str(line.amount_tax).zfill(10)
        iva2= 0000000000
        iva3= 0000000000
        importerecargo1= 0000000000
        importerecargo2= 0000000000
        importerecargo3= 0000000000
        totaldocumento= str(line.amount_total).zfill(10)
        
 
            
        fields_fields_724 = [                            
        numdocumento,
        fechadocumento,    
        tipodocumento,   
        codempresa,       
        codigoruta,     
        codvendedor,              
        codcliente,       
        coddireccion,     
        fechaentrega,      
        codcliealternativo,
        coddirealternativo,
        documentoorigen,    
        base1,     
        base2,
        base3,    
        descuento,   
        descuentopp, 
        iva1,   
        iva2,   
        iva3,    
        importerecargo1,   
        importerecargo2,    
        importerecargo3,   
        totaldocumento,
         ]
        
        fields_724 = ';'.join(['%s' % one_field for one_field in fields_fields_724])
        output += fields_724.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/CARGACAB'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    
    return
#================== 725 lineas de cargas mercancias   ==========================
def _create_report725(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    par_obj = self.pool.get('sale.order')
    lin_obj = self.pool.get('sale.order.line')
    
    search_condition = [('state','=', 'manual')]
    part_selec_obj = par_obj.search(cr, uid, search_condition )
    #ampliado por Manuel el 12-2-16 para controlar precios con y sin iva incluido
    tax_obj = self.pool.get('account.tax')

    output = ''
    num = 0
    for saleorder in part_selec_obj:
        sale = par_obj.browse(cr, uid, saleorder)
        if sale.order_line:
            #for line in lin_selec_obj:
            for orderline in lin_obj.search(cr, uid, [('id','=', sale.id)] ):
                line = lin_obj.browse(cr, uid, orderline)
                
                numdocumento= str(sale.id).zfill(20)  
                fechadocumento= datetime.datetime.now().strftime("%Y-%m-%d")
                tipodocumento= '5'
                numlinea = str(num + 1).zfill(9)
                tipodelinea='20'
                codproducto=  str(line.product_id.id).zfill(9)
                descripcion= line.product_id.name.ljust(50)[:50] if line.product_id.name else ' '
                unidadventa = line.product_uos.tercap_unit if  line.product_uos.tercap_unit else 'U'
                lote = '    '
                cantidad = str(line.product_uom_qty).zfill(10) if line.product_uom_qty else '0'
                cajas = str(line.product_uom.factor_inv).zfill(10) if line.product_uom.factor_inv else '1'
                pesounidad = str(line.th_weight).zfill(10) if line.th_weight else '0'
                pesototal = str(line.th_weight * line.product_uom_qty).zfill(10)
                #para controlar el tipo de iva del producto
                search_condition = [('id', '=', line.product_id.taxes_id.id)]
                tpiva = tax_obj.search(cr, uid, search_condition)
                if (len(tpiva)==0):
                    raise osv.except_osv(('Error!'),('No se ha definido el tipo de iva aplicable al producto %s'%descripcion))
                tipoimp = tax_obj.browse(cr, uid, tpiva[0])
                #si los precios son con iva descontamos el tipo de iva
                if (tipoimp.price_include):
                    preciosin = line.price_unit / (1+tipoimp.amount)
                    precio= str(preciosin).zfill(10)
                else:
                    precio= str(line.price_unit).zfill(10) if line.price_unit else '0'
                
                descuento1 = str(line.discount).zfill(10) if line.discount else '0'
                descuento2='0'
                precioneto=str(line.price_subtotal).zfill(10) if line.price_subtotal else '0'
                preciomanal='N'
                iva = 0
                recargo = 0
                importeiva = 0
                importerecargo = 0 
                if line.tax_id:
                    for t in line.tax_id:
                        if t.tercap_codiva == '1': 
                            iva = str(t.amount*100).zfill(10)
                            importeiva= str(line.price_subtotal * t.amount or 0.0).zfill(10) 
                        elif  t.tercap_codiva == '5': 
                            recargo = str(t.amount*100).zfill(10) 
                            importerecargo= str(line.price_subtotal * t.amount or 0.0).zfill(10) 
                codproalternativo= '   '
                  
                fields_fields_725 = [                            
                numdocumento,  
                fechadocumento,
                tipodocumento,
                numlinea,
                tipodelinea,
                codproducto,
                descripcion.rstrip(), 
                unidadventa,
                lote,
                cantidad,
                cajas,
                pesounidad,
                pesototal,
                precio,
                descuento1,
                descuento2,
                precioneto,
                preciomanal,
                iva,
                recargo,
                importeiva,
                importerecargo,
                codproalternativo,
                ]
        
                fields_725 = ';'.join(['%s' % one_field for one_field in fields_fields_725])
                output += fields_725.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/CARGALIN'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()    
    return

#================== 726 Stock   ==========================creado el 26-4-16
def _create_report726(self, cr, uid, ids, context=None):
    if context is None:
        context = {}

    '''

     #variable para obtener los distintos productos del stock y poder sumar quants
    cr.execute("""SELECT DISTINCT product_id FROM stock_history""")
    nprod_id = cr.fetchall()

    stock_obj = self.pool.get('stock.history')
    product_obj = self.pool.get('product.product')
    output = ''

    for prod in nprod_id:
        codruta ='99'
        search_condition = [('id', 'in', prod)]
        prod_selec_obj = product_obj.search(cr, uid, search_condition)
        codproducto = product_obj.browse(cr, uid, prod_selec_obj).default_code
        if (codproducto == False):
            continue
        lote=''
        search_condition = [('product_id', 'in', prod)]
        stock_ob_prod = stock_obj.search(cr,uid,search_condition)
        cantidad = 0
        for st in stock_ob_prod:
            cantidad += stock_obj.browse(cr,uid,st).quantity
        pesototal ='0.000'
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        codvendedor= '0'


    #product_obj = self.pool.get('product.product')   

    ''' 

    #modificado el 7-6-16 para que muestre el stock real de cada producto a la venta
    output = ''
    #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
    product_obj = self.pool.get('product.product')
    tmpl_obj = self.pool.get('product.template')
    search_condition =[('sale_ok','=',True)]
    product_vta = product_obj.search(cr, uid, search_condition)
    codproducto = 0

    #ampliado el 9-9-16 para controlar el tipo de codigo de producto al exportar
    #localizamos el directorio de importacion y como tiene definido el valor de product_default_idcode
    directory_obj = self.pool['tercap.route']
    search_condition = [('alcance', '=', 'import')]
    direct_imp_obj = directory_obj.search(cr, uid, search_condition)
    codigo_default = directory_obj.browse(cr, uid, direct_imp_obj[0]).product_default_idcode

    for pr in product_vta:
        product_brw = product_obj.browse(cr, uid, pr)
        #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
        search_condition = [('id', '=', product_brw.product_tmpl_id.id)]
        product_tmpl = tmpl_obj.search(cr, uid, search_condition)
        if len (product_tmpl)==0:
            raise osv.except_osv(('Error!'),('No se encuentra identificador en stock para el producto %s'%product_brw.product_tmpl_id))

        #modificado el 9-9-16 para controlar el tipo de valor a exportar, si es True pasamos como codproducto el default code
        #si no se comunica el id de Odoo
        if codigo_default:
            if not product_brw.default_code:
                #si no tiene default_code enviamos el id sumando 900 000 000 para que no se repitan con default_code
                codproducto= 900000000 + int(float(product_brw.id))
                #_logger.error('##### AIKO ###### En 726 stockR entero de id product sin default_code:%s'%int(float(product_brw.id)))
                #_logger.error('##### AIKO ###### En 726 stockR codproducto sin default_code:%s'%codproducto)
            else:
                codproducto= unicode(product_brw.default_code).strip()
                if (len (codproducto)<9) and (codproducto.isdigit()) and (int(codproducto) < 99999999):
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna entero:%s'%codproducto)
                    codproducto= codproducto.zfill(9)
                else:
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna no numerico:%s'%codproducto)
                    #si no es un numero enviamos el id sumando 900 000 000 para que no se repitan con default_code
                    codproducto= 900000000 + int(float(product_brw.id))
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna no numerico queda en:%s'%codproducto)
        #modificacion del 9-9-16: si no esta marcado vamos a enviar en codproducto el id de Odoo.
        else:
            codproducto= str(product_brw.id).zfill(9)

        #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
        prod_tmpl = tmpl_obj.browse(cr, uid, product_tmpl[0])
        
        codruta ='99'
        lote=''
        #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
        #cantidad = product_brw.qty_available
        #pesototal = product_brw.weight * cantidad
        cantidad = prod_tmpl.qty_available
        pesototal = prod_tmpl.weight * cantidad

        fecha = datetime.date.today().strftime('%Y-%m-%d')
        codvendedor= '0'

        fields_fields_726 = [
        codruta,
        codproducto, 
        lote,
        cantidad,
        pesototal,
        fecha,
        codvendedor,
        ]

        #_logger.error('##### AIKO ###### En 726 stock registro valores:%s'%fields_fields_726)     
        fields_726 = ';'.join(['%s' % one_field for one_field in fields_fields_726])
        output += fields_726.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/STOCK'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return


#================== 726V Stock  Virtual ==========================creado el 24-06-16
def _create_report726V(self, cr, uid, ids, context=None):
    if context is None:
        context = {}

    #modificado el 24-6-16 para que muestre el stock virtual de cada producto a la venta
    output = ''
    #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
    product_obj = self.pool.get('product.product')
    tmpl_obj = self.pool.get('product.template')
    search_condition =[('sale_ok','=',True)]
    product_vta = product_obj.search(cr, uid, search_condition)

    #ampliado el 9-9-16 para controlar el tipo de codigo de producto al exportar
    #localizamos el directorio de importacion y como tiene definido el valor de product_default_idcode
    directory_obj = self.pool['tercap.route']
    search_condition = [('alcance', '=', 'import')]
    direct_imp_obj = directory_obj.search(cr, uid, search_condition)
    codigo_default = directory_obj.browse(cr, uid, direct_imp_obj[0]).product_default_idcode

    for pr in product_vta:
        product_brw = product_obj.browse(cr, uid, pr)
        #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
        search_condition = [('id', '=', product_brw.product_tmpl_id.id)]
        product_tmpl = tmpl_obj.search(cr, uid, search_condition)
        if len (product_tmpl)==0:
            raise osv.except_osv(('Error!'),('No se encuentra identificador en stock para el producto %s'%product_brw.product_tmpl_id))

        #modificado el 9-9-16 para controlar el tipo de valor a exportar, si es True pasamos como codproducto el default code
        #si no se comunica el id de Odoo
        if codigo_default:
            if not product_brw.default_code:
                #si no tiene default_code enviamos el id sumando 900 000 000 para que no se repitan con default_code
                codproducto= 900000000 + int(float(product_brw.id))
                #_logger.error('##### AIKO ###### En 726 stockR entero de id product sin default_code:%s'%int(float(product_brw.id)))
                #_logger.error('##### AIKO ###### En 726 stockR codproducto sin default_code:%s'%codproducto)
            else:
                codproducto= unicode(product_brw.default_code).strip()
                if (len (codproducto)<9) and (codproducto.isdigit()) and (int(codproducto) < 99999999):
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna entero:%s'%codproducto)
                    codproducto= codproducto.zfill(9)
                else:
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna no numerico:%s'%codproducto)
                    #si no es un numero enviamos el id sumando 900 000 000 para que no se repitan con default_code
                    codproducto= 900000000 + int(float(product_brw.id))
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna no numerico queda en:%s'%codproducto)
        #modificacion del 9-9-16: si no esta marcado vamos a enviar en codproducto el id de Odoo.
        else:
            codproducto= str(product_brw.id).zfill(9)
        
        #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
        prod_tmpl = tmpl_obj.browse(cr, uid, product_tmpl[0])

        codruta ='99'
        lote=''
        #cantidad = product_brw.virtual_available
        #pesototal = product_brw.weight * cantidad
        cantidad = prod_tmpl.virtual_available
        pesototal = prod_tmpl.weight * cantidad
        
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        codvendedor= '0'

        fields_fields_726 = [
        codruta,
        codproducto, 
        lote,
        cantidad,
        pesototal,
        fecha,
        codvendedor,
        ]

        #_logger.error('##### AIKO ###### En 726V stock registro valores:%s'%fields_fields_726)     
        fields_726 = ';'.join(['%s' % one_field for one_field in fields_fields_726])
        output += fields_726.encode('CP1252') + '\n'
#            output += sale_invoice + '\n'
        
    filename = '/var/ftp/ERP/STOCK'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return

    #================== 726Lote Stock  para Lotes ==========================creado el 09-11-16
def _create_report726L(self, cr, uid, ids, context=None):
    if context is None:
        context = {}

    #creado el 09-11-16 para obtener simplemente un listado de todos los productos con sus lotes y 
    #existencias en stock hipoteticas de 1000 uds: supone que no hay control de stocks.
    output = ''
    #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
    product_obj = self.pool.get('product.product')
    tmpl_obj = self.pool.get('product.template')
    search_condition =[('sale_ok','=',True)]
    product_vta = product_obj.search(cr, uid, search_condition)

    #ampliado el 9-9-16 para controlar el tipo de codigo de producto al exportar
    #localizamos el directorio de importacion y como tiene definido el valor de product_default_idcode
    directory_obj = self.pool['tercap.route']
    search_condition = [('alcance', '=', 'import')]
    direct_imp_obj = directory_obj.search(cr, uid, search_condition)
    codigo_default = directory_obj.browse(cr, uid, direct_imp_obj[0]).product_default_idcode

    #para los lotes necesitamos un objeto mas:
    lots_obj = self.pool['stock.production.lot']

    for pr in product_vta:
        product_brw = product_obj.browse(cr, uid, pr)
        #detectado el 20-10-16 pasa el id del template cuando el product se identifica con el id de product
        search_condition = [('id', '=', product_brw.product_tmpl_id.id)]
        product_tmpl = tmpl_obj.search(cr, uid, search_condition)
        if len (product_tmpl)==0:
            raise osv.except_osv(('Error!'),('No se encuentra identificador en stock para el producto %s'%product_brw.product_tmpl_id))

        #modificado el 9-9-16 para controlar el tipo de valor a exportar, si es True pasamos como codproducto el default code
        #si no se comunica el id de Odoo
        if codigo_default:
            if not product_brw.default_code:
                #si no tiene default_code enviamos el id sumando 900 000 000 para que no se repitan con default_code
                codproducto= 900000000 + int(float(product_brw.id))
                #_logger.error('##### AIKO ###### En 726 stockR entero de id product sin default_code:%s'%int(float(product_brw.id)))
                #_logger.error('##### AIKO ###### En 726 stockR codproducto sin default_code:%s'%codproducto)
            else:
                codproducto= unicode(product_brw.default_code).strip()
                if (len (codproducto)<9) and (codproducto.isdigit()) and (int(codproducto) < 99999999):
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna entero:%s'%codproducto)
                    codproducto= codproducto.zfill(9)
                else:
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna no numerico:%s'%codproducto)
                    #si no es un numero enviamos el id sumando 900 000 000 para que no se repitan con default_code
                    codproducto= 900000000 + int(float(product_brw.id))
                    #_logger.error('##### AIKO ###### En 726 stockR valor de ref interna no numerico queda en:%s'%codproducto)
        #modificacion del 9-9-16: si no esta marcado vamos a enviar en codproducto el id de Odoo.
        else:
            codproducto= str(product_brw.id).zfill(9)

        codruta ='99'
        cantidad = '1000.000'
        pesototal = '1000.000'
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        codvendedor= '0'

        #09-11-16 para cada producto repetimos todos los lotes
        search_condition = [('product_id', '=', product_brw.id)]
        lot_prod = lots_obj.search(cr, uid, search_condition)

        for lt in lot_prod:
            lt_brw = lots_obj.browse(cr, uid, lt)
            lote=lt_brw.name


            fields_fields_726L = [
            codruta,
            codproducto, 
            lote,
            cantidad,
            pesototal,
            fecha,
            codvendedor,
            ]

            #_logger.error('##### AIKO ###### En 726V stock registro valores:%s'%fields_fields_726)     
            fields_726L = ';'.join(['%s' % one_field for one_field in fields_fields_726L])
            output += fields_726L.encode('CP1252') + '\n'
        
    filename = '/var/ftp/ERP/STOCK'
    formato = 'txt'
    nombre = "%s.%s" % (filename, formato)
    #out = base64.encodestring(output)
    outfile = open(nombre, 'w')
    outfile.write(output)
    outfile.close()
    return