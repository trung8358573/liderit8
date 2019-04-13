# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import api, fields, models, _

import logging
logger = logging.getLogger(__name__)
#variable global para llevar los user_id de una funcion a otra
listids=[]

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    def _count_task(self, user_id):
        tasks = self.env['project.task'].search([('stage_closed','=',False)])
        count = 0
        global listids
        for t in tasks:
            if t.user_ids:
                users = t.user_ids
                for u in users:
                    #logger.error('En count task el id del usuario es %s'%user_id)
                    #logger.error('En count task buscando hr = usuario %s'%u.id)
                    if user_id == u.id:
                        #logger.error('En count task encontrado usuario %s'%u.name)
                        listids.append(t.id)
                        #logger.error('En count task agregado task id %s'%t.id)
                        count += 1
        #logger.error('En count task encontrado usuario %s'%u.name)
        #logger.error('En count task devuelve lista de task %s'%listids)
        return count

    @api.multi
    @api.depends('user_id')
    def compute_tasks_count(self):
        # usr_id = 0
        ir_model_data = self.env['ir.model.data']
        search_view_id = ir_model_data.get_object_reference('project', 'view_task_search_form')[1]
        global listids
        listids=[]
    	for each in self:
            if each.user_id:
                # project_task_ids = self.env['project.task'].search([('user_ids','in',each.user_id.id)])
                # length_count = len(project_task_ids)
                length_count = self._count_task(each.user_id.id)
                each.task_count = length_count
                #logger.error('Despues del count task valor lista de task %s'%listids)
                # usr_id = each.user_id.id
            else:
                pass
        #m_domain = {'user_ids': [('id', 'in', listids)]}
        return{
            'name':'Employee Task',
            'res_model':'project.task',
            'type':'ir.actions.act_window',
            'view_type':'list',
            'view_mode':'list,form,kanban,calendar,pivot,graph',
            #'context':{'group_by':'stage_id'},
            #'domain': [('user_id', '=', usr_id)],
            #'domain':m_domain,
            'domain':[('id','in',listids)],
            'search_view_id':search_view_id,
         }

    task_count = fields.Integer(compute=compute_tasks_count,string='Task Count',readonly=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: