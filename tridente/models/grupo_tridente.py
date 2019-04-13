'''
Created on 8/11/2016

@author: lider IT
'''
#from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
#import csv
#import glob, os
# from openerp.osv import osv, fields
from openerp import api, fields, models
from datetime import datetime, date, time, timedelta
import calendar
import datetime
from openerp import tools

import logging

_logger = logging.getLogger(__name__)

class tr_parameters(models.Model):
    _name = 'tr.parameters'

    company_id = fields.Many2one('res.company', string="Company")       
    par_name = fields.Char(string = 'Paramener Name', required=True, size = 4)
    interface_csv_inicial_load = fields.Boolean('Interface with csv files',
            default = False,                                    
            help="Enable interface with csv files for inicial load information")
    cliente_generico_id = fields.Many2one('res.partner', string="Cliente Generico")
    input_ruta_inicial_load = fields.Char(string ='Input route  file',
            default = 'var/ftp/csv',                                                
            help="Path or folder where where you should read the files to be processed.csv")  
    name_file_crm =  fields.Char(string = 'crm')
    
    def tr_control_inicial_load(self, cr, uid, ids, context):
        return 
    
class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'          
    
#    def resgistro_event_count_funtion(self, cr, uid, ids, field_name, arg, context=None):
#         reg = self.pool['event.registration']
#         return {
#             partner_id: reg.search_count(cr,uid, [('partner_id', '=', partner_id)], context=context)
#             for partner_id in ids
#         }    
#     def resgistro_event_count_funtion(self):
#         reg = self.env['event.registration']
#         for regist in self:
#             regist.reg_event_count = reg.search_count([('partner_id', '=', regist.id)])
    sector_id = fields.Many2one('tr.sector', string='Sector')   
    tipo_ferias_asiste = fields.Selection([        
            ("nac", "National"),
            ("int", "International"),
            ("bot", "Both"),
            ("oth", "Others")
        ], "Type of fairs")                    
    ferias_abc_id = fields.Many2one('tr.ferias_abc', string='Trade fairs')
#    reg_event_count = fields.Integer(string='# Num. Restration event', compute='resgistro_event_count_funtion')      
    vendedor = fields.Boolean('Salesman', default=False)
    disenador = fields.Boolean('Disigner', default=False) 
    montador =fields.Boolean('Furniture assembler', default=False) 
    prospector =fields.Boolean('Prospector', default=False) 
    palacio =fields.Boolean('Palace', default=False) 
    tipo_prospector = fields.Selection([        
            ("pot", "Potencial"),
            ("dor", "Asleep"),
            ("car", "in portfolio"),
            ("com", "Competition"),
            ("oth", "Others")
        ], "Type Prospector")       
    freria_ids = fields.Many2many('tr.ferias', 'customer_fair_fair_tag_rel', 'customer_fair_id', 'fair_id', 'Fair Description', copy=False) 
    product_crm_ids = fields.Many2many('tr.product_crm', 'customer_product_product_tag_rel', 'customer_product_id', 'product_crm_id', 'Product CRM Description', copy=False)

class product_template(models.Model):
    _name = "product.template"
    _inherit = ['product.template']
    
    largo = fields.Float('Long', help='Long in meters')
    ancho = fields.Float('Width', help='width in meters')
    alto = fields.Float('High', help='high in meters')
    loc_pasillo = fields.Char(string='Aisle', size=16)


class ProjectProject(models.Model):
    _inherit = "project.project"
       
    user_proyect_id = fields.Many2one('res.users', string="User Proyect")
    cant_por_user_proyect_id = fields.Selection([        
            ("porc", "Percentege"),
            ("cant", "Amount")
        ], "Type commision")  
    com_user_proyect_id = fields.Float(
        'Commission', default=0.0,
        help="Amount or commission percentage assigned.")
    head_studies_id = fields.Many2one('res.users', string="Head of studies")
    cant_por_head_studies_id = fields.Selection([        
            ("porc", "Percentege"),
            ("cant", "Amount")
        ], "Type commision")  
    com_head_studies_id = fields.Float(
        'Commission', default=0.0,
        help="Amount or commission percentage assigned.") 
    designer_id = fields.Many2one('res.partner', string="Designer")
    cant_por_designer_id = fields.Selection([        
            ("porc", "Percentege"),
            ("cant", "Amount")
        ], "Type commision")  
    com_designer_id = fields.Float(
        'Commission', default=0.0,
        help="Amount or commission percentage assigned.") 
    internal_note = fields.Text('Internal Note', help='It allows write internal notes without printing or you can see the customer.') 
#   parte de montaje
    montadores_ids = fields.Many2many('res.partner', 'mont_proyect_tag_rel', 'pro_id', 'mont_id', 'assemblers', copy=False) 
    num_stand = fields.Char(string='Stand Num.', size=30)
    fecha_desde = fields.Datetime(string='From Date',help='Event start date.')
    fecha_hasta = fields.Datetime(string='End Date',help='Event end date.')
    evento = fields.Char(string='Event', size=60)
    palacio_id = fields.Many2one('res.partner', string="Palace")
    contacto_name = fields.Char(string='Contact')
    contacto_tel_email = fields.Char(string='Telefon-email')
    contacto_hora = fields.Datetime(string='Time',help='Exact time of arrival.')
#   dos imagenes 
    notas_parte_montaje = fields.Text('Notes:', help='Explanatory note and notes on the assembly part.') 


class tr_sector(models.Model):
    _name = 'tr.sector'
    _rec_name = 's_descripcion'
    s_descripcion = fields.Char(string ='Sector description', required=True)  
    _sql_constraints = [('name_uniq', 'unique (s_descripcion)', " Name of sector already exists !")]
class tr_ferias_abc(models.Model):
    _name = 'tr.ferias_abc'
    _rec_name = 'abc_descripcion'
    abc_descripcion= fields.Char(string = 'Trade fairs', required=True)    
    _sql_constraints = [('name_uniq', 'unique (abc_descripcion)', " Name of trade fairs already exists !")]
class tr_ferias(models.Model):
    _name = 'tr.ferias'
    _rec_name = 'f_descripcion'
    f_descripcion = fields.Char(string ='Fair description', required=True)
    customer_freria_ids = fields.Many2many('res.partner', 'customer_fair_fair_tag_rel', 'fair_id', 'customer_fair_id',  'Fair Description', copy=False)   
#    _sql_constraints = [('name_uniq', 'unique (f_descripcion)', " Name of fair already exists !")]
class tr_product_crm(models.Model):
    _name = 'tr.product_crm'
    _rec_name = 'p_descripcion'
    p_descripcion = fields.Char(string ='product description crm', required=True)
    customer_crm_ids = fields.Many2many('res.partner', 'customer_product_product_tag_rel', 'product_crm_id', 'customer_product_id', 'Product CRM Description', copy=False) 
    _sql_constraints = [('name_uniq', 'unique (p_descripcion)', " Product already exists !")]



