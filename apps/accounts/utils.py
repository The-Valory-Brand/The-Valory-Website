from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
import logging

from apps.accounts.models import EmailOTP, User

logger = logging.getLogger(__name__)

def generate_and_send_otp(email, purpose=EmailOTP.Purpose.LOGIN):
    """
    Generates a cryptographically secure 6-digit OTP, invalidates existing un-used OTPs for this email/purpose,
    saves the hashed version in the database, and sends the plain code via email.
    """
    # Invalidate previous un-used OTPs for this email and purpose
    EmailOTP.objects.filter(email=email, purpose=purpose, is_used=False).update(is_used=True)

    plain_code = EmailOTP.generate_otp_code()
    hashed_code = EmailOTP.hash_otp(plain_code)
    
    expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

    otp_record = EmailOTP.objects.create(
        email=email,
        otp_hash=hashed_code,
        purpose=purpose,
        expires_at=expires_at
    )

    # Render HTML Email template
    subject = f"THE VALORY - Your OTP Verification Code ({plain_code})"
    html_message = render_to_string('emails/otp_email.html', {
        'otp_code': plain_code,
        'purpose': otp_record.get_purpose_display(),
        'expiry_minutes': expiry_minutes,
    })
    plain_message = f"Your THE VALORY verification code is {plain_code}. It will expire in {expiry_minutes} minutes."

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")

    return otp_record, plain_code
