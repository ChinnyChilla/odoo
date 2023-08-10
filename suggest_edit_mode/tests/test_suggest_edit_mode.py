import logging
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

@tagged( '-at_install', 'post_install', '-standard', 'suggest_mode')
class TestSuggestEditMode(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestSuggestEditMode, cls).setUpClass()
        cls.user = cls.env.ref('base.user_demo')
        super_product = cls.env['product.product'].create({
            'name': 'Super Product',
            'invoice_policy': 'delivery',
        })
        great_product = cls.env['product.product'].create({
            'name': 'Great Product',
            'invoice_policy': 'delivery',
        })
        test_partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })
        cls.test_record = cls.env['sale.order'].create({
            'name': 'Test Sale Order',
            'partner_id': test_partner.id,
            'order_line': [
                (0, 0, {'name': super_product.name, 'product_id': super_product.id, 'product_uom_qty': 1, 'price_unit': 1,}),
                (0, 0, {'name': great_product.name, 'product_id': great_product.id, 'product_uom_qty': 1, 'price_unit': 1,}),
            ]
        })
    
    def test_add_suggestion(self):
        """Test that a suggestion can be added to a record"""
        rec = self.test_record.with_user(self.user)
        self.user.suggest_mode_switch = True

        
		
        testObject = {'payment_term_id': 3, 'note': '<p>I am testing</p>'}
        rec.write(testObject)

        self.assertEqual(self.test_record.suggestion_ids[0].suggested_value, testObject)