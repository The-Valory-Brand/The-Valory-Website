from django.db import models
from django.utils.text import slugify
from django.conf import settings
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Size(models.TextChoices):
    S = 'S', 'Small (S)'
    M = 'M', 'Medium (M)'
    L = 'L', 'Large (L)'
    XL = 'XL', 'Extra Large (XL)'
    XXL = 'XXL', 'Double XL (XXL)'


class Product(models.Model):
    sku = models.CharField('SKU', max_length=50, unique=True, db_index=True)
    product_id = models.CharField('Product Unique ID', max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.sku}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def current_price(self):
        return self.discount_price if (self.discount_price and self.discount_price < self.price) else self.price

    @property
    def total_stock(self):
        return sum(variant.stock_quantity for variant in self.sizes.all())

    @property
    def is_in_stock(self):
        return self.total_stock > 0

    @property
    def primary_image(self):
        first_img = self.images.filter(is_primary=True).first()
        if not first_img:
            first_img = self.images.first()
        return first_img.image.url if first_img and first_img.image else None

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0.0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10, choices=Size.choices)
    stock_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')
        ordering = ['product', 'size']

    def __str__(self):
        return f"{self.product.name} - Size {self.size} ({self.stock_quantity} in stock)"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return f"Image for {self.product.name}"


class RecentlyViewedProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recently_viewed')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} viewed {self.product.name}"


class SiteBanner(models.Model):
    BANNER_TYPES = (
        ('HERO', 'Main Editorial Hero Background Image'),
        ('STORY', 'Brand Story Section Image'),
        ('PROMO', 'Promotional Banner Image'),
    )
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, unique=True)
    title = models.CharField(max_length=255, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='banners/')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_banner_type_display()}"

