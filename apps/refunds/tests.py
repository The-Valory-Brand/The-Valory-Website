from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.accounts.models import User
from apps.products.models import Product, Category
from apps.orders.models import Order
from apps.refunds.models import RefundClaim

class RefundPolicyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            email='refundtest@thevalory.com',
            password='Password123!',
            role=User.Role.CUSTOMER
        )
        self.category = Category.objects.create(name='Jackets', slug='jackets')
        self.product = Product.objects.create(
            sku='JKT-001',
            product_id='PRD-777',
            name='Luxe Bomber Jacket',
            category=self.category,
            price=Decimal('4999.00')
        )

    def test_refund_claim_blocked_for_non_delivered_orders(self):
        self.client.login(email='refundtest@thevalory.com', password='Password123!')
        order = Order.objects.create(
            order_id='VAL-20260813-REF1',
            customer=self.customer,
            status=Order.Status.PROCESSING,  # Not Delivered!
            subtotal=Decimal('4999.00'),
            total_amount=Decimal('4999.00'),
            shipping_full_name='Customer',
            shipping_phone='9876543210',
            shipping_address_line1='Street 1',
            city='Chennai',
            postal_code='600001'
        )
        response = self.client.get(reverse('refunds:submit_claim', kwargs={'order_id': order.order_id}))
        self.assertRedirects(response, reverse('orders:detail', kwargs={'order_id': order.order_id}))

    def test_refund_claim_blocked_after_24_hours(self):
        self.client.login(email='refundtest@thevalory.com', password='Password123!')
        order = Order.objects.create(
            order_id='VAL-20260813-REF2',
            customer=self.customer,
            status=Order.Status.DELIVERED,
            subtotal=Decimal('4999.00'),
            total_amount=Decimal('4999.00'),
            shipping_full_name='Customer',
            shipping_phone='9876543210',
            shipping_address_line1='Street 1',
            city='Chennai',
            postal_code='600001'
        )
        # Artificially age the delivery timestamp beyond 24 hours
        Order.objects.filter(id=order.id).update(updated_at=timezone.now() - timedelta(hours=25))
        
        response = self.client.get(reverse('refunds:submit_claim', kwargs={'order_id': order.order_id}))
        self.assertRedirects(response, reverse('orders:detail', kwargs={'order_id': order.order_id}))
