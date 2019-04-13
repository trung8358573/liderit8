'''
Created on 18/11/2016

@author: liderit
'''
import vatnumber
import unicodedata
import itertools
from lxml import etree
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import csv
import glob, os

from openerp import SUPERUSER_ID
import openerp
from openerp.osv import osv, fields
# from openerp.exceptions import ValidationError
# import time
#     from datetime import datetime,timedelta
from datetime import datetime, date, time, timedelta
import calendar


from openerp import tools
import locale
from collections import defaultdict, Hashable, Iterable, Mapping, OrderedDict
# import re
# from openerp import api, models
# from openerp.addons.procurement import procurement
import logging
#from curses.ascii import NUL

# from stringold import rjust

_logger = logging.getLogger(__name__)

class par_migracion(osv.osv):
    _name = 'par.migracion'
    _columns = {
        'company_id': fields.many2one('res.company', string="Company"),       
        'par_name': fields.char('Paramener Name', required=True, size = 4),
#  inicial load         
        'interface_csv_inicial_load':fields.boolean('Interface with csv files',
            help="Enable interface with csv files for inicial load information"),        
        'cliente_generico_id': fields.many2one('res.partner', string="Cliente Generico"),         
        'input_ruta_inicial_load': fields.char('Input route  file',                  
            help="Path or folder where where you should read the files to be processed.csv"),
        'output_ruta': fields.char('Output route of potpaid file', 
            help="Path or folder where you want to store files processed postpaid.csv."),
        'name_file_vehiculos_b':fields.boolean('Interface with csv files'),                           
        'name_file_vehiculos': fields.char('Vehiculos'),
        'name_file_crm_b':fields.boolean('Interface with csv files'),  
        'name_file_crm': fields.char('crm'),  
        
        'name_file_octanorm_b':fields.boolean('Interface with csv files'),  
        'name_file_octanorm': fields.char('OCTANORM'),                                 
    }
    _sql_constraints = [('al_parameters_par_name_unique','unique(par_name)', 'Parameter already exists')]
    _sql_constraints = [('al_parameters_company_id_unique', 'unique (company_id)', 'Error ! You cannot create recursive company. !')]
    _defaults = {
        'interface_csv_inicial_load': False,
        'name_file_vehiculos_b': False,
        'name_file_vehiculos': 'Vehiculos*.csv',
        'name_file_crm_b': False,
        'name_file_crm': 'crm*.csv',
        'name_file_octanorm_b': False,
        'name_file_octanorm': 'octanorm*.csv',         
        }
    
    def tr_control_inicial_load(self, cr, uid, ids, context):
        load_obj=self.pool.get('tr.load')
        load_obj.contact_load(cr, uid, ids, context)
        return 
  
class tr_load(osv.osv):
   
    """carga de datos iniciales"""
    _name = "tr.load"
    _columns = {
        "company_id": fields.many2one('res.company', 'Company'),        
        "fecha_timestan": fields.datetime("TimeStamp"),
        "tipo_excepcion": fields.char("Detail of Excepcion", required = False, size = 250, readonly=True),
        "tipo_excepcion_cod": fields.selection([        
            ("1", "Realizada"),
            ("2", "No Realizada"),
            ("9", "Others")
            ], "Type Excepcion"),        
    }
    _defaults = {
        'fecha_timestam': fields.datetime.now,
    }
    def contact_load(self, cr, uid, ids, context):
        fechafact = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    
#       asignacion objetos  
#========================================================================================             
        res_obj = self.pool.get('res.partner')
        sector_obj = self.pool.get('tr.sector')
#         estado_obj = self.pool.get('al.estado_web')         
# #        payment_obj = self.pool.get('account.payment.term')
        load_obj = self.pool.get('tr.load')
        parameters_obj = self.pool.get('par.migracion')
#         k_x_company_bank_obj= self.pool.get('al.load_k_x_company_bank')
#         k_x_contact_addr_obj= self.pool.get('al.load_k_x_contact_addr')
#         k_x_company_addr_obj= self.pool.get('al.load_k_x_company_addr')
#         k_addresses_obj= self.pool.get('al.load_k_addresses')
#         k_price_obj= self.pool.get('al.load_price_segment')
#         k_potencial_customer_history_obj= self.pool.get('al.load_potencial_customer_history')
#         k_categories_obj= self.pool.get('al.load_k_categories')
#         k_america_obj= self.pool.get('al.load_k_grupo_paises_america')
#         bank_obj = self.pool.get('res.partner.bank')
#         contract_obj = self.pool.get('account.analytic.account')
#         contract_obj_invoice_line = self.pool.get('account.analytic.invoice.line')
#         dominios_obj = self.pool.get('al.line_sms')
#         country_obj = self.pool.get('res.country')
        title_obj = self.pool.get('res.partner.title')
#         tarifa_obj = self.pool.get('product.pricelist')
#         tarifa_version_obj = self.pool.get('product.pricelist.version')
#         tarifa_version_item_obj = self.pool.get('product.pricelist.item')
#         anexo_obj = self.pool.get('al.anexo_10')
#         lead_obj = self.pool.get('crm.lead')
#         action_obj = self.pool.get('crm.action')
#         action_type_obj = self.pool.get('crm.action.type')
#         origen_obj = self.pool.get('crm.tracking.source')
#         stage_obj = self.pool.get('crm.case.stage')
#         label_obj = self.pool.get('res.partner.category')
        k_p_cat_obj = self.pool.get('product.category')
        product_categories_obj = self.pool.get('product.category')
        k_products_obj = self.pool.get('product.product')
#         
#         k_lines_orders_obj = self.pool.get('al.load_k_lines_orders')
#         account_invoice_obj = self.pool.get('account.invoice')
#         account_invoice_line_obj = self.pool.get('account.invoice.line')
#         journal_obj = self.pool.get('account.journal')
#         tax_obj = self.pool.get('account.tax')
#         etiquetas_obj = self.pool.get('crm.case.categ')
        res_label_obj = self.pool.get('res.partner.category')   
#         res_partner_category_obj = self.pool.get('res.partner.res.partner.category.rel')  
        tr_produt_crm_obj = self.pool.get('tr.product_crm')   
        tr_ferias_crm_obj = self.pool.get('tr.ferias')  
        tr_ferias_abc_obj = self.pool.get('tr.ferias_abc')  
        
#      ========================================================================================                    
#                 PARAMETROS GENERALES 
#      ========================================================================================        
        user = self.pool.get('res.users').browse(cr, uid, uid, context)    
       
        par00 = parameters_obj.search(cr, uid, [('par_name', '=','pa00'), ('company_id', '=', user.company_id.id)], limit=1)
        par =  parameters_obj.browse(cr, uid, par00, context=context)    
        if not  par:
            values_co = {}
            error = _('There are no general parameters "%s".') % ('pa00' or '') 
            _logger.error(error)                       
            values_co["fecha_timestan"] = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            values_co["tipo_excepcion"] = error 
            values_co["tipo_excepcion_cod"] = '4'
            co_id = load_obj.create(cr,uid,values_co,context=None)                                     
            raise osv.except_osv(('Process Canceled'),('There are no general parameters "%s".')% ('pa00' or ''))
            return 
        if par.interface_csv_inicial_load:   
            os.chdir(par.input_ruta_inicial_load)
#      ========================================================================================           
#            Vehiculos  empresa
#      ======================================================================================== 
            for vehiculos in glob.glob(par.name_file_vehiculos) and 'name_file_vehiculos_b':             
                f = open(vehiculos,'rU') 
                c = csv.reader(f, delimiter=';', skipinitialspace=True)
                conta_lineas = 0
                for line in c:                   
                    if line:
                        conta_lineas += 1
                        if conta_lineas == 1:
                            values_categories = {} 
                            values_categories['name'] = 'Vehiculos empresa' 
                            values_categories['parent_id'] = 1 
                            p_cat_id = product_categories_obj.create(cr,uid,values_categories,context=None)
                            continue                     
                        values_p_vehiculos = {}  
                        nota = ' '  
#               
                        if line[0]:
                            try: 
                                values_p_vehiculos['name'] = line[0].encode('UTF-8')
                                values_p_vehiculos['name'] += ' '
                            except UnicodeDecodeError:
                                values_p_vehiculos['name'] = line[0].decode('cp1252')
                        if line[1] and line[1] <> 'null':
                            try: 
                                values_p_vehiculos['name'] += line[1].encode('UTF-8')
                            except UnicodeDecodeError:
                                values_p_vehiculos['name'] += line[1].decode('cp1252')  
                        if line[2] and line[2] <> 'null':
                            try: 
                                nota += 'Propietario...'
                                nota +=  (line[2] + '\n').encode('UTF-8')
                                nota += '\n'
                            except UnicodeDecodeError:
                                nota += 'Propietario...'
                                nota += line[2].decode('cp1252')
                                nota += '\n'    
                        if line[3] and line[3] <> 'null':
                            try: 
                                values_p_vehiculos['default_code'] =  (line[3]).encode('UTF-8')
                                nota += 'Conductor...'
                                nota +=  (line[3] + '\n').encode('UTF-8')
                                nota += '\n'
                            except UnicodeDecodeError:
                                values_p_vehiculos['default_code'] =  (line[3]).decode('cp1252')
                                nota += 'Conductor...'
                                nota += line[3].decode('cp1252')
                                nota += '\n'      
                        values_p_vehiculos['sale_ok'] = False
                        values_p_vehiculos['purchase_ok'] = False
                        values_p_vehiculos['type'] = 'consu'
                        values_p_vehiculos['uom_id'] = 9
                        values_p_vehiculos['uom_po_id'] = 9
                        values_p_vehiculos['categ_id'] = p_cat_id
                        if line[4] and line[4] <> 'null':
                            try: 
                                values_p_vehiculos['list_price']=  (line[4]).encode('UTF-8')
                                values_p_vehiculos['standard_price']=  (line[4]).encode('UTF-8')
                            except UnicodeDecodeError:
                                values_p_vehiculos['list_price']=  (line[4]).decode('cp1252')
                                values_p_vehiculos['standard_price']=  (line[4]).decode('cp1252')                                
                        k_products_obj.create(cr,uid,values_p_vehiculos,context=None)
                f.close()  
                base = os.path.splitext(vehiculos)[0]
                os.rename(vehiculos, base + ".pro")                
#      ========================================================================================           
#      octanorm
#      ========================================================================================                
            for octanorm in glob.glob(par.name_file_octanorm):             
                f = open(octanorm,'rU') 
                c = csv.reader(f, delimiter=';', skipinitialspace=True)
                conta_lineas = 0
                for line in c:                   
                    if line:
                        conta_lineas += 1
                        if conta_lineas == 1:
                            continue                     
                        values_octanorm = {}  
                        nota = ' '  
#                       codigo
                        if line[0]:
                            values_octanorm['default_code'] = 'O'+line[0]                                                      
#                       descripcion espanol                        
                        if line[5]:
                            values_octanorm['name'] = line[5]      
#                       precio
                        if line[6]:
                            precio = line[6]
                            precio = precio.strip()
                            precio = precio.replace(" ", "")
                            precio = precio.replace(",", ".") 
                            preciofob  = (precio*33)/100
                            precioven  = preciofob * 2.3 
                            values_octanorm['list_price'] = precioven
                            values_octanorm['standard_price'] = preciofob
#                       peso 
                        if line[7]:
                            peso = line[7]
                            peso = peso.strip()
                            peso = peso.replace(" ", "")
                            peso = peso.replace(",", ".") 
                            values_octanorm['weight'] = peso
                            values_octanorm['weight_net'] = peso
#                       largo 
                        if line[8]:
                            largo = line[8]
                            largo = largo.strip()
                            largo = largo.replace(" ", "")
                            largo = largo.replace(",", ".") 
                            values_octanorm['largo'] = largo*1000
#                       ancho 
                        if line[9]:
                            ancho = line[9]
                            ancho = ancho.strip()
                            ancho = ancho.replace(" ", "")
                            ancho = ancho.replace(",", ".") 
                            values_octanorm['ancho'] = ancho*1000
#                       alto 
                        if line[10]:
                            alto = line[10]
                            alto = alto.strip()
                            alto = alto.replace(" ", "")
                            alto = alto.replace(",", ".") 
                            values_octanorm['alto'] = alto*1000
                        k_products_obj.create(cr,uid,values_octanorm,context=None)
                f.close()  
                base = os.path.splitext(octanorm)[0]
                os.rename(octanorm, base + ".pro")                        
#      ========================================================================================           
#            crm   
#      ======================================================================================== 
            for crm in glob.glob(par.name_file_crm) and 'name_file_crm_b':             
                f = open(crm,'rU') 
                c = csv.reader(f, delimiter=';', skipinitialspace=True)
                conta_histo = 0 
                conta_lineas = 0
                conta_empresa = 'aaaaaaaaaaaaa'
                empresa_nueva = False
                for line in c:                   
                    if line:
                        conta_lineas += 1
                        if conta_lineas == 1:
                            continue     
#                        if conta_lineas > 50:
#                            break
                        values_crm = {} 
                        nota = ' ' 
                        values_crm["company_id"] = user.company_id.id 
                        values_crm['is_company'] = False   
#                       Asignacion de equipo de venta
#                        values_crm['section_id'] = 4  
                        values_crm["prospector"] = True
                        values_crm["customer"] = False 
                        if conta_empresa <> line[0]:    
                            conta_empresa = line[0]
                            empresa_nueva = True
                            values_crm['is_company'] = True                        
    #                       Nombre
                            values_crm['name'] = line[0]                   
    #                       contact 
                            values_crm['ref']= line[1]
#                           Telefonos
                            phone = ' ' 
                            if line[4]:
                                phone = line[4]
                                phone += ' '
                            if line[5]:
                                phone  += line[5]
                            values_crm['phone'] = phone
                            if line[6]:
                                values_crm['mobile']= line[6]
                            if line[7]:
                                values_crm['street']= line[7]
#                            
                            city = ' '  
                            if line[8]:
                                city = line[8]
                                city += ' '
                            if line[9] and line[8]<>line[9]:
                                city += line[9]           
                            values_crm['city'] = city
#                            
                            if line[10]:
                                values_crm['zip']= line[10]
#                           pais 
                            if line[11]:
                                pais = line[11].strip()
                                if pais == 'Alemania':
                                    values_crm['country_id'] = 58
                                elif   pais == 'Argentina':
                                    values_crm['country_id'] = 11  
                                elif   pais == 'Belgica':
                                    values_crm['country_id'] = 21      
                                elif   pais == 'Canada':
                                    values_crm['country_id'] = 39  
                                elif   pais == 'Colombia':
                                    values_crm['country_id'] = 50    
                                elif   pais == 'Emiratos Arabes Unid':
                                    values_crm['country_id'] = 2  
                                elif   pais == 'Eslovenia':
                                    values_crm['country_id'] = 201      
                                elif   pais == 'Espana':
                                    values_crm['country_id'] = 69 
                                elif   pais == 'Estados Unidos':
                                    values_crm['country_id'] = 235      
                                elif   pais == 'Francia':
                                    values_crm['country_id'] = 76  
                                elif   pais == 'Gran Bretana':
                                    values_crm['country_id'] = 233      
                                elif   pais == 'Holanda':
                                    values_crm['country_id'] = 166  
                                elif   pais == 'Inglaterra':
                                    values_crm['country_id'] = 233    
                                elif   pais == 'Italia':
                                    values_crm['country_id'] = 110  
                                elif   pais == 'Madrid':
                                    values_crm['country_id'] = 69      
                                elif   pais == 'Mexico':
                                    values_crm['country_id'] = 157  
                                elif   pais == 'Paraguay':
                                    values_crm['country_id'] = 187      
                                elif   pais == 'Polonia':
                                    values_crm['country_id'] = 180    
                                elif   pais == 'Portugal':
                                    values_crm['country_id'] = 185  
                                elif   pais == 'Reino Unido':
                                    values_crm['country_id'] = 233      
                                elif   pais == 'Republica Checa':
                                    values_crm['country_id'] = 57  
                                elif   pais == 'Suiza':
                                    values_crm['country_id'] = 44         
                                elif   pais == 'USA':
                                    values_crm['country_id'] = 235  
                                else:
                                    values_crm['city']+= '  '+ line[11]
#                           comercial     
                            if line[12]:
                                nota = 'Comercial  '
                                nota +=   (line[12] + '\n')
                                comercial = line[12].strip()
                                if comercial == 'Antonio Estrada':
                                    values_crm['user_id'] = 9
                                elif comercial == 'David Ruiz':
                                    values_crm['user_id'] = 10    
                                elif comercial == 'Francisco Garrido':
                                    values_crm['user_id'] = 5 
                                elif comercial == 'Irene Fernandez':
                                    values_crm['user_id'] = 16    
                                elif comercial == 'Javier Sanchez':
                                    values_crm['user_id'] = 17 
                                elif comercial == 'Jose Ramon Rubio':
                                    values_crm['user_id'] = 15       
                                elif comercial == 'Macu Lopez':
                                    values_crm['user_id'] = 14 
                                elif comercial == 'Manuel Garcia':
                                    values_crm['user_id'] = 14    
                                elif comercial == 'Manuel Garcia':
                                    values_crm['user_id'] = 14 
                                else: 
                                    values_crm['user_id'] =  1    
#                            tipo cliente
                            et_tipo_cliente = False 
                            if line[13]:
                                nota = 'Tipo Cliente  '
                                nota +=   (line[13] + '\n')
                                tipo_cliente = line[13].strip()
                                if tipo_cliente =='Potencial':
                                    values_crm['tipo_prospector'] = 'pot'
                                elif tipo_cliente =='Dormido':
                                    values_crm['tipo_prospector'] = 'dor'
                                elif tipo_cliente =='Cartera':
                                    values_crm['tipo_prospector'] = 'car'   
                                    values_crm["customer"] = True
                                elif tipo_cliente =='Otra Cia.':
                                    values_crm['tipo_prospector'] = 'com'   #Competencia 
                                else:
                                    values_crm['tipo_prospector'] = 'oth'   #otros                    
#                                   etiguetas tipo de clientes otros                
                                    values_etiquetas_category = {}
                                    values_etiquetas_category['name'] = tipo_cliente                               
                                    search_condition = [('name', '=', values_etiquetas_category['name'])]  
                                    label_ids =  res_label_obj.search(cr, uid, search_condition, limit=1)
                                    if label_ids:
                                        label_id = res_label_obj.browse(cr, uid, label_ids, context=context)
                                        label_id = label_id.id
                                        et_tipo_cliente = True                        
                                    else:
                                        label_id = res_label_obj.create(cr,uid,values_etiquetas_category,context=None)  
                                        et_tipo_cliente = True     
#                           department Sector
                            if line[14]:
                                try:
                                    descripcion = line[14].encode('UTF-8')
                                except UnicodeDecodeError:
                                    descripcion= line[14].decode('cp1252')  
                                search_condition = [('s_descripcion','=', descripcion.strip())]
                                sector_ids = sector_obj.search(cr, uid, search_condition, limit=1)
                                sector_id =  sector_obj.browse(cr, uid, sector_ids, context=context)    
                                if  sector_id:                  
                                    values_crm['sector_id'] = sector_id.id
                                else:
                                    values_se = {}
                                    values_se ['s_descripcion'] = descripcion                                 
                                    sector_id = sector_obj.create(cr,uid,values_se,context=None)
                                    values_crm['sector_id'] = sector_id
                                     
#                           productos intereses
                            if line[15]:
                                try:
                                    producto = line[15].encode('UTF-8')
                                except UnicodeDecodeError:
                                    producto= line[15].decode('cp1252')  
                                search_condition = [('p_descripcion','=', producto.strip())]
                                produts_ids = tr_produt_crm_obj.search(cr, uid, search_condition, limit=1)
                                product_id =  tr_produt_crm_obj.browse(cr, uid, produts_ids, context=context)  
                                
                                if  product_id:                  
#                                    values_crm['product_crm_ids'] = product_id.id
                                    values_crm['product_crm_ids'] = [(6, 0, [product_id.id])]
                                else:
                                    values_pr_crm = {}
                                    values_pr_crm ['p_descripcion'] = producto                                 
                                    product_id = tr_produt_crm_obj.create(cr,uid,values_pr_crm,context=None)
#                                    values_crm['product_crm_ids'] = product_id
                                    values_crm['product_crm_ids'] = [(6, 0, [product_id])]
#                           Notas
                            if line[16]:
                                try:
                                    anotacion = line[16].encode('UTF-8')
                                except UnicodeDecodeError:
                                    anotacion= line[16].decode('cp1252')                      
                                nota = 'Notas:  '
                                nota +=   (anotacion + '\n')
#=================================================================================================================  
                            listap = [] 
                            listad = [] 
                            i17 = False 
                            if line[17]:
                                try:
                                    listap.index(line[17])
                                except:                
                                    listap.append(line[17]) 
                                    i17 = True                                    
                            i18 = False 
                            if line[18]:
                                try:
                                    listap.index(line[18])
                                except:                
                                    listap.append(line[18]) 
                                    i18 = True        
                            i19 = False 
                            if line[19]:
                                try:
                                    listap.index(line[19])
                                except:                
                                    listap.append(line[19]) 
                                    i19 = True
                            i20 = False 
                            if line[20]:
                                try:
                                    listap.index(line[20])
                                except:                
                                    listap.append(line[20]) 
                                    i20 = True              
                            i21 = False 
                            if line[21]:
                                try:
                                    listap.index(line[21])
                                except:                
                                    listap.append(line[21]) 
                                    i21 = True                                                   
                            i22 = False 
                            if line[22]:
                                try:
                                    listap.index(line[22])
                                except:                
                                    listap.append(line[22]) 
                                    i22 = True                                     
#===================================================================================================================                                    
                            # uferia 1
                            if line[17] and i17:
                                try:
                                    feria = line[17].encode('UTF-8')
                                except UnicodeDecodeError:
                                    feria= line[17].decode('cp1252')
                                search_condition = [('f_descripcion','=', feria.strip())]
                                ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                                feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                                if  feria_id:                     
#                                    values_crm['freria_ids'] = [(6,0, [feria_id.id])]
                                    listad.append(feria_id.id) 
                                else:
                                    values_feria_crm = {}
                                    values_feria_crm ['f_descripcion'] = feria                                 
                                    try:
                                        feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)    
                                        listad.append(feria_id)
                                    except:
                                        _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')    
                            #   uferia 2
                            if line[18] and i18:
                                try:
                                    feria = line[18].encode('UTF-8')
                                except UnicodeDecodeError:
                                    feria= line[18].decode('cp1252')  
                                search_condition = [('f_descripcion','=', feria.strip())]
                                ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                                feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)       
                                if  feria_id:                                                  
                                    listad.append(feria_id.id) 
                                else:
                                    values_feria_crm = {}
                                    values_feria_crm ['f_descripcion'] = feria                                
                                    try:
                                        feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)   
                                        listad.append(feria_id)
                                    except:
                                        _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')                            
                            #  uferia 3
                            if line[19] and i19:
                                try:
                                    feria = line[19].encode('UTF-8')
                                except UnicodeDecodeError:
                                    feria= line[19].decode('cp1252')  
                                search_condition = [('f_descripcion','=', feria.strip())]
                                ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                                feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                                if  feria_id:                     
                                    listad.append(feria_id.id) 
                                else:
                                    values_feria_crm = {}
                                    values_feria_crm ['f_descripcion'] = feria
                                    try:                                 
                                        feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)    
                                        listad.append(feria_id)                         
                                    except:
                                        _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n') 
                            #  uferia 4
                            if line[20] and i20:
                                try:
                                    feria = line[20].encode('UTF-8')
                                except UnicodeDecodeError:
                                    feria= line[20].decode('cp1252')  
                                search_condition = [('f_descripcion','=', feria.strip())]
                                ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                                feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                                if  feria_id:                      
                                    listad.append(feria_id.id) 
                                else:
                                    values_feria_crm = {}
                                    values_feria_crm ['f_descripcion'] = feria                                 
                                    try:    
                                        feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)   
                                        listad.append(feria_id)    
                                    except:
                                        _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')         
                            #   uferia 5
                            if line[21] and i21:
                                try:
                                    feria = line[21].encode('UTF-8')
                                except UnicodeDecodeError:
                                    feria= line[21].decode('cp1252')  
                                search_condition = [('f_descripcion','=', feria.strip())]
                                ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                                feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                                if  feria_id:                     
                                    listad.append(feria_id.id)
                                else:
                                    values_feria_crm = {}
                                    values_feria_crm ['f_descripcion'] = feria
                                    try:                                 
                                        feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)   
                                        listad.append(feria_id)
                                    except:
                                        _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')                             
                            #   uferia 6
                            if line[22] and i22:
                                try:
                                    feria = line[22].encode('UTF-8')
                                except UnicodeDecodeError:
                                    feria= line[22].decode('cp1252')  
                                search_condition = [('f_descripcion','=', feria.strip())]
                                ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                                feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                                if  feria_id:                     
                                    listad.append(feria_id.id)
                                else:
                                    values_feria_crm = {}
                                    values_feria_crm ['f_descripcion'] = feria
                                    try:                                 
                                        feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)    #                                    values_crm['product_crm_ids'] = product_id
                                        listad.append(feria_id)
                                    except:
                                        _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')                                           
                            if listad:
                                values_crm['freria_ids'] = [(6,0, (listad))]                                 
#=============================================================================================================================                      
#                           uferint #                            et_uferint = False  
                            if line[23]:  
                                try:
                                    uferint = line[23].encode('UTF-8')
                                except UnicodeDecodeError:
                                    uferint= line[23].decode('cp1252')   
                                nota = 'UFERINT:  '
                                nota +=   (uferint + '\n')  
                                uferint = uferint.strip()
                                if uferint =='Nacional':
                                    values_crm['tipo_ferias_asiste'] = 'nac'
                                elif uferint =='Internacional':                                                    
                                    values_crm['tipo_ferias_asiste'] = 'int'    
                                elif uferint =='Ambos':
                                    values_crm['tipo_ferias_asiste'] = 'bot'
                                else:
                                    values_crm['tipo_ferias_asiste'] = 'oth'    
#                           ufernac                             et_ufernac = False  
                            if line[24]:  
                                try:
                                    ufernac = line[24].encode('UTF-8')
                                except UnicodeDecodeError:
                                    ufernac= line[24].decode('cp1252')   
                            
                                nota = 'UFERNAC:  '
                                nota +=   (ufernac + '\n')  
                                ufernac = ufernac.strip()
                                values_ferias_abc={}
                                values_ferias_abc['abc_descripcion'] = ufernac
                                search_condition = [('abc_descripcion', '=', ufernac.strip())] 
                                try: 
                                    ferias_abc_ids =  tr_ferias_abc_obj.search(cr, uid, search_condition, limit=1)
                                    if ferias_abc_ids:
                                        feria_abc_id = tr_ferias_abc_obj.browse(cr, uid, ferias_abc_ids, context=context)
                                        values_crm['ferias_abc_id']= feria_abc_id.id
                                                          
                                    else:
                                        feria_abc_id = tr_ferias_abc_obj.create(cr,uid,values_ferias_abc,context=None)  
                                        values_crm['ferias_abc_id'] = feria_abc_id
                                except:
                                    _logger.error('######## AIKO abc deferia incorrecta   ####### ->\n'+  str(ufernac) + ' '+ str(values_crm['name']) + '\n')          
#                            emails            
                            email = ' ' 
                            if line[25]:  
                                try:
                                    email_25 = line[25].encode('UTF-8')
                                except UnicodeDecodeError:
                                    email_25= line[25].decode('cp1252')   
                                email = email_25 
                            if line[26]:  
                                try:
                                    email_26 = line[26].encode('UTF-8')
                                except UnicodeDecodeError:
                                    email_26= line[26].decode('cp1252')   
                                email += ',\n'
                                email += email_26          
                            if line[27]:  
                                try:
                                    email_27 = line[27].encode('UTF-8')
                                except UnicodeDecodeError:
                                    email_27= line[27].decode('cp1252')   
                                email += ',\n'
                                email += email_27          
                            if line[28]:  
                                try:
                                    email_28 = line[28].encode('UTF-8')
                                except UnicodeDecodeError:
                                    email_28= line[28].decode('cp1252')   
                                email += ',\n'
                                email += email_28          
                            if line[29]:  
                                try:
                                    email_29 = line[29].encode('UTF-8')
                                except UnicodeDecodeError:
                                    email_29= line[29].decode('cp1252')   
                                email += ',\n'
                                email += email_29      
                            values_crm['email'] = email                        
                            values_crm['comment'] = nota  
                            try: 
                                empresa_id=res_obj.create(cr,uid,values_crm,context=None)                           
                                if et_tipo_cliente:
                                    cr.execute('INSERT INTO res_partner_res_partner_category_rel (category_id, partner_id)  values (%s, %s)', (label_id, empresa_id))                        
                            except:
                                _logger.error('######## AIKO empresa  no procesado   ####### ->\n' + str(values_crm['name']) + '\n')    
#                             if et_uferint:
#                                 cr.execute('INSERT INTO res_partner_res_partner_category_rel (category_id, partner_id)  values (%s, %s)', (label_uferint_id, empresa_id))
#                     
#                             if et_ufernac:
#                                 cr.execute('INSERT INTO res_partner_res_partner_category_rel (category_id, partner_id)  values (%s, %s)', (label_ufernac_id, empresa_id))
#    
##############################################################################################################3
#                           Etiqueta cliente golmain  
                            if conta_histo == 0 :
                                conta_histo = 1  
                                values_etiquetas_category = {}
                                values_etiquetas_category['name'] = 'GOLDMINE'                           
                                search_condition = [('name', '=', values_etiquetas_category['name'])]  
                                golmain_ids =  res_label_obj.search(cr, uid, search_condition, limit=1)
                                if golmain_ids:
                                    golmain_id = res_label_obj.browse(cr, uid, golmain_ids, context=context)
                                    golmain_id = golmain_id.id                  
                                else:
                                    golmain_id = res_label_obj.create(cr,uid,values_etiquetas_category,context=None)                          
                            cr.execute('INSERT INTO res_partner_res_partner_category_rel (category_id, partner_id)  values (%s, %s)', (golmain_id, empresa_id))
###################################################################################################################                                               
#=================================================================================================================
#                       Contactos
#=================================================================================================================
                        values_crm = {} 
                        nota = ' ' 
                        values_crm["company_id"] = user.company_id.id 
                        values_crm['is_company'] = False   
#                       Asignacion de equipo de venta
#                        values_crm['section_id'] = 4  
                        values_crm["prospector"] = True
                        values_crm["customer"] = False                        
                        values_crm['parent_id'] = empresa_id
#                       Nombre
                        if  line[1]: 
                            values_crm['name'] = line[1]
                        else:
                            values_crm['name'] = 'Sin Nombre'                      
#                       contact 
                        values_crm['ref']= ' '
#                       departament
                        funcion = ' '
                        if line[2]:
                            funcion = line[2]
                            funcion += '  '
                        if line[3]:
                            funcion += line[3]
                        values_crm['function'] = funcion     
#                           Telefonos
                        phone = ' ' 
                        if line[4]:
                            phone = line[4]
                            phone += ' '
                        if line[5]:
                            phone  += line[5]
                        values_crm['phone'] = phone
                        if line[6]:
                            values_crm['mobile']= line[6]
                        if line[7]:
                            values_crm['street']= line[7]
#                            
                        city = ' '  
                        if line[8]:
                            city = line[8]
                            city += ' '
                        if line[9] and line[8]<>line[9]:
                            city += line[9]           
                        values_crm['city'] = city
#                            
                        if line[10]:
                            values_crm['zip']= line[10]
#                           pais 
                        if line[11]:
                            pais = line[11].strip()
                            if pais == 'Alemania':
                                values_crm['country_id'] = 58
                            elif   pais == 'Argentina':
                                values_crm['country_id'] = 11  
                            elif   pais == 'Belgica':
                                values_crm['country_id'] = 21      
                            elif   pais == 'Canada':
                                values_crm['country_id'] = 39  
                            elif   pais == 'Colombia':
                                values_crm['country_id'] = 50    
                            elif   pais == 'Emiratos Arabes Unid':
                                values_crm['country_id'] = 2  
                            elif   pais == 'Eslovenia':
                                values_crm['country_id'] = 201      
                            elif   pais == 'Espana':
                                values_crm['country_id'] = 69 
                            elif   pais == 'Estados Unidos':
                                values_crm['country_id'] = 235      
                            elif   pais == 'Francia':
                                values_crm['country_id'] = 76  
                            elif   pais == 'Gran Bretana':
                                values_crm['country_id'] = 233      
                            elif   pais == 'Holanda':
                                values_crm['country_id'] = 166  
                            elif   pais == 'Inglaterra':
                                values_crm['country_id'] = 233    
                            elif   pais == 'Italia':
                                values_crm['country_id'] = 110  
                            elif   pais == 'Madrid':
                                values_crm['country_id'] = 69      
                            elif   pais == 'Mexico':
                                values_crm['country_id'] = 157  
                            elif   pais == 'Paraguay':
                                values_crm['country_id'] = 187      
                            elif   pais == 'Polonia':
                                values_crm['country_id'] = 180    
                            elif   pais == 'Portugal':
                                values_crm['country_id'] = 185  
                            elif   pais == 'Reino Unido':
                                values_crm['country_id'] = 233      
                            elif   pais == 'Republica Checa':
                                values_crm['country_id'] = 57  
                            elif   pais == 'Suiza':
                                values_crm['country_id'] = 44         
                            elif   pais == 'USA':
                                values_crm['country_id'] = 235  
                            else:
                                values_crm['city']+= '  '+ line[11]
#                           comercial     
                        if line[12]:
                            nota = 'Comercial  '
                            nota +=   (line[12] + '\n')
                            comercial = line[12].strip()
                            if comercial == 'Antonio Estrada':
                                values_crm['user_id'] = 9
                            elif comercial == 'David Ruiz':
                                values_crm['user_id'] = 10    
                            elif comercial == 'Francisco Garrido':
                                values_crm['user_id'] = 5 
                            elif comercial == 'Irene Fernandez':
                                values_crm['user_id'] = 16    
                            elif comercial == 'Javier Sanchez':
                                values_crm['user_id'] = 17 
                            elif comercial == 'Jose Ramon Rubio':
                                values_crm['user_id'] = 15       
                            elif comercial == 'Macu Lopez':
                                values_crm['user_id'] = 14 
                            elif comercial == 'Manuel Garcia':
                                values_crm['user_id'] = 14    
                            elif comercial == 'Manuel Garcia':
                                values_crm['user_id'] = 14 
                            else: 
                                values_crm['user_id'] =  1    
#                            tipo cliente
                        et_tipo_cliente = False
                        if line[13]:
                            nota = 'Tipo Cliente  '
                            nota +=   (line[13] + '\n')
                            tipo_cliente = line[13].strip()
                            if tipo_cliente =='Potencial':
                                values_crm['tipo_prospector'] = 'pot'
                            elif tipo_cliente =='Dormido':
                                values_crm['tipo_prospector'] = 'dor'
                            elif tipo_cliente =='Cartera':
                                values_crm['tipo_prospector'] = 'car' 
                                values_crm["customer"] = True  
                            elif tipo_cliente =='Otra Cia.':
                                values_crm['tipo_prospector'] = 'com'   #Competencia 
                            else:
                                values_crm['tipo_prospector'] = 'oth'   #otros 
#                                   etiguetas tipo de clientes otros                
                                values_etiquetas_category = {}
                                values_etiquetas_category['name'] = tipo_cliente                               
                                search_condition = [('name', '=', values_etiquetas_category['name'])]  
                                label_ids =  res_label_obj.search(cr, uid, search_condition, limit=1)
                                if label_ids:
                                    label_id = res_label_obj.browse(cr, uid, label_ids, context=context)
                                    label_id = label_id.id
                                    et_tipo_cliente = True                        
                                else:
                                    label_id = res_label_obj.create(cr,uid,values_etiquetas_category,context=None)  
                                    et_tipo_cliente = True     
#                           department Sector
                        if line[14]:
                            try:
                                descripcion = line[14].encode('UTF-8')
                            except UnicodeDecodeError:
                                descripcion= line[14].decode('cp1252')  
                            search_condition = [('s_descripcion','=', descripcion.strip())]
                            sector_ids = sector_obj.search(cr, uid, search_condition, limit=1)
                            sector_id =  sector_obj.browse(cr, uid, sector_ids, context=context)    
                            if  sector_id:                  
                                values_crm['sector_id'] = sector_id.id
                            else:
                                values_se = {}
                                values_se ['s_descripcion'] = descripcion                                 
                                sector_id = sector_obj.create(cr,uid,values_se,context=None)
                                values_crm['sector_id'] = sector_id
                                 
#                           productos intereses
                        if line[15]:
                            try:
                                producto = line[15].encode('UTF-8')
                            except UnicodeDecodeError:
                                producto= line[15].decode('cp1252')  
                            search_condition = [('p_descripcion','=', producto.strip())]
                            produts_ids = tr_produt_crm_obj.search(cr, uid, search_condition, limit=1)
                            product_id =  tr_produt_crm_obj.browse(cr, uid, produts_ids, context=context)  
                            
                            if  product_id:                  
#                                    values_crm['product_crm_ids'] = product_id.id
                                values_crm['product_crm_ids'] = [(6, 0, [product_id.id])]
                            else:
                                values_pr_crm = {}
                                values_pr_crm ['p_descripcion'] = producto                                 
                                product_id = tr_produt_crm_obj.create(cr,uid,values_pr_crm,context=None)
#                                    values_crm['product_crm_ids'] = product_id
                                values_crm['product_crm_ids'] = [(6, 0, [product_id])]
#                           Notas
                        if line[16]:
                            try:
                                anotacion = line[16].encode('UTF-8')
                            except UnicodeDecodeError:
                                anotacion= line[16].decode('cp1252')                      
                            nota = 'Notas:  '
                            nota +=   (anotacion + '\n')
#=================================================================================================================  
                        listap = [] 
                        listad = [] 
                        i17 = False 
                        if line[17]:
                            try:
                                listap.index(line[17])
                            except:                
                                listap.append(line[17]) 
                                i17 = True                                    
                        i18 = False 
                        if line[18]:
                            try:
                                listap.index(line[18])
                            except:                
                                listap.append(line[18]) 
                                i18 = True        
                        i19 = False 
                        if line[19]:
                            try:
                                listap.index(line[19])
                            except:                
                                listap.append(line[19]) 
                                i19 = True
                        i20 = False 
                        if line[20]:
                            try:
                                listap.index(line[20])
                            except:                
                                listap.append(line[20]) 
                                i20 = True              
                        i21 = False 
                        if line[21]:
                            try:
                                listap.index(line[21])
                            except:                
                                listap.append(line[21]) 
                                i21 = True                                                   
                        i22 = False 
                        if line[22]:
                            try:
                                listap.index(line[22])
                            except:                
                                listap.append(line[22]) 
                                i22 = True                                     
#===================================================================================================================                                    
                        # uferia 1
                        if line[17] and i17:
                            try:
                                feria = line[17].encode('UTF-8')
                            except UnicodeDecodeError:
                                feria= line[17].decode('cp1252')
                            search_condition = [('f_descripcion','=', feria.strip())]
                            ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                            feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                            if  feria_id:                     
#                                    values_crm['freria_ids'] = [(6,0, [feria_id.id])]
                                listad.append(feria_id.id) 
                            else:
                                values_feria_crm = {}
                                values_feria_crm ['f_descripcion'] = feria
                                try:                                 
                                    feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)    
                                    listad.append(feria_id)
                                except:
                                    _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')      
                        #   uferia 2
                        if line[18] and i18:
                            try:
                                feria = line[18].encode('UTF-8')
                            except UnicodeDecodeError:
                                feria= line[18].decode('cp1252')  
                            search_condition = [('f_descripcion','=', feria.strip())]
                            ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                            feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)       
                            if  feria_id:                                                  
                                listad.append(feria_id.id) 
                            else:
                                values_feria_crm = {}
                                values_feria_crm ['f_descripcion'] = feria                                
                                try:
                                    feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)   
                                    listad.append(feria_id)
                                except:
                                    _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')                             
                        #  uferia 3
                        if line[19] and i19:
                            try:
                                feria = line[19].encode('UTF-8')
                            except UnicodeDecodeError:
                                feria= line[19].decode('cp1252')  
                            search_condition = [('f_descripcion','=', feria.strip())]
                            ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                            feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                            if  feria_id:                     
                                listad.append(feria_id.id) 
                            else:
                                values_feria_crm = {}
                                values_feria_crm ['f_descripcion'] = feria
                                try:                                 
                                    feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)    
                                    listad.append(feria_id)
                                except:
                                    _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')                             
                        #  uferia 4
                        if line[20] and i20:
                            try:
                                feria = line[20].encode('UTF-8')
                            except UnicodeDecodeError:
                                feria= line[20].decode('cp1252')  
                            search_condition = [('f_descripcion','=', feria.strip())]
                            ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                            feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                            if  feria_id:                      
                                listad.append(feria_id.id) 
                            else:
                                values_feria_crm = {}
                                values_feria_crm ['f_descripcion'] = feria 
                                try:                                
                                    feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)   
                                    listad.append(feria_id)
                                except:
                                    _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')                                    
                        #   uferia 5
                        if line[21] and i21:
                            try:
                                feria = line[21].encode('UTF-8')
                            except UnicodeDecodeError:
                                feria= line[21].decode('cp1252')  
                            search_condition = [('f_descripcion','=', feria.strip())]
                            ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                            feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                            if  feria_id:                     
                                listad.append(feria_id.id)
                            else:
                                values_feria_crm = {}
                                values_feria_crm ['f_descripcion'] = feria
                                try:                                 
                                    feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)   
                                    listad.append(feria_id)
                                except:
                                    _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')                                 
                        #   uferia 6
                        if line[22] and i22:
                            try:
                                feria = line[22].encode('UTF-8')
                            except UnicodeDecodeError:
                                feria= line[22].decode('cp1252')  
                            search_condition = [('f_descripcion','=', feria.strip())]
                            ferias_ids = tr_ferias_crm_obj.search(cr, uid, search_condition, limit=1)
                            feria_id =  tr_ferias_crm_obj.browse(cr, uid, ferias_ids, context=context)                               
                            if  feria_id:                     
                                listad.append(feria_id.id)
                            else:
                                values_feria_crm = {}
                                values_feria_crm ['f_descripcion'] = feria
                                try:                                 
                                    feria_id = tr_ferias_crm_obj.create(cr,uid,values_feria_crm,context=None)    #                                    values_crm['product_crm_ids'] = product_id
                                    listad.append(feria_id)
                                except:
                                    _logger.error('######## AIKO  feria duplicada   ####### ->\n'+  str(feria) + ' '+ str(values_crm['name']) + '\n')                                          
                        if listad:
                            values_crm['freria_ids'] = [(6,0, (listad))]                              
#=============================================================================================================================
#                           uferint #                            et_uferint = False  
                        if line[23]:  
                            try:
                                uferint = line[23].encode('UTF-8')
                            except UnicodeDecodeError:
                                uferint= line[23].decode('cp1252')   
                            nota = 'UFERINT:  '
                            nota +=   (uferint + '\n')  
                            uferint = uferint.strip()
                            if uferint =='Nacional':
                                values_crm['tipo_ferias_asiste'] = 'nac'
                            elif uferint =='Internacional':
                                values_crm['tipo_ferias_asiste'] = 'int'    
                            elif uferint =='Ambos':
                                values_crm['tipo_ferias_asiste'] = 'bot'
                            else:
                                values_crm['tipo_ferias_asiste'] = 'oth'    
#                           ufernac                             et_ufernac = False  
                        if line[24]:  
                            try:
                                ufernac = line[24].encode('UTF-8')
                            except UnicodeDecodeError:
                                ufernac= line[24].decode('cp1252')   
                        
                            nota = 'UFERNAC:  '
                            nota +=   (ufernac + '\n')  
                            ufernac = ufernac.strip()
                            values_ferias_abc={}
                            values_ferias_abc['abc_descripcion'] = ufernac
                            search_condition = [('abc_descripcion', '=', ufernac.strip())]  
                            try: 
                                ferias_abc_ids =  tr_ferias_abc_obj.search(cr, uid, search_condition, limit=1)
                                if ferias_abc_ids:
                                    feria_abc_id = tr_ferias_abc_obj.browse(cr, uid, ferias_abc_ids, context=context)
                                    values_crm['ferias_abc_id']= feria_abc_id.id
                                                      
                                else:
                                    feria_abc_id = tr_ferias_abc_obj.create(cr,uid,values_ferias_abc,context=None)  
                                    values_crm['ferias_abc_id'] = feria_abc_id
                            except:
                                _logger.error('######## AIKO abc deferia incorrecta   ####### ->\n'+  str(ufernac) + ' '+ str(values_crm['name']) + '\n')       
#                            emails            
                        email = ' ' 
                        if line[25]:  
                            try:
                                email_25 = line[25].encode('UTF-8')
                            except UnicodeDecodeError:
                                email_25= line[25].decode('cp1252')   
                            email = email_25 
                        if line[26]:  
                            try:
                                email_26 = line[26].encode('UTF-8')
                            except UnicodeDecodeError:
                                email_26= line[26].decode('cp1252')   
                            email += ',\n'
                            email += email_26          
                        if line[27]:  
                            try:
                                email_27 = line[27].encode('UTF-8')
                            except UnicodeDecodeError:
                                email_27= line[27].decode('cp1252')   
                            email += ',\n'
                            email += email_27          
                        if line[28]:  
                            try:
                                email_28 = line[28].encode('UTF-8')
                            except UnicodeDecodeError:
                                email_28= line[28].decode('cp1252')   
                            email += ',\n'
                            email += email_28          
                        if line[29]:  
                            try:
                                email_29 = line[29].encode('UTF-8')
                            except UnicodeDecodeError:
                                email_29= line[29].decode('cp1252')   
                            email += ',\n'
                            email += email_29      
                        values_crm['email'] = email                        
                        values_crm['comment'] = nota   
                        try: 
                            cl_id=res_obj.create(cr,uid,values_crm,context=None)                           
                            if et_tipo_cliente:
                                cr.execute('INSERT INTO res_partner_res_partner_category_rel (category_id, partner_id)  values (%s, %s)', (label_id, cl_id))                        
                        except:
                            _logger.error('######## AIKO contacto no procesado   ####### ->\n' + str(values_crm['name']) + '\n')    
#                         if et_uferint:
#                             cr.execute('INSERT INTO res_partner_res_partner_category_rel (category_id, partner_id)  values (%s, %s)', (label_uferint_id, cl_id))
#                 
#                         if et_ufernac:
#                             cr.execute('INSERT INTO res_partner_res_partner_category_rel (category_id, partner_id)  values (%s, %s)', (label_ufernac_id, cl_id))

                f.close()  
#                base = os.path.splitext(crm)[0]
#                os.rename(crm, base + ".pro")
#      ========================================================================================           
#            k_categories   
#      ======================================================================================== 
#             for k_categories in glob.glob(par.name_file_k_categories):             
#                 f = open(k_categories,'rU') 
#                 c = csv.reader(f, delimiter=';', skipinitialspace=True)
#                 nivel1_categories = 'xx'
#                 nivel2_categories = 'xx.yy'
#                 conta_lineas = 0
#                 for line in c:                   
#                     if line:
#                         conta_lineas += 1
#                         if conta_lineas == 1:
#                             continue     
#                 
#                         values_categories = {}   
# #                       nm_shop
#                         if line[0] and line[0] <> 'null':
#                             try: 
#                                 values_categories['l0_nm_shop'] = line[0].encode('UTF-8')
#                             except UnicodeDecodeError:
#                                 values_categories['l0_nm_shop'] = line[0].decode('cp1252')
#                             values_categories['l0_nm_shop_xx'] = values_categories['l0_nm_shop'][0:2]
#                             values_categories['l0_nm_shop_yy'] = values_categories['l0_nm_shop'][3:28]
#                             if  values_categories['l0_nm_shop_xx'] <> nivel1_categories: 
#                                 nivel1_categories = values_categories['l0_nm_shop_xx']
#                                 values_cat_1 = {}   
# #                                values_cat_1['name'] = values_categories['l0_nm_shop_yy']
#                                 values_cat_1['name'] = values_categories['l0_nm_shop']
#                                 values_cat_1['parent_id'] = 2
#                                 cat_1_id=product_categories_obj.create(cr,uid,values_cat_1,context=None) 
#                             values_categories['l0_cateroty_id'] = cat_1_id
# #                       nm_categoy      
#                         if line[1] and line[1] <> 'null':
#                             try: 
#                                 values_categories['l1_nm_category'] = line[1].encode('UTF-8')                               
#                             except UnicodeDecodeError:
#                                 values_categories['l1_nm_category'] = line[1].decode('cp1252')
# #                                _logger.error('######## AIKO  parte de categoria   ####### ->\n'+  str(line[1])  + '\n')
#                             values_categories['l1_nm_category_xx'] = values_categories['l1_nm_category'][0:5]
#                            
#                             values_categories['l1_nm_category_yy'] = values_categories['l1_nm_category'][6:28]
#                             if  values_categories['l1_nm_category_xx'] <> nivel2_categories: 
#                                 nivel2_categories = values_categories['l1_nm_category_xx']
#                                 values_cat_2 = {}   
# #                               values_cat_2['name'] = values_categories['l1_nm_category_yy']
#                                 values_cat_2['name'] = values_categories['l1_nm_category']
#                                 values_cat_2['parent_id'] = cat_1_id
#                                 cat_2_id=product_categories_obj.create(cr,uid,values_cat_2,context=None) 
#                             values_categories['l1_cateroty_id'] = cat_2_id
# #                       gu_product
#                         if line[2] and line[2] <> 'null':
#                             try: 
#                                 values_categories['l2gu_product'] = line[2].encode('UTF-8')
#                             except UnicodeDecodeError:
#                                 values_categories['l2gu_product'] = line[2].decode('cp1252')
# #                       nm_product     
#                         if line[3] and line[3] <> 'null':
#                             try: 
#                                 values_categories['l3_nm_category'] = line[3].encode('UTF-8')
#                             except UnicodeDecodeError:
#                                 values_categories['l3_nm_category'] = line[3].decode('cp1252')
# 
#                         k_categories_obj.create(cr,uid,values_categories,context=None)
#                     
#                 f.close()  
#                 base = os.path.splitext(k_categories)[0]
#                 os.rename(k_categories, base + ".pro")
#      ========================================================================================         
#            k_products
#      ======================================================================================== 
#             for k_products in glob.glob(par.name_file_k_products):             
#                 f = open(k_products,'rU') 
#                 c = csv.reader(f, delimiter=';', skipinitialspace=True)
#                 conta_lineas = 0
#                 for line in c:                   
#                     if line:
#                         conta_lineas += 1
#                         if conta_lineas == 1:
#                             continue     
#                         values_product = {}   
#                         values_product['name'] = 'Sin nombre'
# #                       gu_product 
#                         if line[0] and line[0] <> 'null':
#                             try: 
#                                 values_product['gu_product'] = line[0].encode('UTF-8')
#                             except UnicodeDecodeError:
#                                 values_product['gu_product'] = line[0].decode('cp1252')
#                             search_condition = [('l2gu_product', '=', values_product['gu_product'])]  
#                             c_ids =  k_categories_obj.search(cr, uid, search_condition, limit=1)
#                             c_id = k_categories_obj.browse(cr, uid, c_ids, context=context) 
#                             if c_id:
#                                 values_product["categ_id"] = c_id.l1_cateroty_id.id   
#                        
#                         if line[3] and line[3] <> 'null':
#                             try: 
#                                 values_product['name'] = line[3].encode('UTF-8')
#                             except UnicodeDecodeError:
#                                 values_product['name'] = line[3].decode('cp1252')   
#                                 
# #                             except UnicodeDecodeError:
# #                                 values_product['name'] = 'Sin nombre'
# #                       pr_list precio 
#                         if line[9] and line[9] <> 'null':
#                             try: 
#                                 values_product['list_price'] = line[9].encode('UTF-8')
#                                 values_product['list_price'] = values_product['list_price'].replace(",",".")                                   
#                             except UnicodeDecodeError:
#                                 values_product['list_price'] = 0   
# #
#                         values_product['default_code'] = ' '
#                         if line[0] and line[0] <> 'null':
#                             try: 
#                                 values_product['default_code'] = line[0].encode('UTF-8')
#                             except UnicodeDecodeError:
#                                 values_product['default_code'] = line[0].decode('cp1252') 
#                         if values_product['default_code'] == values_product['name']:
#                             values_product['default_code'] = ' '
#                         
#                         k_products_obj.create(cr,uid,values_product,context=None)
#                   
#                 f.close()  
#                 base = os.path.splitext(k_products)[0]
#                 os.rename(k_products, base + ".pro")
    #   log de control       
#===================================================
            values_load = {}   
            values_load["company_id"] = user.company_id.id
            values_load["fecha_timestan"] = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)   
            values_load["tipo_excepcion"] = 'Carga de datos realizada'
            values_load["tipo_excepcion_cod"] = '1'
            try:    
                co_id = load_obj.create(cr,uid,values_load,context=None)
            except:
                _logger.error('######## AIKO  3283 no se puede crear registrio en al.load  ####### ->\n'+  str(values_load)  + '\n') 
        
            
    