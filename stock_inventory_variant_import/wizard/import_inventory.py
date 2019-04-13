# -*- coding: utf-8 -*-
# (c) 2015 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models, exceptions, api, _
import base64
import csv
import cStringIO
import logging
_logger = logging.getLogger(__name__)


class ImportInventory(models.TransientModel):
    _name = 'import.inventory'
    _description = 'Import inventory'

    def _get_default_location(self):
        ctx = self.env.context
        if 'active_id' in ctx:
            inventory_obj = self.env['stock.inventory']
            inventory = inventory_obj.browse(ctx['active_id'])
            return inventory.location_id or self.env['stock.location']
        return False

    data = fields.Binary('File', required=True)
    name = fields.Char('Filename')
    delimeter = fields.Char('Delimeter', default=',',
                            help='Default delimeter is ","')
    location = fields.Many2one('stock.location', 'Default Location',
                               default=_get_default_location, required=True)

    @api.multi
    def action_import(self):
        """Load Inventory data from the CSV file."""
        ctx = self.env.context
        stloc_obj = self.env['stock.location']
        inventory_obj = self.env['stock.inventory']
        inv_imporline_obj = self.env['stock.inventory.import.line']
        product_obj = self.env['product.product']
        attribute_obj = self.env['product.attribute.value']
        inventory = inventory_obj
        if 'active_id' in ctx:
            inventory = inventory_obj.browse(ctx['active_id'])
        # Decode the file data
        data = base64.b64decode(self.data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        location = self.location
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]
        # check if keys exist
        if not isinstance(keys, list) or ('code' not in keys or
                                          'quantity' not in keys):
            raise exceptions.Warning(
                _("Not 'code' or 'quantity' keys found"))
        del reader_info[0]
        values = {}
        inv_name = u'{} - {}'.format(self.name, fields.Date.today())
        inventory.write({'name': inv_name,
                         'date': fields.Datetime.now(),
                         'imported': True,
                         'state': 'confirm',
                         })
        for i in range(len(reader_info)):
            val = {}
            field = reader_info[i]
            values = dict(zip(keys, field))
            prod_location = location.id
            if 'location' in values and values['location']:
                locations = stloc_obj.search([('name', '=',
                                               values['location'])])
                if locations:
                    prod_location = locations[:1].id
            variant_values=[]
            if 'attribute_talla' in values and values['attribute_talla']:
                _logger.error('########### Valor de attribute_talla: %s', values['attribute_talla'])
                variant_lst = attribute_obj.search([('name', '=',
                                            values['attribute_talla'])])
                if variant_lst:
                    variant_values.append(variant_lst[0].id)
            if 'attribute_color' in values and values['attribute_color']:
                _logger.error('########### Valor de attribute_color: %s', values['attribute_color'])
                variant_lst = attribute_obj.search([('name', '=',
                                            values['attribute_color'])])
                if variant_lst:
                    variant_values.append(variant_lst[0].id)
            if len (variant_values)>0:
                _logger.error('########### Valor de variant_values: %s', variant_values)
                if len (variant_values)==2:
                    prod_lst = product_obj.search([
                        ('default_code', '=',values['code']),
                        ('attribute_value_ids','in',variant_values[0]),
                        ('attribute_value_ids','in',variant_values[1])
                        ])
                else:
                    prod_lst = product_obj.search([
                        ('default_code', '=',values['code']),
                        ('attribute_value_ids','in',variant_values[0])
                        ])
            else:
                prod_lst = product_obj.search([('default_code', '=',
                                            values['code'])])
            if prod_lst:
                _logger.error('########### Valor de prod_lst para attribute: %s', prod_lst[0].attribute_value_ids)
                val['product'] = prod_lst[0].id
            else:
                continue
            if 'lot' in values and values['lot']:
                val['lot'] = values['lot']
            val['code'] = values['code']
            val['attribute_talla'] = values['attribute_talla']
            val['attribute_color'] = values['attribute_color']
            val['quantity'] = values['quantity']
            val['location_id'] = prod_location
            val['inventory_id'] = inventory.id
            val['fail'] = True
            val['fail_reason'] = _('No processed')
            if 'standard_price' in values and values['standard_price']:
                val['standard_price'] = values['standard_price']
            inv_imporline_obj.create(val)


class StockInventoryImportLine(models.Model):
    _name = "stock.inventory.import.line"
    _description = "Stock Inventory Import Line"

    code = fields.Char('Product Code')
    attribute_talla = fields.Char('Attribute Talla')
    attribute_color = fields.Char('Attribute Color')
    product = fields.Many2one('product.product', 'Found Product')
    quantity = fields.Float('Quantity')
    inventory_id = fields.Many2one('stock.inventory', 'Inventory',
                                   readonly=True)
    location_id = fields.Many2one('stock.location', 'Location')
    lot = fields.Char('Product Lot')
    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    standard_price = fields.Float(string='Cost Price')
