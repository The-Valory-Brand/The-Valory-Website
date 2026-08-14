from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User, EmailOTP

class RBACAndAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Main Admin
        self.admin = User.objects.create_superuser(
            email='admin@thevalory.com',
            password='AdminPassword123!'
        )

        # Create Operational Manager
        self.manager = User.objects.create_user(
            email='manager@thevalory.com',
            password='ManagerPassword123!',
            role=User.Role.MANAGER
        )

        # Create Customer
        self.customer = User.objects.create_user(
            email='customer@thevalory.com',
            password='CustomerPassword123!',
            role=User.Role.CUSTOMER
        )

    def test_main_admin_access_to_reports(self):
        self.client.login(email='admin@thevalory.com', password='AdminPassword123!')
        response = self.client.get(reverse('reports:admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_manager_blocked_from_admin_reports(self):
        """CRITICAL REQUIREMENT: Operational Manager MUST receive 403 Forbidden when accessing reports."""
        self.client.login(email='manager@thevalory.com', password='ManagerPassword123!')
        response = self.client.get(reverse('reports:admin_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_customer_blocked_from_admin_reports(self):
        self.client.login(email='customer@thevalory.com', password='CustomerPassword123!')
        response = self.client.get(reverse('reports:admin_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_otp_generation_and_verification(self):
        plain_code = EmailOTP.generate_otp_code()
        hashed = EmailOTP.hash_otp(plain_code)
        
        from django.utils import timezone
        from datetime import timedelta
        
        otp = EmailOTP.objects.create(
            email='customer@thevalory.com',
            otp_hash=hashed,
            purpose=EmailOTP.Purpose.LOGIN,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        self.assertTrue(otp.verify_code(plain_code))
        self.assertFalse(otp.verify_code(plain_code))  # Used OTP must fail on retry
