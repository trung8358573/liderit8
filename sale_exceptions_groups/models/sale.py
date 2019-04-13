# -*- coding: utf-8 -*-
#
#

from openerp import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class sale_exception(models.Model):
    _inherit = 'sale.exception'
    groups_ids = fields.Many2many(
        'res.groups',
        'groups_exception_rel', 'e_id', 'g_id',
        string='Groups')

class res_groups(models.Model):
    _inherit = 'res.groups'   
    groups_exception_ids = fields.Many2many(
        'sale.exception',
        'groups_exception_rel', 'g_id', 'e_id',
        string='Exceptions')
    
class sale_order(models.Model):
    _inherit = 'sale.order'    
    @api.multi
    def _detect_exceptions(self, order_exceptions,
                           line_exceptions):
        #_logger.error('######## AIKO 1 ####### ->\n'+ str(self) + '\n'+ str(order_exceptions) + '\n'+ str(line_exceptions) + '\n')
        self.ensure_one()
        exception_ids = []
        for rule in order_exceptions:
            #_logger.error('######## AIKO 2 ####### ->\n'+ str(rule) + '\n')
            if self._rule_eval(rule, 'order', self): 
                if self.control_groups(rule):               
                    exception_ids.append(rule.id)
                
        for order_line in self.order_line:            
            for rule in line_exceptions:
                #_logger.error('######## AIKO 3 ####### ->\n'+ str(order_line) + '\n')
                if rule.id in exception_ids:
                    # we do not matter if the exception as already been
                    # found for an order line of this order
                    continue
                if self._rule_eval(rule, 'line', order_line):
                    if self.control_groups(rule): 
                        exception_ids.append(rule.id)                    
        return exception_ids
    @api.multi
    def control_groups(self, rule):        
        #_logger.error('######## AIKO control_groups ####### ->\n'+ str(rule) + '\n')
        if not rule.groups_ids:
            #_logger.error('######## AIKO control_groups no tenemos nada en groups_ids ####### ->\n'+ str(rule) + '\n')
            return True  
#        user = self.env['res.users'].browse(self._uid)
        user = self.env.user
        for group in rule.groups_ids:       
#             group_id = self.env.ref(group).id
            if group in user.groups_id:
                #_logger.error('######## AIKO control_groups encontrado ####### ->\n'+ str(rule) + '\n')
                return False
        #_logger.error('######## AIKO control_groups no encontrado ####### ->\n'+ str(rule) + '\n')
        return True
