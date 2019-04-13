# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class res_bank_bicdata(models.TransientModel):
    _name = "res.bank.bicdata"


    @api.model
    def _get_bic_code(self):
        
        if self.env.context.get('active_model', '') == 'res.partner.bank':            
            ids = self.env.context['active_ids']

            p_obj = self.env['res.partner.bank']
            p = p_obj.browse(ids)

            bank_obj = self.env['res.bank']

            # _logger.error('##### AIKO ###### En img_asoc con valor de active_ids: %s' % ids)
           
            for s in p:
            	bank_acc_number = False
            	if s.acc_number and len(s.acc_number)>9:
            		bank_acc_number = s.acc_number[5:9]
            		_logger.error('######## AIKO _get_bic_code valor de code  %s ####### ->'%bank_acc_number)

            		bank_data = bank_obj.search([('code','like',bank_acc_number),('country','=',69)])
            		if bank_data:
            			s.bank = bank_data[0].id
            			s.bank_bic = bank_data[0].bic
            			s.bank_name = bank_data[0].name


        return {}


    @api.multi
    def set_bic_code(self):
    	for s in self:
        	s._get_bic_code()
        	return




    
