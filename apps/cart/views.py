from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.cart.models import Cart, CartItem
from apps.products.models import Product, ProductSize, Size

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_detail_view(request):
    cart = get_or_create_cart(request)
    
    # Revalidate stock for each item in cart
    stock_warnings = []
    for item in cart.items.all().select_related('product'):
        ps = ProductSize.objects.filter(product=item.product, size=item.size).first()
        available = ps.stock_quantity if ps else 0
        if available == 0:
            stock_warnings.append(f"'{item.product.name}' (Size {item.size}) is currently out of stock.")
        elif item.quantity > available:
            item.quantity = available
            item.save()
            stock_warnings.append(f"Quantity for '{item.product.name}' (Size {item.size}) adjusted to available stock ({available}).")

    if stock_warnings:
        for warn in stock_warnings:
            messages.warning(request, warn)

    return render(request, 'storefront/cart.html', {'cart': cart})


@require_POST
def cart_add_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    size_code = request.POST.get('size', '').upper()
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    if size_code not in Size.values:
        messages.error(request, "Please select a valid size option.")
        return redirect('products:product_detail', slug=product.slug)

    # Server-side stock verification
    ps = ProductSize.objects.filter(product=product, size=size_code).first()
    available_stock = ps.stock_quantity if ps else 0

    if available_stock <= 0:
        messages.error(request, f"Size {size_code} for '{product.name}' is currently out of stock.")
        return redirect('products:product_detail', slug=product.slug)

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size_code,
        defaults={'quantity': 0}
    )

    new_total_qty = cart_item.quantity + quantity
    if new_total_qty > available_stock:
        cart_item.quantity = available_stock
        cart_item.save()
        messages.warning(request, f"Added maximum available stock ({available_stock}) for size {size_code}.")
    else:
        cart_item.quantity = new_total_qty
        cart_item.save()
        messages.success(request, f"Added '{product.name}' (Size {size_code}) to your shopping cart.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_item_count': cart.total_items,
            'message': f"Added '{product.name}' (Size {size_code}) to cart."
        })

    return redirect('cart:detail')


@require_POST
def cart_update_view(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, f"Removed '{cart_item.product.name}' from cart.")
    else:
        ps = ProductSize.objects.filter(product=cart_item.product, size=cart_item.size).first()
        available_stock = ps.stock_quantity if ps else 0
        if quantity > available_stock:
            cart_item.quantity = available_stock
            cart_item.save()
            messages.warning(request, f"Quantity adjusted to maximum available stock ({available_stock}).")
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart quantity updated.")

    return redirect('cart:detail')


@require_POST
def cart_remove_view(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f"Removed '{name}' from your cart.")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_item_count': cart.total_items,
            'message': f"Removed '{name}' from cart."
        })
    return redirect('cart:detail')


def cart_json_view(request):
    cart = get_or_create_cart(request)
    items = []
    for item in cart.items.all().select_related('product'):
        img = item.product.images.first()
        items.append({
            'id': item.id,
            'product_id': item.product.id,
            'product_name': item.product.name,
            'product_slug': item.product.slug,
            'size': item.size,
            'quantity': item.quantity,
            'price': float(item.product.price),
            'line_total': float(item.line_total),
            'image_url': img.image.url if img else '/static/images/placeholder.jpg',
        })
    return JsonResponse({
        'total_items': cart.total_items,
        'total_price': float(cart.total_price),
        'items': items
    })
