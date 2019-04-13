# -*- coding: utf-8 -*-


from openerp import models, fields, api
from openerp import tools

import requests, datetime, json

from lxml import etree

from requests.auth import HTTPBasicAuth

import logging 
_logger = logging.getLogger(__name__)


from openerp.osv import osv
#from openerp.tools.translate import _

class sale_order(models.Model):
    _inherit = "sale.order"

    de_tercap = fields.Boolean('Es pedido de Tercap')
    



class tercap_order(models.Model):
    _name = "tercap.order"
    
    @api.multi 
    def extraer_order_api_tercap(self):        
        recs = self.env['res.partner']                    
        rest_partner_obj = recs.search([])   
        sale_order= self.env['sale.order']      
        account_invoice = self.env['account.invoice']      
        sale_order_search = sale_order.search([]) 
        product_product= self.env['product.product'] 
        tax_position = self.env['account.fiscal.position']
        account_tax = self.env['account.tax']    
        salida_API = requests.get('https://odoo.tercap.net/api/v1/pedidoventaanidada?&format=json&estado=E', auth=HTTPBasicAuth('lider', 'lider'))
        lista_pedidos_tercap = salida_API.text
        lista_pedidos_tercap = lista_pedidos_tercap.replace("true","True")
        lista_pedidos_tercap = lista_pedidos_tercap.replace("null","False")
        lista_pedidos_tercap = lista_pedidos_tercap.replace("false","False")
        lista_pedidos_odoo = []
        lista_pedidos_tercap =eval(lista_pedidos_tercap)
        # _logger.error('##### AIKO ###### Valor de dato en lista_pedidos_tercap: %s' % lista_pedidos_tercap)
        for pedido in lista_pedidos_tercap:
          diccionario_odoo = {}
          lista_diccionarios_lineas = []
          for llave,valor in pedido.items():
              if llave =="lineas":
                # _logger.error('##### AIKO ###### Valor de valor en lineas: %s' % valor)
                lista_linea= []
                lista_linea= valor
                # lista_diccionarios_lineas = []
                for linea in lista_linea:
                  # _logger.error('##### AIKO ###### Valores de linea en la lista: %s' % linea)
                  diccionario_new_linea = {}

                  product_uom_qty = linea['cantidad']
                  try:
                    # product_uom_qty = int(product_uom_qty)
                    # cambiamos de entero a decimal con 3 decimales
                    # product_uom_qty = float("{0:.3f}".format(product_uom_qty))
                    product_uom_qty = float(product_uom_qty)
                    diccionario_new_linea['product_uom_qty'] = product_uom_qty
                  except:
                    # continue
                    diccionario_new_linea['product_uom_qty'] = 1

                  total_linea = linea['precio_neto']
                  try:
                    # total_linea = int(total_linea)
                    # cambiamos de entero a decimal con 3 decimales
                    # total_linea = float("{0:.3f}".format(total_linea))
                    total_linea = float(total_linea)
                    diccionario_new_linea['price_unit'] = total_linea
                  except:
                    # continue
                    diccionario_new_linea['price_unit'] = 1

                  dto_linea = linea['porcentaje_descuento']
                  try:
                    dto_linea = float(dto_linea)
                    diccionario_new_linea['discount'] = dto_linea
                  except:
                    pass

                  taxes = []
                  tipo_iva = linea['tipo_iva']
                  tax_producto = account_tax.search([('tercap_sat_codiva','=',tipo_iva)])
                  if len (tax_producto) ==0:
                    raise osv.except_osv(('Error!'),('No se han definido los tipos de IVA para TercapSAT, No se puede registrar'))
                  tax_recargo=0
                  recargo_linea = linea['porcentaje_recargo']
                  try:
                    recargo_linea = float(recargo_linea)
                    if recargo_linea != 0:
                      account_tax_recargo = account_tax.search([('amount','=',(ter_tprecargo/100)),('tercap_sat_codiva','!=','0')])
                      tax_recargo = account_tax_recargo[0].id
                  except:
                    pass
                  if tax_recargo !=0:
                    taxes =[tax_producto[0].id,tax_recargo]
                  else:
                    taxes =[tax_producto[0].id]

                  diccionario_new_linea['tax_id'] = [(6, 0, taxes)]

                  id_producto =linea['producto_id']
                  try:
                    id_producto = int(id_producto)
                    # nombre_producto = linea['nombre']
                    # product_id_producto_search = product_product.search([('id', '=', id_producto)])
                    # product_nombre_search = product_product.search([('name', '=', nombre_producto)])

                    # if product_id_producto_search:
                    #   print nombre_producto, id_producto, "IFFFFFFFFFf"
                    #   diccionario_new_linea['product_id'] = product_id_producto_search.id
                    # elif product_nombre_search:
                    #   print nombre_producto, id_producto, "ELIFFFFFFFFFf"
                    #   diccionario_new_linea['product_id'] = product_nombre_search.id
                    diccionario_new_linea['product_id'] = id_producto
                  except:
                    # continue
                    raise osv.except_osv(('Error!'),('Hay un error en el producto %s utilizado en el pedido, No se puede registrar' %linea['nombre']))

                  # _logger.error('##### AIKO ###### Valor de diccionario_new_linea antes del append: %s' % diccionario_new_linea)
                  lista_diccionarios_lineas.append(diccionario_new_linea)

                  # _logger.error('##### AIKO ###### Valor de dato en diccionario_lineas: %s' % lista_diccionarios_lineas)

              if llave =="numero":
                diccionario_odoo["name"]= valor
                # if diccionario_odoo["name"]:
                #        del diccionario_odoo["name"]

              elif llave =="cliente_id":
                # print 'CLIENTE',valor 
                # if valor != False or valor != "" or valor != " ":
                try:
                  valor = int(valor)
                  id_partner_para_odoo = recs.search([('id', '=', valor)])
                  if id_partner_para_odoo:
                    diccionario_odoo["partner_id"]= id_partner_para_odoo.id
                    print diccionario_odoo["partner_id"], id_partner_para_odoo
                  else:
                    diccionario_odoo["partner_id"]= 0
                except:
                    pass
                if diccionario_odoo["partner_id"]== 0:
                  # continue
                  raise osv.except_osv(('Error!'),('Hay un error en el cliente utilizado en el pedido, No se puede registrar'))

              elif llave =="codigo_vendedor":
                #print "VALOR", valor
                #if valor != False or valor != "" or valor != " ":
                try:
                  valor = int(valor)
                  id_vendedor_odoo = recs.search([('id', '=', valor)])
                  if id_vendedor_odoo:
                    diccionario_odoo["section_id"]= id_vendedor_odoo.id
                except:
                  pass

              elif llave =="direccion_id":
                # print "VALOR ID", valor
                # if valor != False or valor != "" or valor != " ":
                try:
                  valor = int(valor)
                  id_direccion_odoo = recs.search([('id', '=', valor)])
                  if id_direccion_odoo:
                    diccionario_odoo["partner_shipping_id"]= id_direccion_odoo.id

                except:
                  pass                                                                                      
                  
              #diccionario_odoo["partner_invoice_id"]= id_partner_para_odoo.id

              elif llave =="fecha":
                if valor != False or valor != "" or valor != " ":
                  valor = datetime.datetime.strptime(valor, '%Y-%m-%d').date()
                  diccionario_odoo["date_order"]= valor
                  #if diccionario_odoo["date_order"]:
                        #del diccionario_odoo["date_order"]

              elif llave =="forma_pago_id":
                # if valor != False or valor != "" or valor != " ":
                  # diccionario_odoo["payment_mode_id"]= valor
                  # if diccionario_odoo["payment_mode_id"]:
                        #del diccionario_odoo["payment_mode_id"]
                try:
                  valor = int(valor)
                  diccionario_odoo["payment_mode_id"]= valor
                except:
                  pass

              elif llave =="observaciones":
                if valor != False or valor != "" or valor != " ":
                  diccionario_odoo["note"]= valor

              elif llave =="porcentaje_descuento":
                if valor != False or valor != "" or valor != " ":
                  diccionario_odoo["global_discount"]= valor
                  # de momento no tratamos descuento global en presupuesto
                  if diccionario_odoo["global_discount"]:
                        del diccionario_odoo["global_discount"]

              elif llave =="referencia":
                if valor != False or valor != "" or valor != " ":
                  diccionario_odoo["origin"]= valor
                  # if diccionario_odoo["origin"]=="":
                  #   del diccionario_odoo["origin"]

              elif llave =="termino_pago_id":
                # if valor != False or valor != "" or valor != " ":
                #   diccionario_odoo["payment_term"]= valor
                  #if diccionario_odoo["payment_term"]==False:
                        #del diccionario_odoo["payment_term"]
                try:
                  valor = int(valor)
                  diccionario_odoo["payment_term"]= valor
                except:
                  pass

              elif llave =="tipo_fiscalidad":
                if valor != False or valor != "" or valor != " ":
                  tax_pedido = tax_position.search([('tercap_sat_tipo_iva','=',valor)])
                  if tax_pedido:
                    diccionario_odoo["fiscal_position"]= tax_pedido.id
                  else:
                    # continue
                    raise osv.except_osv(('Error!'),('No se han definido las posiciones fiscales para Tercap. No se puede registrar'))

                  #if diccionario_odoo["fiscal_position"]:
                        ##del diccionario_odoo["fiscal_position"]
                  # if diccionario_odoo["fiscal_position"] == "N":
                  #   diccionario_odoo["fiscal_position"]= 1              
                  # else:
                  #  diccionario_odoo["fiscal_position"]= 2

              elif llave =="total":
                if valor != False or valor != "" or valor != " ":
                  diccionario_odoo["amount_total"]= valor

                  # if diccionario_odoo["amount_total"]:
                  #   del diccionario_odoo["amount_total"]

                             
                  #if diccionario_odoo["order_line"]:
                      #del diccionario_odoo["order_line"]

                  #diccionario_odoo["order_line"]= lista_diccionarios_lineas 
              elif llave=="id":
                pedido_cargado = valor
                    
          existe = diccionario_odoo.has_key("partner_id")
          if existe:
            # print "DICCIONARIO BUENO"
            # print diccionario_odoo
            #_logger.error('##### AIKO ###### Valor de dato en diccionario_odoo: %s' % diccionario_odoo)

            # para identificar los pedidos registrados desde la app de Tercap
            diccionario_odoo['de_tercap'] = True
                    
            sale_diccionario = diccionario_odoo
                    
            order_sale_id = sale_order.create(sale_diccionario)
            lista_pedidos_odoo.append (order_sale_id.id)
                    
            sale_linea_diccionario = {}
            # print lista_diccionarios_lineas
            sale_order_line= self.env['sale.order.line']

            # _logger.error('##### AIKO ###### Valor de dato en lista_diccionarios_lineas: %s' % lista_diccionarios_lineas)
            for lineas_en in lista_diccionarios_lineas:
              sale_linea_diccionario = lineas_en
              sale_linea_diccionario['order_id'] = order_sale_id.id
              # _logger.error('##### AIKO ###### Valor de dato en sale_linea_diccionario: %s' % sale_linea_diccionario)
              # print sale_linea_diccionario, "AQUI"
     
              new_order_line = sale_order_line.create(sale_linea_diccionario)


          #un ultimo paso es marcar estos pedidos como registrados para no duplicar su lectura
          # probar este codigo
          if pedido_cargado:
            url='http://odoo.tercap.net/api/v1/pedidoventa/'
            url = url + pedido_cargado+"/"
            headers={'Content-Type': 'application/json'}
            body = {'estado': 'D'}
            r = requests.patch(url=url, data=json.dumps(body), headers=headers, auth=HTTPBasicAuth('lider', 'lider'))
            _logger.error('##### AIKO ###### Valor de url: url=%s' % url)
            _logger.error('##### AIKO ###### Valor de cambio: data=%s' % json.dumps(body))
            _logger.error('##### AIKO ###### Valor de resultado del pedido: %s' % r.status_code)
            _logger.error('##### AIKO ###### Valor de registro del pedido: %s' % r.text)

        # por ultimo se abre la vista de pedidos de venta con el filtro de los que provengan de tercap
        # sale_view = self.env['ir.ui.view'].search([('name','=','sale.order.tree')])[0].id
        
        sale_view = self.env.ref('sale.view_order_tree').id

        return {
                'name': 'Pedidos leídos de Tercap',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'views': [(sale_view, 'tree')],
                'domain': [('id','in', lista_pedidos_odoo)],
                # 'domain': [('de_tercap','=',True)],
                # 'res_id': idf_ids  or False,##provide the id of the record to be opened
                # 'context': self._context,
                'target': 'in_line',
                # 'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }
        
                   
tercap_order()


class res_partner(models.Model):
    _inherit = "res.partner"

    uid_uid = fields.Char('uid_uid')
    

res_partner()