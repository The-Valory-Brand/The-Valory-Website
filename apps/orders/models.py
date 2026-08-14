from django.db import models
from django.conf import settings
from decimal import Decimal
import secrets
import datetime

class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = 'PLACED', 'Order Placed'
        PAYMENT_CONFIRMED = 'PAYMENT_CONFIRMED', 'Payment Confirmed'
        PROCESSING = 'PROCESSING', 'Processing Order'
        PACKED = 'PACKED', 'Packed & Ready'
        DISPATCHED = 'DISPATCHED', 'Dispatched / In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    order_id = models.CharField('Order ID', max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PLACED, db_index=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Shipping Address Details (Tamil Nadu)
    shipping_full_name = models.CharField(max_length=255)
    shipping_phone = models.CharField(max_length=20)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, default='Chennai')
    state = models.CharField(max_length=100, default='Tamil Nadu')
    postal_code = models.CharField(max_length=20)

    # Tracking & Dispatch Information
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)

    # Cancellation Information
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    # Legal & Policy Compliance
    policy_version = models.CharField(max_length=20, default='1.0')
    policy_accepted_at = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def generate_order_id(cls):
        date_str = datetime.date.today().strftime('%Y%m%d')
        random_num = secrets.randbelow(90000) + 10000
        return f"VAL-{date_str}-{random_num}"

    def __str__(self):
        return f"Order #{self.order_id} - {self.customer.email} ({self.get_status_display()})"

    @property
    def can_cancel(self):
        """
        Customer can cancel ONLY before dispatch (PLACED, PAYMENT_CONFIRMED, PROCESSING, PACKED).
        Returns False if DISPATCHED or DELIVERED.
        """
        return self.status in [
            self.Status.PLACED,
            self.Status.PAYMENT_CONFIRMED,
            self.Status.PROCESSING,
            self.Status.PACKED
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50)
    size = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Size {self.size}) in Order #{self.order.order_id}"
