from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.orders.models import Order

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    rating = models.PositiveIntegerField(default=5, choices=[(i, f"{i} Stars") for i in range(1, 6)])
    title = models.CharField(max_length=255)
    comment = models.TextField()
    is_verified_purchaser = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'customer')

    def __str__(self):
        return f"Review ({self.rating}★) by {self.customer.email} on {self.product.name}"
