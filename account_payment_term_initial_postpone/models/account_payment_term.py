##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _, tools
import calendar
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    initial_postpone = fields.Float(string='Days postpone from first due date')

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        """This method can't be new API due to arguments names are not
        standard for the API wrapper.
        """
        result = super(AccountPaymentTerm, self).compute(
            cr, uid, id, value=value, date_ref=date_ref, context=context)
        pay_term = self.browse(cr, uid, id, context=context)
        if not result:
            return result
        # _logger.error('######## AIKO compute payment_term valor de result %s ####### ->'%result)
        if pay_term.initial_postpone > 0:
            i=0
            for r in result:
                # _logger.error('######## AIKO compute payment_term valor de entrada %s ####### ->'%r[0])
                date = fields.Date.from_string(r[0])
                # _logger.error('######## AIKO compute payment_term valor de date %s ####### ->'%date)
                new_date= date + relativedelta(days=+pay_term.initial_postpone)
                # _logger.error('######## AIKO compute payment_term valor de new_date %s ####### ->'%new_date)
                result[i] = (fields.Date.to_string(new_date),r[1])
                i+=1
        
        return result
