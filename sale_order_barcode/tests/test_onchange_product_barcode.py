# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError


class TestOnchangeProductBarcode(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestOnchangeProductBarcode, self).setUp(*args, **kwargs)
        # Objects
        self.wiz = self.env['sale.order.barcode']
        self.obj_sale_order_line =\
            self.env['sale.order.line']

        # Data
        self.data_so = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        self.product_1 =\
            self.env.ref('product.product_product_25')
        self.product_2 =\
            self.env.ref('product.product_product_30')
        self.product_3 =\
            self.env.ref('product.product_product_3')
        self.uom_unit =\
            self.env.ref('product.product_uom_unit')
        self.uom_dozen =\
            self.env.ref('product.product_uom_dozen')

    def test_error_product_no_ean_13(self):
        new = self.wiz.with_context(
            active_model="sale.order",
            active_id=self.data_so.id
        ).new()

        new.product_barcode = 0000000000000
        res = new.product_barcode_onchange()
        self.assertEquals(
            'No product found with this code as '
            'EAN13 or product is not for sale. You should select '
            'the right product manually.',
            res['warning']['message']
        )

    def test_error_product_duplicate_ean(self):
        new = self.wiz.with_context(
            active_model="sale.order",
            active_id=self.data_so.id
        ).new()

        self.product_1.ean13 = 8998989300155
        self.product_2.ean13 = 8998989300155

        new.product_barcode = 8998989300155
        res = new.product_barcode_onchange()
        self.assertIsNotNone(
            res['warning']['message']
        )

    def test_error_more_than_1_line(self):
        order_line = [
            (0, 0, {
                'product_id': self.product_1.id,
                'product_uom_qty': 5,
                }),
            (0, 0, {
                'product_id': self.product_1.id,
                'product_uom_qty': 1,
                }),
        ]

        self.data_so.update({
            'order_line': order_line
        })

        new = self.wiz.with_context(
            active_model="sale.order",
            active_id=self.data_so.id
        ).new()

        self.product_1.ean13 = 8998989300155

        new.product_barcode = 8998989300155
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 20.0

        msg = ("More than 1 line found")

        with self.assertRaises(UserError) as error:
            new.save()

        self.assertEqual(error.exception.message, msg)

    def test_product_barcode_condition_1(self):
        # CONDITION
        # 1. type = INSERT
        # 2. Uom Lines = Uom Wizard
        # 3. Using single product

        self.product_1.ean13 = 8998989300155

        new = self.wiz.with_context(
            active_model="sale.order",
            active_id=self.data_so.id
        ).new()

        new.type = 'insert'
        new.product_barcode = 8998989300155
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 5.0
        new.save()

        new.type = 'insert'
        new.product_barcode = 8998989300155
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 9.0
        new.save()

        line_1 = self.obj_sale_order_line.search([
            ('order_id', '=', self.data_so.id),
            ('product_id', '=', self.product_1.id)
        ])
        self.assertEqual(line_1.product_uom_qty, 14.0)

    def test_product_barcode_condition_2(self):
        # CONDITION
        # 1. type = INSERT
        # 2. Uom Lines != Uom Wizard
        # 3. Using single product

        self.product_2.ean13 = 8996001600382

        new = self.wiz.with_context(
            active_model="sale.order",
            active_id=self.data_so.id
        ).new()

        new.type = 'insert'
        new.product_barcode = 8996001600382
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 1.0
        new.save()

        new.type = 'insert'
        new.product_barcode = 8996001600382
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 2.0
        new.product_uom_id = self.uom_dozen.id
        new.save()

        line_1 = self.obj_sale_order_line.search([
            ('order_id', '=', self.data_so.id),
            ('product_id', '=', self.product_2.id)
        ])
        self.assertEqual(line_1.product_uom_qty, 25.0)

    def test_product_barcode_condition_3(self):
        # CONDITION
        # 1. type = UPDATE
        # 2. Uom Lines = Uom Wizard
        # 3. Using single product

        self.product_1.ean13 = 8998989300155

        new = self.wiz.with_context(
            active_model="sale.order",
            active_id=self.data_so.id
        ).new()

        new.type = 'insert'
        new.product_barcode = 8998989300155
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 1.0
        new.save()

        new.type = 'update'
        new.product_barcode = 8998989300155
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 2.0
        new.save()

        line_1 = self.obj_sale_order_line.search([
            ('order_id', '=', self.data_so.id),
            ('product_id', '=', self.product_1.id)
        ])
        self.assertEqual(line_1.product_uom_qty, 2.0)

    def test_product_barcode_condition_4(self):
        # CONDITION
        # 1. type = UPDATE
        # 2. Uom Lines != Uom Wizard
        # 3. Using single product

        self.product_3.ean13 = 8998666000903

        new = self.wiz.with_context(
            active_model="sale.order",
            active_id=self.data_so.id
        ).new()

        new.type = 'insert'
        new.product_barcode = 8998666000903
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 4.0
        new.save()

        new.type = 'update'
        new.product_barcode = 8998666000903
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 1.0
        new.product_uom_id = self.uom_dozen.id
        new.save()

        line_1 = self.obj_sale_order_line.search([
            ('order_id', '=', self.data_so.id),
            ('product_id', '=', self.product_3.id)
        ])
        self.assertEqual(line_1.product_uom_qty, 12.0)

    def test_product_barcode_condition_5(self):
        # CONDITION
        # 1. type = UPDATE & INSERT
        # 2. Uom Lines != Uom Wizard & Uom Lines = Uom Wizard
        # 3. Using multiple product

        self.product_1.ean13 = 8998989300155
        self.product_2.ean13 = 8996001600382
        self.product_3.ean13 = 8998666000903

        new = self.wiz.with_context(
            active_model="sale.order",
            active_id=self.data_so.id
        ).new()

        new.type = 'insert'
        new.product_barcode = 8998989300155
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 3.0
        new.save()

        new.type = 'insert'
        new.product_barcode = 8996001600382
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 10.0
        new.save()

        new.type = 'insert'
        new.product_barcode = 8998666000903
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 8.0
        new.save()

        new.type = 'update'
        new.product_barcode = 8998989300155
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 13.0
        new.save()

        new.type = 'insert'
        new.product_barcode = 8996001600382
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 10.0
        new.save()

        new.type = 'update'
        new.product_barcode = 8998666000903
        new.product_barcode_onchange()
        new.product_id_onchange()
        new.product_qty = 10.0
        new.product_uom_id = self.uom_dozen.id
        new.save()

        line_1 = self.obj_sale_order_line.search([
            ('order_id', '=', self.data_so.id),
            ('product_id', '=', self.product_1.id)
        ])
        self.assertEqual(line_1.product_uom_qty, 13.0)

        line_2 = self.obj_sale_order_line.search([
            ('order_id', '=', self.data_so.id),
            ('product_id', '=', self.product_2.id)
        ])
        self.assertEqual(line_2.product_uom_qty, 20.0)

        line_3 = self.obj_sale_order_line.search([
            ('order_id', '=', self.data_so.id),
            ('product_id', '=', self.product_3.id)
        ])
        self.assertEqual(line_3.product_uom_qty, 120.0)
