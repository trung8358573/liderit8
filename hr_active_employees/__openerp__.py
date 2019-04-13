# -*- coding: utf-8 -*-
##############################################################################
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_holidays_validity_date.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "HR holidays active employees",

    'summary': """
        Show holidays only from active employees.""",
    'author': 'LiderIT',
    'website': "http://liderit.es",
    'category': 'Human resources',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_view.xml',
    ],
}
