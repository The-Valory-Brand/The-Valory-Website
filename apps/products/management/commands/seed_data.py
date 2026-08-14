from django.core.management.base import BaseCommand
from apps.products.models import Category, Product, ProductSize, Size
from apps.policies.models import Policy
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds initial categories, products, sizes, and brand policies for THE VALORY.'

    def add_arguments(self, parser):
        parser.add_argument('--if-empty', action='store_true', help='Only seed if database is currently empty')

    def handle(self, *args, **options):
        if options['if_empty'] and Product.objects.exists():
            self.stdout.write(self.style.SUCCESS("Database already seeded. Skipping."))
            return

        self.stdout.write("Seeding THE VALORY default Admin and Manager accounts...")
        self.seed_users()

        self.stdout.write("Seeding THE VALORY brand policies...")
        self.seed_policies()

        self.stdout.write("Seeding categories & products...")
        self.seed_catalog()

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))

    def seed_policies(self):
        policies_data = [
            {
                'type': Policy.PolicyType.SHIPPING,
                'title': 'Tamil Nadu Shipping & Logistics Policy',
                'content': """
                <h3>THE VALORY Shipping & Logistics Policy</h3>
                <p><strong>Coverage:</strong> THE VALORY ships orders all over Tamil Nadu, India.</p>
                <p><strong>Processing:</strong> Orders are processed immediately following payment confirmation.</p>
                <p><strong>Tracking:</strong> Real-time tracking details and courier consignment numbers are dispatched via email and SMS once the package is handed over to our delivery partners.</p>
                <p><strong>Delivery Timelines:</strong> Typical delivery timeline across Chennai, Coimbatore, Madurai, Tiruchirappalli, Salem, and rest of Tamil Nadu is 2-4 business days.</p>
                <p><strong>Carrier Delays:</strong> Delays caused by severe weather, regional transport disruptions, or courier operational bottlenecks are beyond THE VALORY's direct control.</p>
                """
            },
            {
                'type': Policy.PolicyType.REFUND,
                'title': 'Strict Damaged Product Refund Policy',
                'content': """
                <h3>THE VALORY Refund Policy</h3>
                <p><strong>General Refunds:</strong> THE VALORY operates a strict NO GENERAL REFUNDS policy.</p>
                <p><strong>Damaged Product Eligibility:</strong> Refunds are applicable ONLY when a customer receives a damaged or defective item upon delivery.</p>
                <p><strong>Mandatory Claim Verification Rules:</strong></p>
                <ol>
                    <li>Customer <strong>MUST record an unboxing video</strong> starting from the sealed outer package up to inspecting the damaged item.</li>
                    <li>Customer <strong>MUST provide clear high-resolution photos</strong> of the damaged section.</li>
                    <li>The damage claim <strong>MUST be submitted within 24 hours of delivery</strong> via your account dashboard.</li>
                    <li>Claims submitted without unboxing video proof or exceeding 24 hours will be strictly rejected.</li>
                </ol>
                <p>Once verified and approved by THE VALORY quality control team, eligible refunds are credited to the original payment source within 5-7 business days.</p>
                """
            },
            {
                'type': Policy.PolicyType.RETURN_EXCHANGE,
                'title': 'No Return & No Exchange Policy',
                'content': """
                <h3>THE VALORY Return & Exchange Policy</h3>
                <p><strong>NO RETURNS & NO EXCHANGES:</strong> In accordance with our luxury brand standards, THE VALORY does NOT accept returns or exchanges for any purchased items.</p>
                <p><strong>Customer Size Selection:</strong> Customers are solely responsible for reviewing our garment size chart (S, M, L, XL, XXL) and selecting the correct size prior to order placement.</p>
                <p>Returns or exchanges will NOT be granted for:</p>
                <ul>
                    <li>Incorrect size selection by the buyer</li>
                    <li>Change of mind or personal preference</li>
                    <li>Minor color shade variations caused by screen displays and studio lighting</li>
                </ul>
                """
            },
            {
                'type': Policy.PolicyType.ORDER,
                'title': 'Order Terms & Cancellation Policy',
                'content': """
                <h3>THE VALORY Order & Pre-Dispatch Cancellation Policy</h3>
                <p><strong>Order Placement:</strong> By placing an order with THE VALORY, you confirm that all shipping details, size choices, and billing information are accurate.</p>
                <p><strong>Cancellation Window:</strong> Customers may cancel an order <strong>ONLY BEFORE DISPATCH</strong> (while status is Placed, Payment Confirmed, Processing, or Packed).</p>
                <p><strong>Post-Dispatch Lock:</strong> Once an order status is updated to <strong>DISPATCHED</strong>, cancellation is strictly blocked server-side and cannot be processed.</p>
                """
            },
            {
                'type': Policy.PolicyType.GENERAL,
                'title': 'General Terms & Brand Guidelines',
                'content': """
                <h3>THE VALORY General Terms & Conditions</h3>
                <p>Welcome to THE VALORY ("Timeless Elegance"). All products undergo rigorous quality inspection prior to dispatch across Tamil Nadu.</p>
                <p>THE VALORY reserves the right to update product offerings, pricing, and operational policies without prior individual notice.</p>
                """
            },
            {
                'type': Policy.PolicyType.TERMS,
                'title': 'Terms of Service',
                'content': """
                <h3>THE VALORY Terms of Service</h3>
                <p>By accessing or purchasing from THE VALORY website, you agree to comply with our Terms of Service, Privacy practices, and Brand Policies.</p>
                """
            }
        ]

        for p_data in policies_data:
            Policy.objects.update_or_create(
                policy_type=p_data['type'],
                defaults={
                    'title': p_data['title'],
                    'content': p_data['content'],
                    'version': '1.0',
                    'is_active': True
                }
            )

    def seed_catalog(self):
        cat_tees, _ = Category.objects.get_or_create(name='Heavyweight Tees', defaults={'description': 'Premium 240 GSM luxury cotton t-shirts.'})
        cat_hoodies, _ = Category.objects.get_or_create(name='Oversized Hoodies', defaults={'description': 'Ultra-soft fleece oversized street hoodies.'})
        cat_pants, _ = Category.objects.get_or_create(name='Athletic Track Pants', defaults={'description': 'Tailored athletic track pants built for comfort.'})
        cat_acc, _ = Category.objects.get_or_create(name='Caps & Accessories', defaults={'description': 'Luxury streetwear caps and daily essentials.'})

        products_data = [
            {
                'sku': 'VAL-TEE-001',
                'product_id': 'PRD-1001',
                'name': 'Noir Monogram Heavyweight Tee',
                'category': cat_tees,
                'description': 'Crafted from 240 GSM combed ring-spun cotton. Features subtle embroidered VALORY monogram on left chest.',
                'price': Decimal('1999.00'),
                'discount_price': Decimal('1699.00'),
                'is_featured': True,
                'is_new_arrival': True,
            },
            {
                'sku': 'VAL-TEE-002',
                'product_id': 'PRD-1002',
                'name': 'Cream Elegance Graphic Tee',
                'category': cat_tees,
                'description': 'Minimalist cream oversized tee with high-density puff print graphic on the back.',
                'price': Decimal('1899.00'),
                'discount_price': None,
                'is_featured': True,
                'is_new_arrival': True,
            },
            {
                'sku': 'VAL-HUD-001',
                'product_id': 'PRD-2001',
                'name': 'Timeless Luxe Oversized Hoodie',
                'category': cat_hoodies,
                'description': '400 GSM heavy fleece hoodie with double-lined hood and drop-shoulder silhouette.',
                'price': Decimal('3499.00'),
                'discount_price': Decimal('2999.00'),
                'is_featured': True,
                'is_new_arrival': True,
            },
            {
                'sku': 'VAL-PNT-001',
                'product_id': 'PRD-3001',
                'name': 'Noir Tailored Athletic Jogger',
                'category': cat_pants,
                'description': 'Sleek black technical athletic pants with custom metal zips and elastic waist.',
                'price': Decimal('2499.00'),
                'discount_price': Decimal('2199.00'),
                'is_featured': False,
                'is_new_arrival': True,
            },
            {
                'sku': 'VAL-CAP-001',
                'product_id': 'PRD-4001',
                'name': 'Valory Signature Snapback Cap',
                'category': cat_acc,
                'description': 'Structured 6-panel streetwear cap with 3D embroidery of THE VALORY logo.',
                'price': Decimal('999.00'),
                'discount_price': None,
                'is_featured': True,
                'is_new_arrival': False,
            }
        ]

        for p_info in products_data:
            prod, _ = Product.objects.get_or_create(
                sku=p_info['sku'],
                defaults=p_info
            )
            # Add Sizes (S, M, L, XL, XXL) with stock
            for size_val in [Size.S, Size.M, Size.L, Size.XL, Size.XXL]:
                ProductSize.objects.get_or_create(
                    product=prod,
                    size=size_val,
                    defaults={'stock_quantity': 15}
                )

    def seed_users(self):
        from apps.accounts.models import User, ManagerProfile
        admin, created = User.objects.get_or_create(
            email='thevalory.brand@gmail.com',
            defaults={
                'first_name': 'Valory',
                'last_name': 'Admin',
                'role': User.Role.MAIN_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_email_verified': True
            }
        )
        if created:
            admin.set_password('AdminPassword123!')
            admin.save()

        m1, m1_created = User.objects.get_or_create(
            email='manager1@thevalory.com',
            defaults={
                'first_name': 'Operational',
                'last_name': 'Manager 1',
                'role': User.Role.MANAGER,
                'is_staff': True,
                'is_email_verified': True
            }
        )
        if m1_created:
            m1.set_password('ManagerPassword123!')
            m1.save()
            ManagerProfile.objects.get_or_create(user=m1, defaults={'assigned_by': admin, 'department': 'Inventory & Operations'})

        m2, m2_created = User.objects.get_or_create(
            email='manager2@thevalory.com',
            defaults={
                'first_name': 'Fulfillment',
                'last_name': 'Manager 2',
                'role': User.Role.MANAGER,
                'is_staff': True,
                'is_email_verified': True
            }
        )
        if m2_created:
            m2.set_password('ManagerPassword123!')
            m2.save()
            ManagerProfile.objects.get_or_create(user=m2, defaults={'assigned_by': admin, 'department': 'Fulfillment & Logistics'})

