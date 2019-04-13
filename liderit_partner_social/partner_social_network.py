# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _



class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'facebook_url': fields.char('Facebook'),
        'twitter_url': fields.char('Twitter'),
        'linkedin_url': fields.char('LinkedIn'),
        'youtube_url': fields.char('Youtube'),
        'instagram_url': fields.char('Instagram'),
        'googleplus_url': fields.char('Google+'),
    }

    _defaults = {
    }





