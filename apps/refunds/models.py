from django.db import models
from django.conf import settings
from apps.orders.models import Order
import secrets

class RefundClaim(models.Model):
    class Status(models.TextChoices):
        NOT_REQUESTED = 'NOT_REQUESTED', 'Not Requested'
        CLAIM_SUBMITTED = 'CLAIM_SUBMITTED', 'Claim Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        REFUND_PROCESSED = 'REFUND_PROCESSED', 'Refund Processed'

    claim_id = models.CharField('Claim ID', max_length=50, unique=True, db_index=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund_claim')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='refund_claims')
    
    damage_description = models.TextField(help_text="Detailed description of product damage.")
    unboxing_video_url = models.URLField(max_length=500, blank=True, help_text="Link to unboxing video (Google Drive, Dropbox, YouTube, etc.)")
    unboxing_video_file = models.FileField(upload_to='refunds/videos/', blank=True, null=True)
    photo_evidence_1 = models.ImageField(upload_to='refunds/photos/')
    photo_evidence_2 = models.ImageField(upload_to='refunds/photos/', blank=True, null=True)
    
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.CLAIM_SUBMITTED, db_index=True)
    admin_notes = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    @classmethod
    def generate_claim_id(cls):
        return f"CLM-{secrets.token_hex(4).upper()}"

    def __str__(self):
        return f"Claim #{self.claim_id} for Order #{self.order.order_id} ({self.get_status_display()})"
