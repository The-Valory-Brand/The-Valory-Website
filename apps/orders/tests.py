from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from apps.accounts.models import User
from apps.products.models import Product, Category, ProductSize, Size
from apps.orders.models import Order, OrderItem

class OrderLifecycleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            email='shopper@thevalory.com',
            password='ShopperPassword123!',
            role=User.Role.CUSTOMER
        )
        self.category = Category.objects.create(name='Tees', slug='tees')
        self.product = Product.objects.create(
            sku='VAL-TEST-01',
            product_id='PRD-999',
            name='Test Luxe Tee',
            slug='test-luxe-tee',
            category=self.category,
            price=Decimal('1999.00')
        )
        self.product_size = ProductSize.objects.create(
            product=self.product,
            size=Size.L,
            stock_quantity=10
        )

    def test_pre_dispatch_cancellation_restores_stock(self):
        self.client.login(email='shopper@thevalory.com', password='ShopperPassword123!')

        # Create Order in PAYMENT_CONFIRMED status
        order = Order.objects.create(
            order_id='VAL-20260812-TEST1',
            customer=self.customer,
            status=Order.Status.PAYMENT_CONFIRMED,
            subtotal=Decimal('1999.00'),
            shipping_fee=Decimal('100.00'),
            total_amount=Decimal('2099.00'),
            shipping_full_name='Test Buyer',
            shipping_phone='9876543210',
            shipping_address_line1='Anna Salai',
            city='Chennai',
            state='Tamil Nadu',
            postal_code='600002'
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            sku=self.product.sku,
            size=Size.L,
            quantity=2,
            price_at_purchase=Decimal('1999.00'),
            total_price=Decimal('3998.00')
        )

        # Deduct stock initially
        self.product_size.stock_quantity -= 2
        self.product_size.save()
        self.assertEqual(self.product_size.stock_quantity, 8)

        # Cancel Order
        response = self.client.post(reverse('orders:cancel', kwargs={'order_id': order.order_id}))
        order.refresh_from_db()
        self.product_size.refresh_from_db()

        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.product_size.stock_quantity, 10)  # Stock restored!

    def test_cancellation_blocked_after_dispatch(self):
        """CRITICAL REQUIREMENT: Post-dispatch cancellation MUST be blocked!"""
        self.client.login(email='shopper@thevalory.com', password='ShopperPassword123!')

        order = Order.objects.create(
            order_id='VAL-20260812-TEST2',
            customer=self.customer,
            status=Order.Status.DISPATCHED,  # Already dispatched!
            subtotal=Decimal('1999.00'),
            shipping_fee=Decimal('0.00'),
            total_amount=Decimal('1999.00'),
            shipping_full_name='Test Buyer',
            shipping_phone='9876543210',
            shipping_address_line1='Anna Salai',
            city='Chennai',
            state='Tamil Nadu',
            postal_code='600002'
        )

        response = self.client.post(reverse('orders:cancel', kwargs={'order_id': order.order_id}))
        order.refresh_from_db()

        self.assertNotEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(order.status, Order.Status.DISPATCHED)
