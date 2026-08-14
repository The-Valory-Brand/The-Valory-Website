from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import hashlib
import secrets
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('role', User.Role.CUSTOMER)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.MAIN_ADMIN)
        extra_fields.setdefault('is_email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        MAIN_ADMIN = 'MAIN_ADMIN', 'Main Admin'
        MANAGER = 'MANAGER', 'Operational Manager'
        CUSTOMER = 'CUSTOMER', 'Customer'

    username = None  # Use email as unique identifier
    email = models.EmailField('Email Address', unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def is_main_admin(self):
        return self.role == self.Role.MAIN_ADMIN or self.is_superuser

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    shipping_address_line1 = models.CharField(max_length=255, blank=True)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, default='Chennai')
    state = models.CharField(max_length=100, default='Tamil Nadu')
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='India')

    def __str__(self):
        return f"Profile of {self.user.email}"


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField('Address Line 1', max_length=255)
    address_line2 = models.CharField('Address Line 2 (Optional)', max_length=255, blank=True)
    city = models.CharField(max_length=100, default='Chennai')
    district = models.CharField(max_length=100, default='Chennai')
    state = models.CharField(max_length=100, default='Tamil Nadu')
    pincode = models.CharField(max_length=20)
    landmark = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.state} ({self.pincode})"



class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_managers')
    department = models.CharField(max_length=100, default='Operations & Inventory')
    is_active_manager = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Manager: {self.user.email}"


class EmailOTP(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = 'LOGIN', 'Login Verification'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Password Reset'
        EMAIL_VERIFICATION = 'EMAIL_VERIFICATION', 'Email Verification'

    email = models.EmailField(db_index=True)
    otp_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=30, choices=Purpose.choices, default=Purpose.LOGIN)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    resend_count = models.IntegerField(default=0)
    max_resend = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def generate_otp_code(cls):
        """Generates a cryptographically secure 6-digit OTP code string."""
        return f"{secrets.randbelow(900000) + 100000}"

    @classmethod
    def hash_otp(cls, code: str) -> str:
        return hashlib.sha256(code.encode('utf-8')).hexdigest()

    def verify_code(self, input_code: str) -> bool:
        if self.is_used or timezone.now() > self.expires_at or self.attempts >= self.max_attempts:
            return False
        
        input_hash = self.hash_otp(input_code)
        if secrets.compare_digest(self.otp_hash, input_hash):
            self.is_used = True
            self.save(update_fields=['is_used'])
            return True
        else:
            self.attempts += 1
            self.save(update_fields=['attempts'])
            return False

    def is_expired(self):
        return timezone.now() > self.expires_at
