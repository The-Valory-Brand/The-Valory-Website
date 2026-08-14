from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.products.models import Category, Product, ProductSize, Size
from decimal import Decimal

class ProductManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            email='admin@thevalory.com',
            password='AdminPassword123!'
        )
        self.manager = User.objects.create_user(
            email='manager@thevalory.com',
            password='ManagerPassword123!',
            role=User.Role.MANAGER
        )
        self.category = Category.objects.create(name='Heavyweight Tees', slug='heavyweight-tees')
        self.product = Product.objects.create(
            sku='TEST-001',
            product_id='PRD-999',
            name='Test Product',
            category=self.category,
            price=Decimal('1999.00')
        )
        ProductSize.objects.create(product=self.product, size=Size.M, stock_quantity=10)

    def test_manager_edit_product_get(self):
        self.client.login(email='manager@thevalory.com', password='ManagerPassword123!')
        response = self.client.get(reverse('products:manager_product_edit', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('existing_sizes', response.context)
        self.assertEqual(response.context['existing_sizes'].get(Size.M), 10)

    def test_admin_edit_product_get(self):
        self.client.login(email='admin@thevalory.com', password='AdminPassword123!')
        response = self.client.get(reverse('products:manager_product_edit', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 200)
