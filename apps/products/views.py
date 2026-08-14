from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from apps.products.models import Product, Category, ProductSize, ProductImage, RecentlyViewedProduct, Size, SiteBanner
from apps.products.forms import ProductForm, CategoryForm, SiteBannerForm
from apps.accounts.decorators import manager_required
from apps.reviews.models import Review
from apps.audit.models import AuditLog


def home_view(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True).prefetch_related('images', 'sizes')[:8]
    new_arrivals = Product.objects.filter(is_active=True, is_new_arrival=True).prefetch_related('images', 'sizes')[:8]
    categories = Category.objects.filter(is_active=True)
    customer_reviews = Review.objects.filter(is_approved=True, rating__gte=4).select_related('customer', 'product')[:6]
    try:
        hero_banner = SiteBanner.objects.filter(banner_type='HERO').first()
        story_banner = SiteBanner.objects.filter(banner_type='STORY').first()
    except Exception:
        hero_banner = None
        story_banner = None

    return render(request, 'storefront/index.html', {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'customer_reviews': customer_reviews,
        'hero_banner': hero_banner,
        'story_banner': story_banner,
    })


def shop_view(request):
    products = Product.objects.filter(is_active=True).prefetch_related('images', 'sizes', 'category')

    # Category Filter
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        # Resilient category lookup matching slug, alias, or name
        selected_category = Category.objects.filter(
            Q(slug=category_slug) |
            Q(slug='heavyweight-tees' if category_slug == 'tees' else '') |
            Q(slug='oversized-hoodies' if category_slug == 'hoodies' else '') |
            Q(slug='athletic-track-pants' if category_slug == 'trackpants' else '') |
            Q(slug='tees' if category_slug == 'heavyweight-tees' else '') |
            Q(slug='hoodies' if category_slug == 'oversized-hoodies' else '') |
            Q(name__iexact=category_slug),
            is_active=True
        ).first()

        if not selected_category:
            selected_category = Category.objects.filter(
                Q(slug__icontains=category_slug) | Q(name__icontains=category_slug),
                is_active=True
            ).first()

        if selected_category:
            products = products.filter(category=selected_category)

    # Size Filter
    size_filter = request.GET.get('size')
    if size_filter and size_filter in Size.values:
        products = products.filter(sizes__size=size_filter, sizes__stock_quantity__gt=0)

    # Search Filter (Name, SKU, Product ID, Category Name)
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(product_id__icontains=query) |
            Q(category__name__icontains=query) |
            Q(description__icontains=query)
        )

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    products = products.distinct()

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)

    return render(request, 'storefront/shop.html', {
        'products': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'selected_size': size_filter,
        'search_query': query,
        'current_sort': sort,
        'sizes': Size.choices,
    })


def product_detail_view(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'sizes', 'reviews__customer'),
        slug=slug,
        is_active=True
    )

    # Record Recently Viewed for logged-in user
    if request.user.is_authenticated:
        RecentlyViewedProduct.objects.update_or_create(
            user=request.user,
            product=product
        )

    approved_reviews = product.reviews.filter(is_approved=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]

    return render(request, 'storefront/product_detail.html', {
        'product': product,
        'approved_reviews': approved_reviews,
        'related_products': related_products,
        'sizes': product.sizes.all(),
    })


def product_detail_json_view(request, product_id):
    product = get_object_or_404(Product.objects.prefetch_related('images', 'sizes', 'category'), id=product_id, is_active=True)
    images = [img.image.url for img in product.images.all()]
    if not images:
        images = ['/static/images/placeholder.jpg']
    
    sizes = []
    for ps in product.sizes.all():
        sizes.append({
            'size': ps.size,
            'stock': ps.stock_quantity,
            'available': ps.stock_quantity > 0
        })

    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'sku': product.sku,
        'price': float(product.price),
        'discount_price': float(product.discount_price) if product.discount_price else None,
        'category': product.category.name,
        'description': product.description,
        'images': images,
        'sizes': sizes,
    })


def search_json_view(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'products': []})

    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(sku__icontains=query) |
        Q(category__name__icontains=query) |
        Q(description__icontains=query),
        is_active=True
    ).prefetch_related('images')[:8]

    results = []
    for p in products:
        img = p.images.first()
        results.append({
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'price': float(p.price),
            'category': p.category.name,
            'image_url': img.image.url if img else '/static/images/placeholder.jpg'
        })

    return JsonResponse({'products': results})


# --- MANAGER / ADMIN PRODUCT MANAGEMENT ---

@manager_required
def manager_product_list_view(request):
    products = Product.objects.all().select_related('category').prefetch_related('sizes').order_by('-created_at')
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(sku__icontains=query) | Q(product_id__icontains=query)
        )
    return render(request, 'dashboard/manager_products.html', {'products': products, 'search_query': query})


@manager_required
def manager_product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()

            # Handle Size Stock Entries
            for size_code in Size.values:
                stock_key = f"size_stock_{size_code}"
                stock_qty = request.POST.get(stock_key, 0)
                try:
                    qty = int(stock_qty)
                    if qty > 0:
                        ProductSize.objects.create(product=product, size=size_code, stock_quantity=qty)
                except ValueError:
                    pass

            # Handle Product Images
            images = request.FILES.getlist('images')
            for index, img_file in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=img_file,
                    is_primary=(index == 0),
                    display_order=index
                )

            AuditLog.objects.create(
                actor=request.user,
                action='CREATE_PRODUCT',
                target_model='Product',
                target_id=str(product.id),
                details=f"Created product {product.name} (SKU: {product.sku})"
            )

            messages.success(request, f"Product '{product.name}' created successfully.")
            return redirect('products:manager_products')
    else:
        form = ProductForm()

    categories = Category.objects.filter(is_active=True)
    return render(request, 'dashboard/manager_product_form.html', {
        'form': form,
        'sizes': Size.choices,
        'categories': categories,
        'is_edit': False
    })


@manager_required
def manager_product_edit_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # Update Size Stocks
            for size_code in Size.values:
                stock_key = f"size_stock_{size_code}"
                stock_qty = request.POST.get(stock_key, 0)
                try:
                    qty = int(stock_qty)
                    ProductSize.objects.update_or_create(
                        product=product,
                        size=size_code,
                        defaults={'stock_quantity': max(0, qty)}
                    )
                except ValueError:
                    pass

            # Handle new images
            images = request.FILES.getlist('images')
            if images:
                for index, img_file in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image=img_file,
                        is_primary=False,
                        display_order=10 + index
                    )

            AuditLog.objects.create(
                actor=request.user,
                action='EDIT_PRODUCT',
                target_model='Product',
                target_id=str(product.id),
                details=f"Updated product {product.name}"
            )

            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('products:manager_products')
    else:
        form = ProductForm(instance=product)

    existing_sizes = {ps.size: ps.stock_quantity for ps in product.sizes.all()}

    return render(request, 'dashboard/manager_product_form.html', {
        'form': form,
        'product': product,
        'sizes': Size.choices,
        'existing_sizes': existing_sizes,
        'is_edit': True
    })


@manager_required
@require_POST
def manager_product_toggle_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save()

    status_str = "activated" if product.is_active else "deactivated"
    AuditLog.objects.create(
        actor=request.user,
        action='TOGGLE_PRODUCT_STATUS',
        target_model='Product',
        target_id=str(product.id),
        details=f"Product {product.name} {status_str}."
    )

    messages.success(request, f"Product '{product.name}' has been {status_str}.")
    return redirect('products:manager_products')


@manager_required
@require_POST
def manager_product_delete_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    sku = product.sku
    product.delete()

    AuditLog.objects.create(
        actor=request.user,
        action='DELETE_PRODUCT',
        target_model='Product',
        target_id=str(product_id),
        details=f"Deleted product '{product_name}' (SKU: {sku})"
    )

    messages.success(request, f"Product '{product_name}' has been permanently deleted.")
    return redirect('products:manager_products')


# --- CATEGORY MANAGEMENT ---

@manager_required
def manager_category_list_view(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'dashboard/manager_categories.html', {'categories': categories})


@manager_required
def manager_category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created.")
            return redirect('products:manager_categories')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/manager_category_form.html', {'form': form, 'is_edit': False})


@manager_required
def manager_category_edit_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated.")
            return redirect('products:manager_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/manager_category_form.html', {'form': form, 'category': category, 'is_edit': True})


@manager_required
@require_POST
def manager_category_delete_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category_name = category.name
    category.delete()

    AuditLog.objects.create(
        actor=request.user,
        action='DELETE_CATEGORY',
        target_model='Category',
        target_id=str(category_id),
        details=f"Deleted category '{category_name}'"
    )

    messages.success(request, f"Category '{category_name}' has been deleted.")
    return redirect('products:manager_categories')


@manager_required
@require_POST
def manager_product_image_delete_view(request, image_id):
    img = get_object_or_404(ProductImage, id=image_id)
    product_id = img.product.id
    product_name = img.product.name
    img.delete()

    AuditLog.objects.create(
        actor=request.user,
        action='DELETE_PRODUCT_IMAGE',
        target_model='ProductImage',
        target_id=str(image_id),
        details=f"Deleted image for product {product_name}"
    )

    messages.success(request, "Product photo deleted successfully.")
    return redirect('products:manager_product_edit', product_id=product_id)


@manager_required
@require_POST
def manager_category_image_delete_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if category.image:
        category.image.delete(save=True)
        messages.success(request, f"Image for category '{category.name}' deleted.")
    return redirect('products:manager_category_edit', category_id=category.id)


@login_required
def recently_viewed_list_view(request):
    recently_viewed = RecentlyViewedProduct.objects.filter(user=request.user).select_related('product').order_by('-viewed_at')
    return render(request, 'accounts/recently_viewed.html', {'recently_viewed': recently_viewed})


# --- BANNER & HERO IMAGE MANAGEMENT (ADMINS & MANAGERS) ---

@manager_required
def manager_banners_view(request):
    banners = SiteBanner.objects.all()
    if request.method == 'POST':
        banner_type = request.POST.get('banner_type')
        title = request.POST.get('title', '')
        subtitle = request.POST.get('subtitle', '')
        image_file = request.FILES.get('image')

        if banner_type and image_file:
            banner, created = SiteBanner.objects.get_or_create(banner_type=banner_type)
            banner.title = title
            banner.subtitle = subtitle
            banner.image = image_file
            banner.save()

            AuditLog.objects.create(
                actor=request.user,
                action='UPDATE_BANNER',
                target_model='SiteBanner',
                target_id=str(banner.id),
                details=f"Updated site banner '{banner.get_banner_type_display()}'"
            )

            messages.success(request, f"Site image for '{banner.get_banner_type_display()}' updated successfully.")
            return redirect('products:manager_banners')
        else:
            messages.error(request, "Please select a banner section and choose an image file.")

    return render(request, 'dashboard/manager_banners.html', {
        'banners': banners,
        'banner_choices': SiteBanner.BANNER_TYPES,
    })


@manager_required
@require_POST
def manager_banner_delete_view(request, banner_id):
    banner = get_object_or_404(SiteBanner, id=banner_id)
    banner_type_name = banner.get_banner_type_display()
    banner.delete()

    AuditLog.objects.create(
        actor=request.user,
        action='DELETE_BANNER',
        target_model='SiteBanner',
        target_id=str(banner_id),
        details=f"Deleted site banner '{banner_type_name}'"
    )

    messages.success(request, f"Banner '{banner_type_name}' reset to default photo.")
    return redirect('products:manager_banners')


