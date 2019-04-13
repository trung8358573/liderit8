# -*- coding: utf-8 -*-


from openerp import models, fields, api
from openerp import tools

import requests

from lxml import etree

from requests.auth import HTTPBasicAuth

    

#from openerp.osv import fields, osv
#from openerp.tools.translate import _



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
        salida_API = requests.get('https://odoo.tercap.net/api/v1/pedidoventaanidada?&format=json', auth=HTTPBasicAuth('lider', 'lider'))
        lista_pedidos_tercap = salida_API.text
        lista_pedidos_tercap = lista_pedidos_tercap.replace("true","True")
        lista_pedidos_tercap = lista_pedidos_tercap.replace("null","False")
        lista_pedidos_tercap = lista_pedidos_tercap.replace("false","False")
        lista_pedidos_odoo = []
        lista_pedidos_tercap =eval(lista_pedidos_tercap)
        for pedido in lista_pedidos_tercap:
                    diccionario_odoo = {}
                    for llave,valor in pedido.items():
                                                 if llave =="lineas":  
                                                                                  lista_linea= []
                                                                                  lista_linea= valor
                                                                                  lista_diccionarios_lineas = []
                                                                                  for linea in lista_linea:
                                                                                       diccionario_new_linea = {}
                                                                                       product_uom_qty = linea['cantidad']
                                                                                       diccionario_new_linea['product_uom_qty'] = product_uom_qty
                                                                                       diccionario_new_linea['price_unit'] = linea['total']
                                                                                       id_producto =linea['producto_id']
                                                                                       nombre_producto = linea['nombre']
                                                                                       product_id_producto_search = product_product.search([('name', '=', id_producto)])
                                                                                       product_nombre_search = product_product.search([('name', '=', nombre_producto)])
                                                                                       if  product_id_producto_search:
                                                                                           diccionario_new_linea['producto_id'] = product_id_producto_search.id
                                                                                       elif     product_nombre_search:
                                                                                           print product_nombre_search.id, nombre_producto
                                                                                           diccionario_new_linea['producto_id'] = product_nombre_search.id
                                                                                       lista_diccionarios_lineas.append(diccionario_new_linea)
                                                 if llave =="numero":
                                                                                  diccionario_odoo["name"]= valor
                                                 elif llave =="cliente_id":
                                                                                  #id_partner_para_odoo = recs.search([('uid_uid', '=', valor)])
                                                                                  id_partner_para_odoo = recs.search([('id', '=', valor)])
                                                                                  if id_partner_para_odoo:
                                                                                       diccionario_odoo["partner_id"]= id_partner_para_odoo.id
                                                                                       print diccionario_odoo["partner_id"], id_partner_para_odoo
                                                 elif llave =="codigo_vendedor":
                                                                                  id_partner_para_odoo = recs.search([('uid_uid', '=', valor)])
                                                                                  if id_partner_para_odoo:
                                                                                       diccionario_odoo["section_id"]= id_partner_para_odoo.id
                                                 elif llave =="direccion_id":
                                                                                  id_partner_para_odoo = recs.search([('uid_uid', '=', valor)])
                                                                                  if id_partner_para_odoo:
                                                                                       diccionario_odoo["partner_shipping_id"]= id_partner_para_odoo.id
                                                                                       diccionario_odoo["partner_invoice_id"]= id_partner_para_odoo.id
                                                 elif llave =="fecha":
                                                                                  diccionario_odoo["date_order"]= valor
                                                 elif llave =="forma_pago_id":
                                                                                  diccionario_odoo["payment_mode_id"]= valor
                                                 elif llave =="observaciones":
                                                                                  diccionario_odoo["note"]= valor
                                                 elif llave =="porcentaje_descuento":
                                                                                  diccionario_odoo["global_discount"]= valor
                                                 elif llave =="referencia":
                                                                                  diccionario_odoo["origin"]= valor
                                                 elif llave =="termino_pago_id":
                                                                                  diccionario_odoo["payment_term"]= valor
                                                 elif llave =="tipo_fiscalidad":
                                                                                  diccionario_odoo["fiscal_position"]= valor
                                                 elif llave =="total":
                                                                                  diccionario_odoo["amount_total"]= valor
                    if diccionario_odoo["fiscal_position"] == "N":
                             diccionario_odoo["fiscal_position"]= 1              
                    else:
                             diccionario_odoo["fiscal_position"]= 2        
                             
                    if diccionario_odoo["origin"]=="":
                        del diccionario_odoo["origin"]
                    
                               
                    if diccionario_odoo["payment_term"]==False:
                        del diccionario_odoo["payment_term"]
                    
                               
                    if diccionario_odoo["global_discount"]:
                        del diccionario_odoo["global_discount"]
                    
                               
                    if diccionario_odoo["note"]=="":
                        del diccionario_odoo["note"]
                    
                               
                    if diccionario_odoo["amount_total"]:
                        del diccionario_odoo["amount_total"]
                    
                    if diccionario_odoo["payment_mode_id"]:
                        del diccionario_odoo["payment_mode_id"]
                    
                    if diccionario_odoo["date_order"]:
                        del diccionario_odoo["date_order"]
                        
                    if diccionario_odoo["name"]:
                        del diccionario_odoo["name"]
                    
                    if diccionario_odoo["fiscal_position"]:
                        del diccionario_odoo["fiscal_position"]
                    

                    diccionario_odoo["order_line"]= lista_diccionarios_lineas 
                    
                    sale_diccionario = {'partner_shipping_id': 7  , 'partner_invoice_id': 7, 'partner_id': 6} 
                    order_sale_id = sale_order.create(sale_diccionario)
                    
                    sale_linea_diccionario = {}
                    for lineas_en in lista_diccionarios_lineas:
                        sale_linea_diccionario = lineas_en
                        sale_linea_diccionario['order_id'] = order_sale_id.id
                        sale_linea_diccionario["product_id"] = sale_linea_diccionario["producto_id"]
                        del sale_linea_diccionario["producto_id"]
                        print sale_linea_diccionario, "AQUI"

                        sale_order_line= self.env['sale.order.line']      
                        sale_order_line.create(sale_linea_diccionario)
                   
tercap_order()
class res_partner(models.Model):
    _inherit = "res.partner"



                                                        
    
    uid_uid = fields.Char('uid_uid')
    

    
res_partner()