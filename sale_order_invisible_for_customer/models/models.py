
from openerp import models, fields, api
class sale_order_invisible(models.Model):
    
    _inherit = 'sale.order' 
    invisible_totals= fields.Boolean('Invisibilize totals', default=False, 
        help ='Allows to hide the totals to place the order in front of the customer without the customer seeing it.')
    
    
    
    
    