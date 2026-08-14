from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.products.models import Product, ProductSize, Size

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        owner = self.user.email if self.user else f"Session {self.session_key}"
        return f"Cart ({owner})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def shipping_fee(self):
        # All over Tamil Nadu shipping standard flat rate or free above ₹2,999
        if self.subtotal >= Decimal('2999.00') or self.subtotal == Decimal('0.00'):
            return Decimal('0.00')
        return Decimal('100.00')

    @property
    def total_amount(self):
        return self.subtotal + self.shipping_fee


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, choices=Size.choices)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'size')

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Size {self.size})"

    @property
    def unit_price(self):
        return self.product.current_price

    @property
    def total_price(self):
        return self.unit_price * Decimal(self.quantity)

    @property
    def available_stock(self):
        ps = ProductSize.objects.filter(product=self.product, size=self.size).first()
        return ps.stock_quantity if ps else 0
