# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.osv import fields, osv
from datetime import datetime, date, time, timedelta
import logging
_logger = logging.getLogger(__name__)


class mrp_repair(osv.osv):

  _inherit = ['mrp.repair']

  # (MON, TUE, WED, THU, FRI, SAT, SUN) = range(7)
  # def addworkdays(self, cr, uid, ids, d_start, days, holidays=(), workdays=(MON,TUE,WED,THU,FRI)):
  def addworkdays(self, cr, uid, ids, d_start, d_end, context=None):
    # workdays=('MON','TUE','WED','THU','FRI')
    workdays=(0,1,2,3,4)
    # weeks, days = divmod(days, len(workdays))
    # res = d_start + timedelta(weeks=weeks)
    # lo, hi = min(d_start, res), max(d_start, res)
    # count = len([h for h in holidays if h >= lo and h <= hi])
    # days += count * (-1 if days < 0 else 1)
    # for _ in range(days):
    #     res += timedelta(days=1)
    #     while res in holidays or res.weekday() not in workdays:
    res = d_start
    count = 0
    while res <= d_end:
      if res.weekday() in workdays:
        count += 1
      res += timedelta(seconds=24*60*60)
    return count
    

  def numholidays(self, cr, uid, ids, d_start, d_end, context=None):
    workdays=(0,1,2,3,4)
    holidays = self.pool.get('res.holiday')
    res = d_start
    count = 0
    while res <= d_end:
      search_condition = [('name', '=', res.date())]
      es_festivo = holidays.search(cr, uid, search_condition)
      if len (es_festivo)>0:
        if res.weekday() in workdays:
          count +=1
      res += timedelta(seconds=24*60*60)
    
    return count

  def calculate_date(self, cr, uid, ids, field_name, arg, context=None):
    records = self.browse(cr, uid, ids, context=context)
   
    res = {}
    fmt = '%Y-%m-%d'
    for r in records:
      dias_festivos = 0
      if r.repair_ready_date and r.fecha_reparacion:
        d_end = datetime.strptime(r.fecha_reparacion, fmt)
        # _logger.error('##### AIKO ###### Valor de id reg en calculate_date: %s' % r.id)
        # _logger.error('##### AIKO ###### Valor de d_end en calculate_date: %s' % d_end)
        d_start = datetime.strptime(r.repair_ready_date, fmt)
        # _logger.error('##### AIKO ###### Valor de d_start en calculate_date: %s' % d_start)
        
        # res[r.id] = (d_end - d_start).days
        num_dia = (d_end - d_start).days
        # dias_lab = self.suma_dias_habiles(cr, uid, ids, d_start,num_dia, context=context)
        dias_lab = self.addworkdays(cr, uid, ids, d_start,d_end, context=context)
        # _logger.error('##### AIKO ###### Valor de dias_lab en calculate_date: %s' % dias_lab)

        dias_festivos = self.numholidays(cr, uid, ids, d_start,d_end, context=context)

        res[r.id] = float(dias_lab-dias_festivos)        
         
    #   # print "RESULTADO", res
    # _logger.error('##### AIKO ###### Valor de res: %s' % res)
    return res
   
      
  _columns = {
    'num_dias_laborales' : fields.function (calculate_date, type = 'float', string = 'Numero dias laborales', store=True),
    'fecha_recepcion': fields.date ('Fecha de Recepción'),
    'repair_ready_date': fields.date('Inicio Reparación'),
    'fecha_reparacion': fields.date ('Fecha de Reparación'),
  }
      