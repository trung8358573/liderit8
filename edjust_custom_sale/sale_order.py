# -*- encoding: utf-8 -*-
##############################################################################
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tools import ustr
import calendar

from datetime import date, datetime

import logging
logger = logging.getLogger(__name__)

VALUES = [('1','Enero'),
        ('2','Febrero'),
        ('3','Marzo'),
        ('4','Abril'),
        ('5','Mayo'),
        ('6','Junio'),
        ('7','Julio'),
        ('8','Agosto'),
        ('9','Septiembre'),
        ('10','Octubre'),
        ('11','Noviembre'),
        ('12','Diciembre')]


class edjust_sale_medio(models.Model):
    _name = 'edjust.sale.medio'

    def _ediciones_count(self):
        ediciones = self.env['edjust.sale.edicion']
        result = {}
        for pub in self:
            pub.ediciones_count = ediciones.search_count([('medio_id', '=', pub.id)])


    name = fields.Char(_('Publication'), size=100)
    categ_id = fields.Many2one ('product.category',string=_('Related category'),required=True)
    product_id = fields.Many2one ('product.product',string=_('Related product'),required=True)
    ediciones_count = fields.Float(compute='_ediciones_count', string=_('Editions'),store=True)
    pub_interval = fields.Integer(string=_('Billed each'), help=_('It is billed each X (days, weeks....'))
    pub_rule_type =  fields.Selection([
            ('dayly', _('Day(s)')),
            ('weekly', _('week(s)')),
            ('monthly', _('Mounth(s)')),
            ('yearly', _('Year(s)')),
            ], _('Frecuency'), help=_("It is billed with this frecuency"))

# para poder limitar en medios un solo template por medio
class ProductTemplate(models.Model):
    _inherit = "product.product"

    edjust_medio_ids = fields.One2many('edjust.sale.medio', 'product_id', ondelete='cascade')



class edjust_sale_edicion(models.Model):
    _name = 'edjust.sale.edicion'

    def default_year(self):
        t_year = datetime.now().strftime("%Y")
        t_year=int(t_year)
        return t_year


    name = fields.Char(_('Edition'), size=100, required = True)
    year = fields.Integer (_('Year of Edition'), default=default_year)

    mes_desde = fields.Selection(
        VALUES,
        string=_("From mounth"))
    mes_hasta = fields.Selection(
        VALUES,
        string=_("To mounth"))
    medio_id = fields.Many2one ('edjust.sale.medio', string=_('Publication medium'), required=True)
    compromiso_ids = fields.One2many ('edjust.compromiso','sale_edicion',string=_('Editorial commitments'))
    difusion_ids = fields.One2many ('edjust.difusion','edicion_id',string=_('Diffusion list'))
    

    

    @api.onchange('mes_hasta')
    def _onchange_mes_hasta(self):
        if self.year and self.mes_desde and self.mes_hasta:
            valdesde=""
            valhasta=""
            for v in VALUES:
                if self.mes_desde == v[0]:
                    valdesde= v[1]

                if self.mes_hasta == v[0]:
                    valhasta= v[1]

            if self.name == False:
                self.name = valdesde+" / "+valhasta+" de "+str(self.year)


    #create diffusion list of this edition
    @api.multi
    def do_create_dist_list(self):
       
        
        #load models
        difusion_obj = self.env['edjust.difusion']
        difusion_line_obj = self.env['edjust.difusion.lines']

        # composicion de fechas de edición para comparar con las de contrato
        fecha_mes_desde = datetime.strptime('01-' + str(self.mes_desde) + '-'+ str(self.year), '%d-%m-%Y')
        
        #fecha_mes_hasta = datetime.strptime('01-' + str(self.mes_hasta) + '-'+ str(self.year), '%d-%m-%Y')
        
        #creamos un difusion nueva con la fecha actual.
        #componemos el nombre de la difusion con la publicacion, la edicion y la fecha
        fecha_hoy= datetime.now()
        nombre_difusion = self.medio_id.name + ', '+ self.name + ', '+str(str(fecha_hoy.strftime('%d-%m-%Y')))
        idf=difusion_obj.create ({'name': nombre_difusion, 'edicion_id': self.id, 'medio_id': self.medio_id.id, 'difusion_date': fecha_hoy})

        # iteramos el recordset obrenido con la fecha de contrato menor o igual a la composicion de fecha desde de la publicación, del medio de esta
        # edicion y que no tengan fecha de fin
        for contrato in self.env['account.analytic.account'].search([('date_start','<=',fecha_mes_desde),
            ('medio_id.id','=',self.medio_id.id),('date','=',False)]):
            # componemos el campo con el nombre del cliente y el nombre de contrato
            nombre_comp=str(contrato.partner_id.name +', '+ contrato.name)
            # establecemos el tipo de contrato por defecto en S (suscripción), si es gratuito se cambia posteriormente a G.
            contra_tipo = 'S'
            if contrato.gratuito:
                contra_tipo = 'G'
                        
            # si el cliente no tine los enviso retenidos, se almancena en difusion
            if not contrato.partner_id.cust_reten:
                # se guarda el registro en el modelo de difusion. no funciona si se divide la linea
                difusion_line_obj.create({ 'name': nombre_comp, 'difusion_id': idf.id,'partner_id': contrato.contact_partner_id.id, 'difusion_type': contra_tipo, 'num_ejemplares': contrato.num_ejemplares })
                
        # iteramos el recordset de pedidos que pertenecen a esta edicion y no estan ni en borrador ni cancelados
        for pedido in self.env['sale.order.line'].search([('edicion_id.id','=', self.id), ('state','!=', 'draft'), ('state','!=','cancel')]):
            #componer nombre
            nombre_comp = pedido.order_id.partner_id.name + ', ' + self.medio_id.name +', '+ self.name +', '+ pedido.order_id.name

            if not pedido.partner_id.cust_reten:
                difusion_line_obj.create({ 'name': nombre_comp, 'difusion_id': idf.id,'partner_id': pedido.order_id.partner_shipping_id.id, 'difusion_type': 'A', 'num_ejemplares': 1 })
            



    # @api.onchange('year')
    # def _onchange_year(self):
    #     if self.year and self.mes_desde and self.mes_hasta:
    #         valdesde=""
    #         valhasta=""
    #         for v in VALUES:
    #             if self.mes_desde == v[0]:
    #                 valdesde= v[1]

    #             if self.mes_hasta == v[0]:
    #                 valhasta= v[1]

    #         self.name = valdesde+" / "+valhasta+" de "+str(self.year)


class sale_order(models.Model):
    _inherit = "sale.order"

    internal_note = fields.Text(string=_('Internal observations'))
    sale_pub = fields.Many2one ('edjust.sale.medio', string = _('Publication medium'))
    sale_gen_categ = fields.Many2one(string=_('General Category'),related='sale_pub.categ_id')
    sale_subcateg = fields.Many2one ('product.category', string=_('Product type'))
    sale_edicion = fields.Many2one ('edjust.sale.edicion', string = _('Edition of the publication'))
    sale_med_edicion = fields.Char (string=_('Medium and Edition'), compute='_texto_mededicion', store = True)
    no_avisar = fields.Boolean (string=_('not notify partner'), default=False)
    contacto_aviso=fields.Many2one (relation='rel_sale_order_partner',comodel_name='res.partner', string=_('Notify contact'), required=True)

    @api.onchange('sale_pub', 'sale_edicion')
    @api.depends('sale_pub', 'sale_edicion')
    def _texto_mededicion(self):
        for s in self:
            if s.sale_pub and s.sale_edicion:
                s.sale_med_edicion = s.sale_pub.name + " "+ s.sale_edicion.name

   

class edjust_tipo_compromiso(models.Model):
    _name = 'edjust.tipo.compromiso'

    name= fields.Char(string=_('communication type'),required=True)


class edjust_compromiso(models.Model):
    _name = 'edjust.compromiso'


    name = fields.Char (string=_('Summary commitment'),required=True)
    sale_pub = fields.Many2one ('edjust.sale.medio', string = _('Publication medium'),required=True)
    sale_edicion = fields.Many2one ('edjust.sale.edicion', string = _('Edition of the publication'),required=True)
    sale_med_edicion = fields.Char (string=_('Medium and Edition'), compute='_texto_mededicion', store = True)
    partner_id = fields.Many2one ('res.partner',string=_('Partner'),required=True)
    sale_id = fields.Many2one ('sale.order.line',string=_('Advertising Request'),required=True)
    tipo_id = fields.Many2one ('edjust.tipo.compromiso',string=_('communication type'),required=True)
    date = fields.Date (_('Date annotation'), default=datetime.now())
    extension = fields.Char (string=_('Extension'), size = 20)
    num_pagina = fields.Char (string=_('Page No.'), size = 20)
    notes = fields.Text (string=_('Observations'))
    notes_red = fields.Text (string=_('Annotations Writing'))
    realizado = fields.Boolean (string=_('Accomplished'), default=False)
    no_avisar = fields.Boolean (string=_('not notify partner'), default=False)
    contacto_aviso = fields.Many2one (relation='rel_compromiso_partner',comodel_name='res.partner', string=_('Notify contact'), required=True)

    @api.onchange('sale_pub', 'sale_edicion')
    @api.depends('sale_pub', 'sale_edicion')
    def _texto_mededicion(self):
        for s in self:
            if s.sale_pub and s.sale_edicion:
                s.sale_med_edicion = s.sale_pub.name + " "+ s.sale_edicion.name


class res_partner(models.Model):
    _inherit = "res.partner"

    comunicaciones_count = fields.Integer (string='Comunicaciones', compute='_count_comunicaciones', store=True)


    @api.multi
    def _count_comunicaciones(self):
        comunic = self.env['edjust.compromiso']
        for p in self:
            p.comunicaciones_count = comunic.search_count([('partner_id','=',p.id)])


    @api.multi
    def return_comunic_items(self):
            domain = [('partner_id', '=', self.id)]
            return {
                'type': 'ir.actions.act_window',
                'name': _('Commitments Drafting'),
                'res_model': 'edjust.compromiso',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_id': self.id,
                'target': 'current',
                'domain': domain,
                'nodestroy': True,
                'flags': {'form': {'action_buttons': True}}
            }

# clase para recoger las distribuciones por edicion

class edjust_difusion(models.Model):

    _name='edjust.difusion'

    name =  fields.Char (_('Publication, Edition'), required = True)
    edicion_id = fields.Many2one (relation='rel_difusion_edition',comodel_name='edjust.sale.edicion', string = _('Edition'), required = True)
    medio_id =fields.Many2one(string=_('Publication'), related = 'edicion_id.medio_id', store =True)
    difusion_date = fields.Date(string=_('Diffusion Date'), required=True)
    num_subscriber = fields.Integer(string = _('Subscribers Copies'), compute='_ejemplares_subc', store=True)
    num_gratis = fields.Integer(string = _('Free Contract Copies'), compute='_ejemplares_free', store=True)
    num_anunci = fields.Integer(string = _('Advertiser Copies'), compute='_ejemplares_advert', store=True)
    num_invitado = fields.Integer(string = _('Guest Copies'), compute='_ejemplares_guest', store=True)
    difusion_line_ids = fields.One2many ('edjust.difusion.lines','difusion_id',string=_('Diffusion Lines'))
    total_difusion = fields.Integer(string=_('Total Copies'),compute='_ejemplares_difusion', store=True)
    enabled = fields.Boolean(string=_('Enabled'), default =True)
    edit_exclude_from = fields.Many2one(relation='rel_difus_edit_from_filter', comodel_name='edjust.edition.date.filter', string=_('Exclude from'))
    edit_exclude_to=fields.Many2one(relation='rel_difus_edit_to_filter',comodel_name='edjust.edition.date.filter', string=_('Exclude to'))
    activities_ids = fields.One2many('edjust.difusion.activities', 'difusion_id', string =_('Activities'))
    sectors_ids =fields.One2many('edjust.difusion.sectors', 'difusion_id', string =_('Sectors'))
    groups_ids =fields.One2many('edjust.difusion.groups', 'difusion_id', string =_('Groups'))
    positions_ids =fields.One2many('edjust.difusion.positions', 'difusion_id', string=_('Positions'))
    states_ids=fields.One2many('edjust.difusion.states', 'difusion_id', string=_('States'))
    country_ids=fields.One2many('edjust.difusion.country', 'difusion_id', string=_('Country'))
    page=fields.Integer(string='position', default=0)
    inicio=fields.Integer(string='inicio', compute='_calc_posible_editions')
    


    #recalc copies number when change lines of diffusion list
    #@api.onchange('difusion_line_ids')
    @api.depends('difusion_line_ids')
    def _ejemplares_difusion(self):
        for s in self:
            count = 0
            if s.difusion_line_ids:
                for d in s.difusion_line_ids:
                    count += d.num_ejemplares
            s.total_difusion = count
        #self.page=0
        

    @api.depends('difusion_line_ids')
    def _ejemplares_subc(self):
        for s in self:
            count = 0
            if s.difusion_line_ids:
                for d in s.difusion_line_ids:
                    if d.difusion_type=='S':
                        count += d.num_ejemplares
            s.num_subscriber = count

    @api.depends('difusion_line_ids')
    def _ejemplares_free(self):
        for s in self:
            count = 0
            if s.difusion_line_ids:
                for d in s.difusion_line_ids:
                    if d.difusion_type=='G':
                        count += d.num_ejemplares
            s.num_gratis = count

    @api.depends('difusion_line_ids')
    def _ejemplares_advert(self):
        for s in self:
            count = 0
            if s.difusion_line_ids:
                for d in s.difusion_line_ids:
                    if d.difusion_type=='A':
                        count += d.num_ejemplares
            s.num_anunci = count

    @api.depends('difusion_line_ids')
    def _ejemplares_guest(self):
        for s in self:
            count = 0
            if s.difusion_line_ids:
                for d in s.difusion_line_ids:
                    if d.difusion_type=='I':
                        count += d.num_ejemplares
            s.num_invitado = count

    @api.onchange('edit_exclude_from')
    def _onchange_edit_excludefrom(self):
        
        self.edit_exclude_to=self.edit_exclude_from
        

    
    def _calc_posible_editions(self):
        
        edition_obj=self.env['edjust.sale.edicion'].search([('medio_id','=',self.medio_id.id)])
        edition_exclude_obj= self.env['edjust.edition.date.filter']
        
               
        lista_ediciones=[]
        ediciones= edition_exclude_obj.search([('id','>',0)])
        for edic in ediciones:
            lista_ediciones.append(edic.edition_id.id)
        

        for edition in edition_obj:
            if edition.id not in lista_ediciones:
                fecha_mes_desde = datetime.strptime('01-' + str(edition.mes_desde) + '-'+ str(edition.year), '%d-%m-%Y')
                 #get last day in month
                st_month = int(edition.mes_hasta)
                st_year = int(edition.year)
                num_days = calendar.monthrange(st_year, st_month)[1]
                num_days = str(num_days)
                st_year = str(st_year)
                st_month = str(st_month)
                st_date = num_days+"-"+st_month+"-"+st_year
                fecha_mes_hasta = datetime.strptime(st_date,'%d-%m-%Y')
                #fecha_mes_hasta = datetime.strptime('01-' + str(edition.mes_hasta) + '-'+ str(edition.year), '%d-%m-%Y')
                
                edition_exclude_obj.create({'name': edition.name,
                    'edition_id': edition.id,
                    'medio_id': edition.medio_id.id,
                    'date_from': fecha_mes_desde,
                    'date_to': fecha_mes_hasta,
                    })
        
        
    def _calc_ediciones_ant(self):

        edition_obj=self.env['edjust.sale.edicion'].search([('medio_id','=',self.medio_id.id)])
        fecha_mes_desde=fecha_mes_hasta=False
        fecha_mes_desde = datetime.strptime('01-' + str(self.edit_exclude_from.edition_id.mes_desde) + '-'+ str(self.edit_exclude_from.edition_id.year), '%d-%m-%Y')
        #get last day in month
        st_month = int(self.edit_exclude_to.edition_id.mes_hasta)
        st_year = int(self.edit_exclude_to.edition_id.year)
        num_days = calendar.monthrange(st_year, st_month)[1]
        num_days = str(num_days)
        st_year = str(st_year)
        st_month = str(st_month)
        st_date = num_days+"-"+st_month+"-"+st_year
        fecha_mes_hasta = datetime.strptime(st_date,'%d-%m-%Y')

        #fecha_mes_hasta = datetime.strptime('01-' + str(self.edit_exclude_to.edition_id.mes_hasta) + '-'+ str(self.edit_exclude_to.edition_id.year), '%d-%m-%Y')
        

        excluded_ids=[]
        for edicion in edition_obj:
            edicion_mes_desde = datetime.strptime('01-' + str(edicion.mes_desde) + '-'+ str(edicion.year), '%d-%m-%Y')
             #get last day in month
            st_month = int(edicion.mes_hasta)
            st_year = int(edicion.year)
            num_days = calendar.monthrange(st_year, st_month)[1]
            num_days = str(num_days)
            st_year = str(st_year)
            st_month = str(st_month)
            st_date = num_days+"-"+st_month+"-"+st_year
            edicion_mes_hasta = datetime.strptime(st_date,'%d-%m-%Y')
            #edicion_mes_hasta = datetime.strptime('01-' + str(edicion.mes_hasta) + '-'+ str(edicion.year), '%d-%m-%Y') 
            
            if (edicion_mes_desde>=fecha_mes_desde) and (edicion_mes_hasta<=fecha_mes_hasta):
                for difus in edicion.difusion_ids:
                    excluded_ids.append(difus.id)
        return excluded_ids

    #calculate posible guests
    @api.multi
    def do_calculate_guests(self):


        #load models with all data
        activities_obj=self.env['edjust.partner.activities'].search([('id','>',0)])
        sectors_obj=self.env['edjust.sector'].search([('id','>',0)])
        groups_obj=self.env['edjust.partner.relation'].search([('id','>',0)])
        positions_obj=self.env['edjust.partner.position'].search([('id','>',0)])
        states_obj=self.env['res.country.state'].search([('id','>',0)])
        country_obj=self.env['res.country'].search([('id','>',0)])
        
        #load list of difusions to exclude, the actual and the specified in fields from and to.
        excluded_ids=[]
        
        
        if self.edit_exclude_from:
            excluded_ids=self._calc_ediciones_ant()

        excluded_ids.append(self.id)
        
        #load the difusion lines of the excluded lists
        difusion_lines_obj =self.env['edjust.difusion.lines'].search([('difusion_id','in',excluded_ids)])
        
        #delete all previus data of guests from this difusion list
        self.activities_ids.unlink()
        self.sectors_ids.unlink()
        self.groups_ids.unlink()
        self.positions_ids.unlink()
        self.states_ids.unlink()
        self.country_ids.unlink()
        
        #load models of filters for guests
        difusion_activ=self.env['edjust.difusion.activities']
        difusion_secto=self.env['edjust.difusion.sectors']
        difusion_group=self.env['edjust.difusion.groups']
        difusion_posit=self.env['edjust.difusion.positions']
        difusion_state=self.env['edjust.difusion.states']
        difusion_count=self.env['edjust.difusion.country']

        #create list of posible guests
        guests=[]

        cont=0   
        #load model of all partners     
        all_clients = self.env['res.partner'].search([('customer','=',True),('type','=','contact')])
        
        #for all partners        
        for clientes in all_clients:
            #for each partner compare with the lines of diffusion list excluded, if found in this list, change sw encontrado.
            encontrado=0
            for lines in difusion_lines_obj:
                
                if clientes.id==lines.partner_id.id:
                    encontrado =1
            #if not changed sw encontrado, not found in excluded list and add to de posible guests ids list.
            if encontrado == 0:
                guests.append(clientes.id)

        #for all activities
        for activity in activities_obj:
            cont=0
            #for each partner in posible guests
            for cliente in guests:
                #load record of client whit the id of the list
                client = self.env['res.partner'].browse(cliente)
                #for all activities of this partner if the activity compared is in the partner activities sum 1 to counter
                for act_client in client.cust_activities:

                    if activity.id == act_client.id:
                        cont+=1
            #only rec the data in model if there is more than 0 partners
            if cont>0:
                #create record  whit this difusion_id, actual activity_id of iteration and counter of partners with this activity
                idf = difusion_activ.create({'difusion_id': self.id,
                                  'activity_id': activity.id,
                                  'quantity': cont,
                                  })
        
        #same logic that activities
        for sector in sectors_obj:
            cont=0
            for cliente in guests:
                client = self.env['res.partner'].browse(cliente)
               
                for sec_client in client.cust_sector:

                    if sector.id == sec_client.id:
                        cont+=1

            if cont>0:
                idf = difusion_secto.create({'difusion_id': self.id,
                                  'sector_id': sector.id,
                                  'quantity': cont,
                                  })

        #same logic that activities
        for group in groups_obj:
            cont=0
            for cliente in guests:
                client = self.env['res.partner'].browse(cliente)
               
                for group_client in client.cust_relation2:

                    if group.id == group_client.id:
                        cont+=1
            if cont>0:
                idf = difusion_group.create({'difusion_id': self.id,
                                  'group_id': group.id,
                                  'quantity': cont,
                                  })

        #same logic that activities
        for position in positions_obj:
            cont=0
            for cliente in guests:
                client = self.env['res.partner'].browse(cliente)
               
                for pos_client in client.cust_position:

                    if position.id == pos_client.id:
                        cont+=1
            if cont>0:
                idf = difusion_posit.create({'difusion_id': self.id,
                                  'position_id': position.id,
                                  'quantity': cont,
                                  })
        
        #same logic that activities
        for state in states_obj:
            cont=0
            for cliente in guests:
                client = self.env['res.partner'].browse(cliente)
               
                for sta_client in client.state_id:

                    if state.id == sta_client.id:
                        cont+=1
            if cont>0:
                idf = difusion_state.create({'difusion_id': self.id,
                                  'state_id': state.id,
                                  'quantity': cont,
                                  })

        
        #same logic that activities
        for country in country_obj:
            cont=0
            for cliente in guests:
                client = self.env['res.partner'].browse(cliente)
               
                for coun_client in client.country_id:
                    
                    if country.id == coun_client.id:
                        cont+=1
            if cont>0:
                idf = difusion_count.create({'difusion_id': self.id,
                                  'country_id': country.id,
                                  'quantity': cont,
                                  })


    #change the page value to show the tree linked to the button pressed and call to calculate posible guests.
    #implemented with buttons becouse the onchange metod fails with unlink () used in do_calculate_guests
    @api.multi
    def do_calculate_activities(self):
        self.page=1
        self.do_calculate_guests()        

    @api.multi
    def do_calculate_sectors(self):
        self.page=2
        self.do_calculate_guests()

    @api.multi
    def do_calculate_groups(self):
        self.page=3
        self.do_calculate_guests()

    @api.multi
    def do_calculate_positions(self):
        self.page=4
        self.do_calculate_guests()

    @api.multi
    def do_calculate_states(self):
        self.page=5
        self.do_calculate_guests()

    @api.multi
    def do_calculate_countries(self):
        self.page=6
        self.do_calculate_guests()

    #call wizard to apply filters an add guests.
    #implemented with code to call do_calculate_guests before launch wizard 
    @api.multi
    def call_wizard_actl(self):
        
        
        
        self.do_calculate_guests()
        fecha_mes_desde=fecha_mes_hasta=False
        if self.edit_exclude_from:
            
            fecha_mes_desde = datetime.strptime('01-' + str(self.edit_exclude_from.edition_id.mes_desde) + '-'+ str(self.edit_exclude_from.edition_id.year), '%d-%m-%Y')
             #get last day in month
            st_month = int(self.edit_exclude_from.edition_id.mes_hasta)
            st_year = int(self.edit_exclude_from.edition_id.year)
            num_days = calendar.monthrange(st_year, st_month)[1]
            num_days = str(num_days)
            st_year = str(st_year)
            st_month = str(st_month)
            st_date = num_days+"-"+st_month+"-"+st_year
            fecha_mes_hasta = datetime.strptime(st_date,'%d-%m-%Y')
            #fecha_mes_hasta = datetime.strptime('01-' + str(self.edit_exclude_from.edition_id.mes_hasta) + '-'+ str(self.edit_exclude_from.edition_id.year), '%d-%m-%Y')

        #load wizard form view
        wizard_form = self.env.ref('edjust_custom_sale.view_filter_difusion_list_wizard', False)
        #create record to pass values of this model to new wizard window
        view_id = self.env['edjust.difusion.list.wizard']
         
        vals = {
                'difusion_id': self.id,
                'edicion_id': self.edicion_id.id,
                'date_exclude_from': fecha_mes_desde,
                'date_exclude_to': fecha_mes_hasta,
                }
        new = view_id.create(vals)
        #call wizard form pass the new record created.
        return {
                'name'      : _('Add partners to list'),
                'type'      : 'ir.actions.act_window',
                'res_model' : 'edjust.difusion.list.wizard',
                'res_id'    : new.id,
                'view_id'   : wizard_form.id,
                'view_type' : 'form',
                'view_mode' : 'form',
                'target'    : 'new'
                }
        
    @api.multi
    def open_difusion_lines(self):
        view_id = self.env['ir.ui.view'].search([('name','=','view_edjust_difusion_line_tree1')]).id
        
        return {
            'name':'Lines',
            'view_type':'form',
            'view_mode':'tree',
            'res_model':'difusion.line.label',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            #'res_id':self.id,
            'target':'current',
            'domain': [('difusion_id','=', self.id)],
            
        }   
        



        

    #creación masiva de clientes para probar, boton en distribución
    # @api.multi
    # def do_create_clients(self):

    #     num=0
    #     clie_obj = self.env['res.partner'].search([('id','>',0)])
    #     actividad=1
        
    #     grupo = 1
    #     print clie_obj
        
    #     for cli in clie_obj:
    #         nombre='cliente '+str(num)

    #         if num>30:
    #             actividad=2
    #         if num>60:
    #             actividad=3
    #         if num>90:
    #             actividad=4

    #         if num>120:
    #             actividad=5
    #         if num>150:
    #             actividad=6
    #         if num>100:
    #             grupo=3

            
    #         print cli.id
            
    #         cli.cust_activities = [(4,actividad)]
    #         cli.cust_relation2 = [(4,grupo)]
    #         # idf=clie_obj.create({'name': nombre,
    #         #     'cust_activities': actividad,
    #         #     'cust_relation2':grupo,
    #         #     })

            
    #         print cli.cust_activities
    #         num +=1

    
    

#lineas de difusion   
class edjust_difusion_lines(models.Model):
    
    _name = 'edjust.difusion.lines'

    name =  fields.Char (_('Partner name, Subscription or Concept'), required = True)
    difusion_id = fields.Many2one ('edjust.difusion', string = _('Diffusion'), required = True, ondelete='cascade')
    partner_id=fields.Many2one('res.partner', string=_('Partner'), required =True)
    difusion_type = fields.Selection([
            ('S', _('Subscriber')),
            ('G', _('Free')),
            ('A', _('Advertiser')),
            ('I', _('Guest')),
            ], _('Subscriber Type'), help=_('Reason why it is included in the diffusion'), required=True)
    num_ejemplares = fields.Integer (string=_('Num of Copies'), required = True, default=1)



class edjust_difusion_list_wizard(models.TransientModel):

    _name = 'edjust.difusion.list.wizard'
    
    difusion_id = fields.Many2one ('edjust.difusion', string = _('Diffusion'))
    num_ejemplares = fields.Integer (string=_('Num of Copies'), default=1)
    inc_duplicados = fields.Boolean(string = _('Increase in duplicates'), default =False)
    
    activities_ids = fields.Many2many (relation='edlw_activities_epa_activites', comodel_name='edjust.partner.activities', string =_('Activities'))
    sectors_ids = fields.Many2many (relation='edlw_sector_es_activities', comodel_name='edjust.sector', string =_('Sectors'))
    groups_ids = fields.Many2many (relation='edlw_groups_rpr_groups',comodel_name='edjust.partner.relation', string =_('Groups'))
    positions_ids = fields.Many2many (relation='rel_wiz_partner_position',comodel_name='edjust.partner.position', string =_('Positions'))
    country_ids=fields.Many2many(relation='rel_wiz_country', comodel_name='res.country', string=_('Countries'))
    states_ids=fields.Many2many(relation='rel_wiz_state',comodel_name='res.country.state', string=_('States'))
    partners_ids=fields.Many2many(relation='rel_wiz_partner', comodel_name='res.partner', string=('Partners'))
    total_lista = fields.Integer(string=_('Subscriber & Advertisers Copies'))
    cont_inv = fields.Integer(string=_('Copies Guest'))
    date_exclude_from = fields.Date(string=_('Exclude from'))
    date_exclude_to=fields.Date(string=_('Exclude to'))
    edicion_id = fields.Many2one ('edjust.sale.edicion', string = _('Edition'))

    _DIFUSION_ID=0
      
    

    @api.multi
    def _inicializar(self):
        
        #global variable because the difusion id was lost in final record
        global _DIFUSION_ID
        
        #same logic in posible guests of edjust.difusion
        _guests =[]
       
               
        excluded_ids=[]
        
        
        if self.date_exclude_from:

            edition_obj=self.env['edjust.sale.edicion'].search([('medio_id','=',self.edicion_id.medio_id.id)])
            
            for edicion in edition_obj:
                edicion_mes_desde = datetime.strptime('01-' + str(edicion.mes_desde) + '-'+ str(edicion.year), '%d-%m-%Y')
                 #get last day in month
                st_month = int(edicion.mes_hasta)
                st_year = int(edicion.year)
                num_days = calendar.monthrange(st_year, st_month)[1]
                num_days = str(num_days)
                st_year = str(st_year)
                st_month = str(st_month)
                st_date = num_days+"-"+st_month+"-"+st_year
                edicion_mes_hasta = datetime.strptime(st_date,'%d-%m-%Y')
                #edicion_mes_hasta = datetime.strptime('01-' + str(edicion.mes_hasta) + '-'+ str(edicion.year), '%d-%m-%Y') 
                
                if (edicion_mes_desde>=datetime.strptime(self.date_exclude_from, '%Y-%m-%d')) and (edicion_mes_hasta<=datetime.strptime(self.date_exclude_to, '%Y-%m-%d')):
                    for difus in edicion.difusion_ids:
                        excluded_ids.append(difus.id)
            

        excluded_ids.append(self.difusion_id.id)    



        difusion_lines_obj =self.env['edjust.difusion.lines'].search([('difusion_id','in',excluded_ids)])

        _DIFUSION_ID=self.difusion_id.id
        
        all_clients = self.env['res.partner'].search([('customer','=',True),('type','=','contact')])
                
        for clientes in all_clients:
            
            encontrado=0
            for lines in difusion_lines_obj:
                
                if clientes.id==lines.partner_id.id:
                    encontrado =1

            if encontrado == 0:
                _guests.append(clientes.id)

        
       
        self.total_lista =self.difusion_id.total_difusion
    
        return(_guests)


    @api.onchange('activities_ids')
    def _rec_activ(self):

        
        self._recalcular()

    @api.onchange('sectors_ids')    
    def _rec_sectors(self):
        list_of_sectors=[]
        for sectors in self.sectors_ids:
            list_of_sectors.append(sectors.id)
        
        
        for activ in self.activities_ids:

            if activ.sector_id.id not in list_of_sectors:
                self.activities_ids=[(3,activ.id)]
        
        self._recalcular()
        

        if self.sectors_ids:
            return {'domain': {'activities_ids': [('sector_id', 'in', list_of_sectors)]}}
        else:
            
            return {'domain': {'activities_ids': []}}

    @api.onchange('groups_ids')    
    def _rec_groups(self):

        
        self._recalcular()

    @api.onchange('positions_ids')
    def _rec_positions(self):
        self._recalcular()

    @api.onchange('num_ejemplares')    
    def _rec_num(self):

        
        self._recalcular()

    @api.onchange('country_ids')    
    def _rec_country(self):

        
        self._recalcular()

    @api.onchange('states_ids')    
    def _rec_state(self):

        
        self._recalcular()

    @api.onchange('partners_ids')    
    def _rec_partner(self):

        print ('partner')
        self._recalcular()

    @api.multi
    def _recalcular (self):

        
        _guests=self._inicializar()

        
        guest_filtered=[]
        # if all fields are empty no calc and put count to 0 
        if not self.activities_ids and not self.sectors_ids and not self.groups_ids and not self.positions_ids and not self.country_ids and not self.states_ids:
            self.cont_inv=0
        else:
            
            #for all posible guests
            for cliente in _guests:
                sw_act=0
                sw_sec=0
                sw_gru=0
                sw_pos=0
                sw_cou=0
                sw_sta=0
                
                #load the partner of the actual id
                client = self.env['res.partner'].browse(cliente)
                #for all activities included in the filter
                for actividad in self.activities_ids:
                    #look in the actual client activities
                    for act_cli in client.cust_activities:
                        #if actual activity is in client activities change sw activity to 1
                        if (act_cli.id == actividad.id):
                            sw_act=1
                    #si en este punto el sw es 0 significa que hay actividades en el filtro, pero el cliente no las tiene en su lista
                    #si no hay actividades en el filtro no entra en este iterador.
                    #si se cambia 1 ya cumple al menos una de las actividades y no entrará en este if.
                    if sw_act==0:
                        sw_act=-1

                #same logic of activities
                for sector in self.sectors_ids:
                    for sector_cli in client.cust_sector:
                                            
                        if (sector_cli.id == sector.id):
                            sw_sec=1
                    if sw_sec==0:
                        sw_sec=-1

                #same logic of activities
                for grupo in self.groups_ids:
                    for grupo_cli in client.cust_relation2:
                                        
                        if (grupo_cli.id == grupo.id):
                            sw_gru=1
                    if sw_gru==0:
                        sw_gru=-1

                #same logic of activities
                for puesto in self.positions_ids:
                    for pos_cli in client.cust_position:
                        if (pos_cli.id == puesto.id):
                            sw_pos=1            
                    if sw_pos==0:
                        sw_pos=-1
                
                #same logic of activities
                for pais in self.country_ids:
                    for pais_cli in client.country_id:
                        if (pais_cli.id == pais.id):
                            sw_cou=1            
                    if sw_cou==0:
                        sw_cou=-1

                #same logic of activities
                for prov in self.states_ids:
                    for prov_cli in client.state_id:
                        if (prov_cli.id == prov.id):
                            sw_sta=1            
                    if sw_sta==0:
                        sw_sta=-1

                #only if all the sw are 0 or plus means that partener is in all fliters or neednt to evaluate filter because is empty.
                if (sw_act>=0) and (sw_sec>=0) and (sw_gru>=0) and (sw_pos>=0) and (sw_cou>=0) and (sw_sta>=0):
                    guest_filtered.append(client.id)

                
        
        #add all contacts of a partner to guests if not added previusly.
        for partner in self.partners_ids:
            
            for child in partner.child_ids:
                
                if (child.id not in guest_filtered):
                    guest_filtered.append(child.id)            
        #the total copies of guests is the number of guests append to with filters x copies number.
        self.cont_inv=len(guest_filtered) * self.num_ejemplares            
            
        
        return guest_filtered



    @api.multi
    def do_add_to_list(self):

        global _DIFUSION_ID
        #cargamos el modelo de clientes
        clie_obj = self.env['res.partner']

        dif_obj = self.env['edjust.difusion'].browse(_DIFUSION_ID)
        #carga todas las id seleccionadas en el tree que llama al asistente
        active_ids = self._recalcular()
        #busca todos los registros de esas ids en el modelo de clientes
        all_regs = clie_obj.browse(active_ids)
        
        idf_ids=[]
        
        #carga el modelo de lineas de difusion
        difusion_obj =self.env['edjust.difusion.lines']
        #itera todos los registros recuperados
        for cliente in all_regs:
            #crea una linea de lista por cada cliente invitado                   
            idf = difusion_obj.create({'name': cliente.name,
                                  'difusion_id': _DIFUSION_ID,
                                  'partner_id': cliente.id,
                                  'difusion_type': 'I',
                                  'num_ejemplares': self.num_ejemplares,
                                  })
        #put page to 0 to force push recalculate buttons in posible guests
        dif_obj.page=0

        #se carga la vista que vamos a visualizar al terminar el porceso
        #inv_view = self.env['ir.ui.view'].search([('name','=','edjust_difusion_list_tree')]).id
        inv_fview = self.env['ir.ui.view'].search([('name','=','edjust_difusion_form_view')]).id
        #en el return llama a la vista para visualizar los datos actualiza
        return {
                    'name': _('Distribution list'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'edjust.difusion',
                    'view_id': inv_fview,
                    'res_id': _DIFUSION_ID or False,
                    # 'context': "{}",
                    'target': 'current',
                }
#models for guests filter
class edjust_difusion_activities(models.Model):
    _name='edjust.difusion.activities'

    difusion_id=fields.Many2one('edjust.difusion', string=_('Diffusion'))
    quantity=fields.Integer(string=_('Quantity'))
    activity_id=fields.Many2one('edjust.partner.activities', string=_('Activity'))


class edjust_difusion_sectors(models.Model):
    _name='edjust.difusion.sectors'

    difusion_id=fields.Many2one('edjust.difusion', string=_('Diffusion'))
    quantity=fields.Integer(string=_('Quantity'))
    sector_id=fields.Many2one('edjust.sector', string=_('Sector'))

class edjust_difusion_groups(models.Model):
    _name='edjust.difusion.groups'

    difusion_id=fields.Many2one('edjust.difusion', string=_('Diffusion'))
    quantity=fields.Integer(string=_('Quantity'))
    group_id=fields.Many2one('edjust.partner.relation', string=_('Group'))

class edjust_difusion_positions(models.Model):
    _name='edjust.difusion.positions'

    difusion_id=fields.Many2one('edjust.difusion', string=_('Diffusion'))
    quantity=fields.Integer(string=_('Quantity'))
    position_id=fields.Many2one('edjust.partner.position', string=_('Position'))

class edjust_difusion_country(models.Model):
    _name='edjust.difusion.country'

    difusion_id=fields.Many2one('edjust.difusion', string=_('Diffusion'))
    quantity=fields.Integer(string=_('Quantity'))
    country_id=fields.Many2one('res.country', string=_('Country'))

class edjust_difusion_states(models.Model):
    _name='edjust.difusion.states'

    difusion_id=fields.Many2one('edjust.difusion', string=_('Difussion'))
    quantity=fields.Integer(string=_('Quantity'))
    state_id=fields.Many2one('res.country.state', string=_('State'))

#model for guests date filter
class edjust_edition_date_filter(models.Model):

    _name='edjust.edition.date.filter'

    name=fields.Char(string=_('Edition Name'))
    medio_id=fields.Many2one('edjust.sale.medio',string=_('Medium'))    
    edition_id=fields.Many2one('edjust.sale.edicion',string=_('Edition'))
    date_from=fields.Date(string=_('Date From'))
    date_to=fields.Date(string=_('Date To'))

#model for order line
class edjust_sale_order_line(models.Model):

    _inherit='sale.order.line'

    medio_id=fields.Many2one('edjust.sale.medio', string=_('Medium'))
    categ_id=fields.Many2one('product.category', string=_('Category'), related ='medio_id.categ_id')
    edicion_id=fields.Many2one('edjust.sale.edicion', string=_('Edition'))
    usable_tmpl_ids = fields.Many2many(
        comodel_name='product.template', string=_('Usable templates'),
        compute='_compute_usable')
    usable_product_ids = fields.Many2many(
        comodel_name='product.product', string=_('Usable products'),
        compute='_compute_usable')

    @api.onchange('edicion_id')
    @api.depends('edicion_id')
    def _edicion_id_onchange(self):
        
        if self.medio_id:
            self.name = str(self.product_id.name_template)+ ', ' +str(self.medio_id.name) + ', ' + str(self.edicion_id.name)


    @api.onchange('medio_id')
    @api.depends('medio_id')
    def _compute_usable(self):
        res = {}
        product_obj = self.env['product.template']
        for line in self:
            if line.categ_id:
                suppinfo = self.env['product.product'].search(
                    ['|',('categ_id', '=', line.categ_id.id),
                    ('categ_id', 'child_of', line.categ_id.id)])
                usable_tmpl_ids = suppinfo.mapped('product_tmpl_id')
            else:
                usable_tmpl_ids = product_obj.search(
                    [('sale_ok', '=', True)])

            line.usable_tmpl_ids = usable_tmpl_ids.filtered('sale_ok')
            line.usable_product_ids =\
                line.mapped(
                    'usable_tmpl_ids.product_variant_ids').filtered('sale_ok')

        res['domain'] = {'product_id': [('id', 'in', [l.id for l in line.usable_product_ids])]}

        return res

