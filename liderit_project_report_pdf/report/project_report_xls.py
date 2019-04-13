# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2009-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Nilmar Shereef(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx

import logging 
_logger = logging.getLogger(__name__)


class LideritProjectReportXls(ReportXlsx):

    #las funciones estan detalladas en http://xlsxwriter.readthedocs.io/
    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet()
        # ajustamos el ancho de las 10 primeras columnas a 10 px (23 mm):
        sheet.set_column(0, 10, 10)
        format1 = workbook.add_format({'font_size': 22, 'bg_color': '#D3D3D3'})
        format4 = workbook.add_format({'font_size': 22})
        format2 = workbook.add_format({'font_size': 10, 'bold': True, 'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10})
        format5 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF'})
        # agregamos un formato para fecha
        formatDat = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF', 'num_format': 'dd/mm/yyyy'})
        format7 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF'})
        format6 = workbook.add_format({'font_size': 22, 'bg_color': '#FFFFFF'})
        format7.set_align('center')
        if lines.company_id.state_id.name == False:
            state_name = ""
        else:
            state_name = lines.company_id.state_id.name
        if lines.company_id.country_id.name == False:
            country_name = ""
        else:
            country_name = lines.company_id.country_id.name
        sheet.merge_range('A1:B1', lines.company_id.name, format5)
        sheet.merge_range('A2:B2', lines.company_id.street, format5)
        sheet.write('A3', lines.company_id.city, format5)
        sheet.write('B3', lines.company_id.zip, format5)
        sheet.merge_range('A4:B4', state_name, format5)
        sheet.merge_range('A5:B5', country_name, format5)
        # sheet.merge_range('G1:H1', lines.company_id.rml_header1, format5)
        # informamos si hay un filtro aplicado
        if len(data['form']['stage_select']) != 0:
            sheet.merge_range('G1:H1', 'Filtro por tipo de tareas', format5)
        if len(data['form']['partner_select']) != 0:
            sheet.merge_range('G2:H2', 'Filtro por responsable de tarea', format5)

        # los rangos son los dos primeros para la primera celda por ejemplo 5, 0 es la celda A(pos. 0)6(pos. 5) = A6
        # y los segundos para una segunda celda, por ejemplo 6, 1 es la celda B(pos. 1)7(pos. 6) = B7
        # sheet.merge_range(5, 0, 6, 1, "Project  :", format1)
        sheet.merge_range(5, 0, 6, 1, "Proyecto  :", format1)
        # siguiendo el ejemplo el siguiente rango 5,2,6,7 es de la celda C6 a la celda H7
        sheet.merge_range(5, 2, 6, 7, lines.name, format1)
        # sheet.merge_range('A8:B8', "Project Manager    :", format5)
        sheet.merge_range('A8:B8', "Gestor del Proyecto :", format5)
        sheet.merge_range('C8:D8', lines.user_id.name, format5)
        if lines.date_start:
            date_start = lines.date_start
            # tenemos que tratar la cadena de texto y cambiar el orden del valor
            day_start = date_start[8:10]
            month_start = date_start[5:7]
            year_start = date_start[:4]
            date_start = day_start+"/"+month_start+"/"+year_start
        else:
            date_start = ""
        if lines.date:
            date_end = lines.date
            day_end = date_end[8:10]
            month_end = date_end[5:7]
            year_end = date_end[:4]
            date_end = day_end+"/"+month_end+"/"+year_end
        else:
            date_end = ""
        # sheet.merge_range('A9:B9', "Start Date             :", format5)
        sheet.merge_range('A9:B9', "Fecha de Inicio      :", format5)
        sheet.merge_range('C9:D9', date_start, format5)
        # sheet.merge_range('A10:B10', "End Date               :", format5)
        sheet.merge_range('A10:B10', "Fecha de Fin         :", format5)
        sheet.merge_range('C10:D10', date_end, format5)
        # row_number = 10
        # desplazamos el row number para hacer sitio al porcentaje de ejecucion del proyecto
        row_number = 16

        # para el porcentaje de ejecucion empieza aqui
        # ponemos la cadena para el formato de 0.00, otros ver web de http://xlsxwriter.readthedocs.io/
        formatH = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF', 'num_format': '0.00'})
        # ponemos la cadena para el formato de 0.00%, otros ver web de http://xlsxwriter.readthedocs.io/
        formatP = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF', 'num_format': '0.00%'})

        if lines.planned_hours:
            planned_hours = lines.planned_hours
        else:
            planned_hours = 0
        if lines.effective_hours:
            effective_hours = lines.effective_hours
        else:
            effective_hours = 0
        if planned_hours != 0 and effective_hours != 0:
            ejec_project = effective_hours / planned_hours
        else:
            ejec_project = 0
        sheet.merge_range(10, 0, 11, 7, "Porcentaje de Ejecucion  :", format1)
        sheet.merge_range(10, 6, 11, 7, "", format1)
        sheet.merge_range('A13:B13', "Horas Planificadas :", format5)
        sheet.merge_range('C13:D13', planned_hours, formatH)
        sheet.merge_range('A14:B14', "Horas Ejecutadas   :", format5)
        sheet.merge_range('C14:D14', effective_hours, formatH)
        sheet.merge_range('A15:B15', "Porc. Ejecucion  :", format5)
        sheet.merge_range('C15:D15', ejec_project, formatP)
        # hasta aqui el porcentaje de ejecucion

        sheet.merge_range(0, 2, 4, 5, "", format5)
        sheet.merge_range(1, 6, 4, 7, "", format5)
        sheet.merge_range(7, 4, 9, 7, "", format5)


        if data['form']['task_select'] == True :
            # variable para saber la seleccion de current_task
            cur_task = 0

            task_obj = self.env['project.task']
            if len(data['form']['partner_select']) == 0:
                cur_task = 1
                if len(data['form']['stage_select']) == 0:
                    current_task_obj = task_obj.search([('project_id', '=', lines.id)])                      
                else:
                    current_task_obj = task_obj.search(
                        [('project_id', '=', lines.id), ('stage_id', 'in', data['form']['stage_select'])])
            else:
                cur_task = 2
                if len(data['form']['stage_select']) == 0:
                    current_task_obj = task_obj.search(
                        [('project_id', '=', lines.id), ('user_id', 'in', data['form']['partner_select'])])                            
                else:
                    current_task_obj = task_obj.search(
                        [('project_id', '=', lines.id), ('user_id', 'in', data['form']['partner_select']),
                         ('stage_id', 'in', data['form']['stage_select'])])

            # en una variable contamos el numero de coincidencias
            total_task = len (current_task_obj)
            # _logger.error('##### AIKO ###### Valor de total_task en project_report: %s' % total_task)

            #agregamos info de los filtros que pueden estar aplicados
            if cur_task == 2:
                user_filter = self.env['res.users']
                sheet.merge_range(row_number, 0, row_number+1, 7, "Filtro para las tareas asignadas a los usuarios:", format1)
                row_number += 2
                for user in data['form']['partner_select']:
                    # _logger.error('##### AIKO ###### Valor de user en project_report: %s' % user)
                    user_search = user_filter.search([('id','=',user)])
                    if len(user_search)==0:
                        raise osv.except_osv(('Error!'),('No se han encontrado usuarios'))
                    sheet.merge_range(row_number, 0, row_number, 3, user_search.partner_id.name, format3)
                    row_number += 1
                row_number += 1

            task_type = self.env['project.task.type']

            if len(data['form']['stage_select']) != 0:
                sheet.merge_range(row_number, 0, row_number+1, 7, "Filtro para las tareas en las etapas:", format1)
                row_number += 2
                for stage in data['form']['stage_select']:
                    # _logger.error('##### AIKO ###### Valor de stage en project_report: %s' % stage)
                    task_select = task_type.search([('id','=',stage)])
                    if len(task_select)==0:
                        raise osv.except_osv(('Error!'),('No se han encontrado etapas'))
                    sheet.merge_range(row_number, 0, row_number, 3, task_select.name, format3)
                    row_number += 1
                row_number += 1

            task_type_all = task_type.search([])
            # AGREGAMOS UN CUADRO RESUMEN DE LOS ESTADOS DE LA TAREAS
            sheet.merge_range(row_number, 4, row_number+1, 7, "", format5)
            sheet.merge_range(row_number, 0, row_number+1, 7, "Tareas Resumidas por Etapa", format1)
            row_number += 2
            sheet.merge_range(row_number, 0, row_number, 3, "Etapa", format2)
            sheet.merge_range(row_number, 4, row_number, 5, "Num. Tareas", format2)
            sheet.merge_range(row_number, 6, row_number, 7, "Porc. del Total", format2)
            # _logger.error('##### AIKO ###### Valor de len (task_type) en project_report: %s' % len (task_type_all))
            # _logger.error('##### AIKO ###### Valor de cur_task en project_report: %s' % cur_task)
            for types in task_type_all:
                if cur_task == 1:
                    # _logger.error('##### AIKO ###### Buscamos en project_report para un project_id: %s' % lines.id)
                    # _logger.error('##### AIKO ###### Buscamos en project_report para un satge_id: %s' % types.id)
                    task_type_project = task_obj.search([('project_id', '=', lines.id),('stage_id','=',types.id)])
                if cur_task == 2:
                    task_type_project = task_obj.search(
                            [('project_id', '=', lines.id), ('user_id', 'in', data['form']['partner_select']),
                            ('stage_id','=',types.id)])
                #_logger.error('##### AIKO ###### Valor de len (task_type_project) en project_report: %s' % len (task_type_project))

                if len (task_type_project)!=0:
                    if len(data['form']['stage_select']) != 0 and (types.id in data['form']['stage_select']) or len(data['form']['stage_select']) == 0:
                        num_task = len (task_type_project)
                        # _logger.error('##### AIKO ###### Valor de num_task en project_report: %s' % num_task)
                        # _logger.error('##### AIKO ###### Valor de total_task en project_report: %s' % total_task)
                        per_task_type = num_task / float(total_task)
                        # _logger.error('##### AIKO ###### Valor de per_task_type en project_report: %s' % per_task_type)
                        row_number += 1
                        
                        sheet.merge_range(row_number, 0, row_number, 3, types.name, format3)
                        sheet.merge_range(row_number, 4, row_number, 5, num_task, format3)
                        #el % del total solo cuando no se seleccionan unas tareas concretas
                        if len(data['form']['stage_select']) == 0:
                            sheet.merge_range(row_number, 6, row_number, 7, per_task_type, formatP)
                        else:
                            sheet.merge_range(row_number, 6, row_number, 7, "N/A", format3)
                    
            row_number += 1

            # sheet.merge_range(10, 4, 11, 7, "", format5)
            sheet.merge_range(row_number, 4, row_number+1, 7, "", format5)
            # sheet.merge_range(row_number, 0, row_number+1, 3, "Open Tasks", format4)
            sheet.merge_range(row_number, 0, row_number+1, 7, "Tareas Abiertas", format1)
            row_number += 2
            
            # sheet.merge_range(row_number, 0, row_number, 3, "Tasks", format2)
            sheet.write(row_number, 0, "Tarea", format2)
            # sheet.merge_range(row_number, 4, row_number, 5, "Assigned", format2)
            # sheet.merge_range(row_number, 6, row_number, 7, "Stage", format2)
            # acrotamos las celdas una por valor
            # sheet.write(row_number, 4, "Assigned", format2)
            sheet.write(row_number, 1, "Asignada a", format2)
            # sheet.write(row_number, 5, "Stage", format2)
            sheet.write(row_number, 2, "Etapa", format2)
            # nuevos valores para el detalle de tareas
            sheet.write(row_number, 3, "Fecha Inicio", format2)
            sheet.write(row_number, 4, "Fecha Fin", format2)
            sheet.write(row_number, 5, "Horas Plan", format2)
            sheet.write(row_number, 6, "Horas Ejecutadas", format2)
            sheet.write(row_number, 7, "Porc. Progreso", format2)
            for records in current_task_obj:
                row_number += 1
                if records.user_id.name:
                    user_name = records.user_id.name
                else:
                    user_name = ""
                # nuevos valores para el detalle de tareas
                if records.date_start:
                    date_start_t = records.date_start
                    # tenemos que tratar la cadena de texto y cambiar el orden del valor
                    day_start_t = date_start_t[8:10]
                    month_start_t = date_start_t[5:7]
                    year_start_t = date_start_t[:4]
                    date_start_t = day_start_t+"/"+month_start_t+"/"+year_start_t
                else:
                    date_start_t = ""
                if records.date_end:
                    date_end_t = records.date_end
                    day_end_t = date_end_t[8:10]
                    month_end_t = date_end_t[5:7]
                    year_end_t = date_end_t[:4]
                    date_end_t = day_end_t+"/"+month_end_t+"/"+year_end_t
                else:
                    date_end_t = ""
                if records.planned_hours !=0 and records.effective_hours !=0:
                    progress_task = records.effective_hours / records.planned_hours
                else:
                    progress_task = 0

                sheet.merge_range(row_number, 0, row_number, 4, records.name, format3)
                row_number+=1
                sheet.write(row_number, 1, user_name, format3)
                sheet.write(row_number, 2, records.stage_id.name, format3)
                # nuevos valores para el detalle de tareas
                sheet.write(row_number, 3, date_start_t, format3)
                sheet.write(row_number, 4, date_end_t, format3)
                sheet.write(row_number, 5, records.planned_hours, formatH)
                sheet.write(row_number, 6, records.effective_hours, formatH)
                sheet.write(row_number, 7, progress_task, formatP)
            row_number += 1
#
#        sql = 'SELECT DISTINCT ttype.name,count(task.id) as num_tareas FROM project_task task \
#        JOIN project_task_type ttype ON task.stage_id = ttype.id
#        WHERE task.project_id = %s GROUP BY ttype.name' % (current_task_obj.id)
#        
#        self.env.cr.execute(sql)
#        for record in self.env.cr.fetchall():
#
        if data['form']['issue_select'] == True :

            row_number += 1
            sheet.merge_range(row_number-1, 0, row_number-1, 7, "", format4)
            sheet.merge_range(row_number, 4, row_number + 1, 7, "", format5)
            # sheet.merge_range(row_number, 0, row_number+1, 3, "Open Issues", format6)
            sheet.merge_range(row_number, 0, row_number+1, 7, "Incidencias", format1)
            row_number += 2
            task_obj = self.env['project.issue']


            if len(data['form']['partner_select']) == 0:
                if len(data['form']['stage_select']) == 0:
                    current_task_obj = task_obj.search([('project_id', '=', lines.id)])
                else:
                    current_task_obj = task_obj.search(
                        [('project_id', '=', lines.id), ('stage_id', 'in', data['form']['stage_select'])])
            else:
                if len(data['form']['stage_select']) == 0:
                    current_task_obj = task_obj.search(
                        [('project_id', '=', lines.id), ('user_id', 'in', data['form']['partner_select'])])
                else:
                    current_task_obj = task_obj.search(
                        [('project_id', '=', lines.id), ('user_id', 'in', data['form']['partner_select']),
                         ('stage_id', 'in', data['form']['stage_select'])])

            # sheet.merge_range(row_number, 0, row_number, 3, "Issues", format2)
            sheet.merge_range(row_number, 0, row_number, 3, "Incidencia", format2)
            # sheet.merge_range(row_number, 4, row_number, 5, "Assigned", format2)
            sheet.merge_range(row_number, 4, row_number, 5, "Asignada a", format2)
            # sheet.merge_range(row_number, 6, row_number, 7, "Stage", format2)
            sheet.merge_range(row_number, 6, row_number, 7, "Etapa", format2)
            for records in current_task_obj:
                row_number += 1
                if records.user_id.name:
                    user_name = records.user_id.name
                else:
                    user_name = ""
                sheet.merge_range(row_number, 0, row_number, 3, records.name, format3)
                sheet.merge_range(row_number, 4, row_number, 5, user_name, format3)
                sheet.merge_range(row_number, 6, row_number, 7, records.stage_id.name, format3)
        # row_number += 2
        # sheet.merge_range(row_number, 0, row_number, 1, lines.company_id.phone, format7)
        # sheet.merge_range(row_number, 2, row_number, 4, lines.company_id.email, format7)
        # sheet.merge_range(row_number, 5, row_number, 7, lines.company_id.website, format7)

LideritProjectReportXls('report.liderit_project_report_pdf.project_report_xls.xlsx', 'project.project')