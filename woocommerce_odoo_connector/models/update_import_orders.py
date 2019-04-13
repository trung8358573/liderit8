#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp import api,fields,models
from woocommerce import API
from openerp.tools.translate import _
from datetime import datetime,timedelta
from openerp.addons.odoo_multi_channel_sale.tools import extract_list as EL
from openerp.osv import osv
import logging
_logger	 = logging.getLogger(__name__)

class MultiChannelSale(models.Model):
	_inherit = "multi.channel.sale"

	@api.multi
	def update_woocommerce_orders(self, woocommerce=False):
		update_rec = []
		count = 0
		if not woocommerce:
			woocommerce = self.get_woocommerce_connection()
		order_feed_data = self.env['order.feed']
		date = self.with_context({'name':'order'}).get_woocommerce_update_date()
		try:
			order_data = woocommerce.get('orders?filter[limit]=-1&filter[updated_at_min]='+date).json()
		except Exception as e:
			raise osv.except_osv(_('Error'),_("Error : "+str(e)))
		if order_data.has_key('errors'):
			raise osv.except_osv(_('Error'),_("Error : "+str(order_data['errors'][0]['message'])))
		else :
			for order in order_data['orders']:
				update_record = self.env['order.feed'].search([('store_id','=',order['id'])])
				if update_record and update_record.order_state != order['status']:
					count += 1
					update_record.state = 'update'
					order_dict = {
								'order_state': order['status']
					}
					update_record.write(order_dict)
					update_rec.append(update_record)
			feed_res = dict(create_ids=[],update_ids=update_rec)
			self.env['channel.operation'].post_feed_import_process(self,feed_res)
			self.woocommerce_update_order_date = str(datetime.now().date())
			message = str(count)+" Order(s) Updated! , "
			return message
