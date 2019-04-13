# -*- coding: utf-8 -*-
##############################################################################
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_holidays_validity_date.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    active_employee = fields.Boolean(string='Active Employee',related='employee_id.active')
