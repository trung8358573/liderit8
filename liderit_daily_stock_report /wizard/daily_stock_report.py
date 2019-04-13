# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
import time
import StringIO
import base64
from openerp import tools
from openerp.tools import ustr
import unicodedata
from openerp.tools.translate import _
import logging 
from datetime import datetime
_logger = logging.getLogger(__name__)
from fpdf import FPDF

class product_category_ext(osv.TransientModel):
    _name = "product.category.ext"
    _columns = {
        'category_id': fields.many2one('product.category','Category'),
        'report_category_id' : fields.many2one('daily.stock.report', 'Stock Report'),
    }

product_category_ext()

class stock_location_ext(osv.TransientModel):
    _name = "stock.location.ext"
    _columns = {
        'location_id': fields.many2one('stock.location','Location',domain="[('usage', '=', 'internal')]"),
        'report_location_id' : fields.many2one('daily.stock.report', 'Stock Report'),
    }

stock_location_ext()

class product_stock_ext(osv.TransientModel):
    _name = "product.stock.ext"
    _columns = {
        'product_id': fields.many2one('product.product','Product',domain="[('type', '!=', 'service')]"),
        'report_product_id' : fields.many2one('daily.stock.report', 'Stock Report'),
    }

product_stock_ext()

class daily_stock_report(osv.osv_memory):
    _name = "daily.stock.report"
           
    def act_getstockreport(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids, context=context)[0]
        
        #check of location           
        if not this.location_ids:
            raise osv.except_osv(_('Warning'), _('Please select Location'))
        
        report_date = this.report_date
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        obj_precision = self.pool.get('decimal.precision')
        
        account_prec = obj_precision.precision_get(cr, uid, 'Account')
        price_prec = obj_precision.precision_get(cr, uid, 'Product Price')
        
        product_ids =[]
        # if spec a category
        if this.category_ids:
            this.product_ids and product_ids.extend([prod.product_id.id for prod in this.product_ids])
        
            for category in this.category_ids:
                category_product_ids = product_obj.search(cr,uid,[('categ_id', 'child_of', category.category_id.name)])
                product_ids.extend(category_product_ids)
        
            product_ids = list(set(product_ids))
        
        #location is mandatory

        locations = [loc.location_id for loc in this.location_ids]
        locations = list(set(locations))

        prod_dict = {}

        #if dont specify a product get all products id in product_ids
        if not this.product_ids:
            
            product_ids = data_ids = self.pool.get('product.product').search(cr, uid, [])
            
        
        #get all products from product_ids list
        for product in product_obj.browse(cr, uid, product_ids, context):
            prod_dict[product.name] = product

        prod_name_sorted = sorted(prod_dict)
        
        all_location_data = []
        
        # create pdf
        pdf=FPDF()
        pdf.add_page()
        #import font DejaVu with unicode
        pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        #set size 16 for title
        pdf.set_font('DejaVu','',16)
        #use ustr for unicode string
        #change date format
        fecha=datetime.strptime(report_date, '%Y-%m-%d')
        titulo = ustr('EXISTENCIAS A FECHA: ' + str(fecha.strftime('%d-%m-%Y')))
        ##add cell to pdf
        pdf.cell(40,10,titulo,'C')
        # add line to pdf
        pdf.ln(15)

        pdf.set_font('DejaVu','',8)
        pdf.cell(80,10,'Producto')
        pdf.cell(15,10,'Ref.')
        pdf.cell(20,10,'UdM')
        
        # header of pdf
        
        for each_location in locations:
            if this.show_opening:
                pdf.cell(30,10, ustr('Inicial- '+ ustr(each_location.name)))
            if this.show_incoming:
                pdf.cell(30,10, ustr('Entrante- '+ ustr(each_location.name)))
            if this.show_outgoing:
                pdf.cell(30,10, ustr('Saliente- '+ ustr(each_location.name)))
            
            pdf.cell(30,10,ustr('Cant.- '+ustr(each_location.name)))
                                   
            pdf.cell(30,10,ustr('Val.- '+ustr(each_location.name)))
        pdf.ln(15)

        # total value of stock
        total_val = 0.0

        for each_prod_name in prod_name_sorted:
            product = prod_dict[each_prod_name]
            all_location_product_data_dic ={}
            product_location_dic = {}
            
            ### Fetching UoM for each product and finding its factor
            if product.uom_id.category_id.name == 'Weight':
                reference_unit = this.weight_uom_id
                product_uom = product.uom_id
                
                factor = 1 / product_uom.factor
                factor = factor * reference_unit.factor
            else:
                reference_unit = product.uom_id
                factor = 1
            
            for each_location in locations:
                opening_stock = 0.0
                total_incoming_stock = 0.0
                total_outgoing_stock = 0.0
                closing_stock = 0.0
                product_costing = 0.0
                
                ### Opening Stock
                if this.show_opening:
                    cr.execute("SELECT SUM(h.quantity) FROM stock_history h, stock_move m WHERE h.move_id=m.id AND h.product_id=%s AND h.location_id=%s AND m.date < %s GROUP BY h.product_id",
                               (product.id, each_location.id, this.report_date_start + ' 00:00:00'))
                    res = cr.fetchone()
                    opening_stock_temp = res and res[0] or 0.0
                    opening_stock_temp = opening_stock_temp * factor
                    opening_stock = round(opening_stock_temp, account_prec)
                
                ### Total Incoming
                if this.show_incoming:
                    cr.execute("SELECT SUM(h.quantity) \
                                FROM stock_history h, stock_move m \
                                WHERE h.move_id=m.id AND \
                                h.product_id=%s AND h.location_id=%s AND h.quantity > 0 AND \
                                m.date >= %s AND m.date <= %s \
                                GROUP BY h.product_id",
                               (product.id, each_location.id, this.report_date_start + ' 00:00:00', this.report_date + ' 23:59:59'))
                    res = cr.fetchone()
                    total_incoming_stock_temp = res and res[0] or 0.0
                    total_incoming_stock_temp = total_incoming_stock_temp * factor
                    total_incoming_stock = round(total_incoming_stock_temp, account_prec)
                
                ### Total Outgoing
                if this.show_outgoing:
                    cr.execute("SELECT SUM(h.quantity) \
                                FROM stock_history h, stock_move m \
                                WHERE h.move_id=m.id AND \
                                h.product_id=%s AND h.location_id=%s AND h.quantity < 0 AND \
                                m.date >= %s AND m.date <= %s \
                                GROUP BY h.product_id",
                               (product.id, each_location.id, this.report_date_start + ' 00:00:00', this.report_date + ' 23:59:59'))
                    res = cr.fetchone()
                    total_outgoing_stock_temp = res and res[0] or 0.0
                    total_outgoing_stock_temp = total_outgoing_stock_temp * factor * -1
                    total_outgoing_stock = round(total_outgoing_stock_temp, account_prec)
                
                ### Closing Stock
                this_day = time.strftime('%Y-%m-%d')
                if this_day == this.report_date:
                    cr.execute("SELECT SUM(qty) FROM stock_quant WHERE product_id=%s AND location_id=%s GROUP BY product_id",
                        (product.id, each_location.id))
                else:
                    cr.execute("SELECT SUM(h.quantity) FROM stock_history h, stock_move m WHERE h.move_id=m.id AND h.product_id=%s AND h.location_id=%s AND m.date <= %s GROUP BY h.product_id",
                           (product.id, each_location.id, this.report_date + ' 23:59:59'))
                res = cr.fetchone()
                closing_stock_res = res and res[0] or 0.0
                closing_stock_temp = closing_stock_res * factor
                closing_stock = round(closing_stock_temp, account_prec)

                
                product_costing_temp = closing_stock_res * product.standard_price
                product_costing = round(product_costing_temp, price_prec)
                    
                location_dic={
                    'product_name': product.name or '',
                    'product_reference': product.default_code or product.ean13 or '',
                    'uom': reference_unit.name,
                    'closing_stock': closing_stock,
                }
                if this.show_opening:
                    location_dic['opening_stock'] = opening_stock
                if this.show_incoming:
                    location_dic['incoming'] = total_incoming_stock
                if this.show_outgoing:
                    location_dic['outgoing'] = total_outgoing_stock
                
                location_dic['product_cp'] = product_costing
                # acumulate total value
                total_val += product_costing

                product_location_dic[each_location.id]=location_dic
            all_location_product_data_dic[product.id]=product_location_dic
            all_location_data.append(all_location_product_data_dic)
        #

              
        # create lines of report    
        if this.action == 'individual':
            for data in all_location_data:
                
                for prod_id,loc_data in data.iteritems():
                    value_list=[]
                    for loc_id,loc_value in loc_data.iteritems():
                        product_name = ustr(loc_value['product_name'])
                        product_reference = loc_value['product_reference']
                        uom = loc_value['uom']
                        break
                        
                    
                    pdf.cell(80,10,ustr(product_name))   
                     
                    pdf.cell(15,10,ustr(product_reference))  
                    
                    pdf.cell(20,10,ustr(uom))
                    
                    for each_location in locations:
                        loc_value = loc_data[each_location.id]
                        if this.show_opening:
                            opening_stock = loc_value['opening_stock']
                            
                            pdf.cell(30,10,ustr(loc_value['opening_stock']))
                            
                        if this.show_incoming:
                            
                            pdf.cell(30,10,ustr(loc_value['incoming']))
                        if this.show_outgoing:
                            
                            pdf.cell(30,10,ustr(loc_value['outgoing']))
                        
                        
                        pdf.cell(30,10,ustr(loc_value['closing_stock']))
                            
                                    
                        pdf.cell(30,10,ustr(str(loc_value['product_cp']) + "€"))
                            
                                        
                    pdf.ln()

            pdf.ln()
            pdf.cell(45,10,'  ')
            pdf.cell(100,10,ustr('Valoración Total de Existencias: '))
            pdf.cell(30,10,ustr(str(total_val) + "€"))
            #encode pdf in binary for store in field
            data = base64.b64encode(pdf.output(dest='S'))
            name = "%s.pdf" % ("Informe_de_stock_"+report_date)
             
        
        this.write({ 'state': 'get', 'data': data, 'name': name })
               
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'daily.stock.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        
    def _get_default_weight_uom_id(self, cr, uid, context=None):
        uom_categ_ids = self.pool.get('product.uom.categ').search(cr, uid, [('name','=','Weight')])
        if not uom_categ_ids:
            return False
        
        uom_ids = self.pool.get('product.uom').search(cr,uid,[('category_id','=',uom_categ_ids[0]),('uom_type','=','reference')])
        if not uom_ids:
            return False
        
        return uom_ids[0]

    _columns = {
            'name': fields.char('File Name', readonly=True),
            'report_date_start': fields.date('Start Date'),
            'report_date': fields.date('End Date'),
            'location_ids': fields.one2many('stock.location.ext','report_location_id', 'Location'),
            'product_ids': fields.one2many('product.stock.ext','report_product_id', 'Products'),
            'category_ids': fields.one2many('product.category.ext','report_category_id', 'Category'),
            'weight_uom_id': fields.many2one('product.uom', 'Weight UoM', required=True),
            'data': fields.binary('File', readonly=True),
            'action': fields.selection([('individual', 'Individual'),('combined', 'Combined')],'Action'),
            'show_incoming': fields.boolean('Incoming'),
            'show_outgoing': fields.boolean('Outgoing'),
            'show_opening': fields.boolean('Opening'),
            'show_valuation': fields.boolean('Valuation'),
            'state': fields.selection([('choose', 'choose'),   # choose date
                                       ('get', 'get')])        # get the report
    }
    _defaults = {
        'state': 'choose',
        'report_date_start': '2000-01-01',
        'report_date': time.strftime('%Y-%m-%d'),
        'action': 'individual',
        'show_incoming': False,
        'show_outgoing': False,
        'show_opening': False,
        'show_valuation': False,
        'weight_uom_id': _get_default_weight_uom_id
    }