from django.db import models
from django.conf import settings

class Policy(models.Model):
    class PolicyType(models.TextChoices):
        SHIPPING = 'SHIPPING', 'Shipping Policy'
        REFUND = 'REFUND', 'Refund Policy'
        RETURN_EXCHANGE = 'RETURN_EXCHANGE', 'Return & Exchange Policy'
        ORDER = 'ORDER', 'Order Cancellation & Terms'
        GENERAL = 'GENERAL', 'General Terms & Conditions'
        TERMS = 'TERMS', 'Terms of Service'

    policy_type = models.CharField(max_length=30, choices=PolicyType.choices, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="HTML or Markdown policy text.")
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Policies'

    def __str__(self):
        return f"{self.get_policy_type_display()} (v{self.version})"


class PolicyAcceptance(models.Model):
    class AcceptanceType(models.TextChoices):
        SIGNUP = 'SIGNUP', 'Account Signup Agreement'
        CHECKOUT = 'CHECKOUT', 'Checkout Terms Agreement'
        REFUND_CLAIM = 'REFUND_CLAIM', 'Refund Claim Agreement'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='policy_acceptances')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True, related_name='policy_acceptances')
    policy_version = models.CharField(max_length=20, default='1.0')
    acceptance_type = models.CharField(max_length=30, choices=AcceptanceType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} agreed to {self.get_acceptance_type_display()} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
