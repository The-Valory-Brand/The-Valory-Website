from django.db import models
from apps.orders.models import Order

class Payment(models.Model):
    class Method(models.TextChoices):
        COD = 'COD', 'Cash on Delivery (Tamil Nadu)'
        UPI = 'UPI', 'UPI / QR Payment'
        CARD = 'CARD', 'Credit / Debit Card'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=Method.choices, default=Method.UPI)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment #{self.transaction_id} for Order #{self.order.order_id} ({self.get_status_display()})"
