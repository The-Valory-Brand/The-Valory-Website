from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from decimal import Decimal
import secrets

from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart, CartItem
from apps.products.models import ProductSize, RecentlyViewedProduct
from apps.payments.models import Payment
from apps.policies.models import Policy, PolicyAcceptance
from apps.notifications.models import Notification
from apps.accounts.decorators import manager_required, customer_required
from apps.audit.models import AuditLog
from django.views.decorators.http import require_POST


@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.error(request, "Your cart is currently empty.")
        return redirect('cart:detail')

    # Re-validate stock for every item in cart
    for item in cart.items.all().select_related('product'):
        ps = ProductSize.objects.filter(product=item.product, size=item.size).first()
        available = ps.stock_quantity if ps else 0
        if available < item.quantity:
            messages.error(request, f"Stock changed for '{item.product.name}' (Size {item.size}). Please review your cart.")
            return redirect('cart:detail')

    user_profile = getattr(request.user, 'profile', None)

    return render(request, 'storefront/checkout.html', {
        'cart': cart,
        'profile': user_profile,
    })


@login_required
@require_POST
def place_order_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('cart:detail')

    # Verify Explicit Policy Acceptance Checkbox
    policy_accepted = request.POST.get('policy_accepted') == 'on'
    if not policy_accepted:
        messages.error(request, "You MUST accept THE VALORY Order, Shipping, Return & Exchange, and Refund Policies to place an order.")
        return redirect('orders:checkout')

    shipping_name = request.POST.get('shipping_full_name', '').strip()
    shipping_phone = request.POST.get('shipping_phone', '').strip()
    address_line1 = request.POST.get('shipping_address_line1', '').strip()
    address_line2 = request.POST.get('shipping_address_line2', '').strip()
    city = request.POST.get('city', 'Chennai').strip()
    state = request.POST.get('state', 'Tamil Nadu').strip()
    postal_code = request.POST.get('postal_code', '').strip()
    payment_method = request.POST.get('payment_method', Payment.Method.UPI)

    if not (shipping_name and shipping_phone and address_line1 and postal_code):
        messages.error(request, "Please fill in all required shipping address fields.")
        return redirect('orders:checkout')

    try:
        with transaction.atomic():
            # 1. Lock and Re-validate Stock with select_for_update()
            cart_items = list(cart.items.all().select_related('product'))
            for item in cart_items:
                ps = ProductSize.objects.select_for_update().filter(product=item.product, size=item.size).first()
                if not ps or ps.stock_quantity < item.quantity:
                    messages.error(request, f"Sorry! '{item.product.name}' (Size {item.size}) just ran out of stock. Order cancelled.")
                    return redirect('cart:detail')

            # 2. Calculate Server Totals
            subtotal = sum(item.total_price for item in cart_items)
            shipping_fee = Decimal('0.00') if subtotal >= Decimal('2999.00') else Decimal('100.00')
            total_amount = subtotal + shipping_fee

            # 3. Create Order
            order_id = Order.generate_order_id()
            order = Order.objects.create(
                order_id=order_id,
                customer=request.user,
                status=Order.Status.PAYMENT_CONFIRMED,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                total_amount=total_amount,
                shipping_full_name=shipping_name,
                shipping_phone=shipping_phone,
                shipping_address_line1=address_line1,
                shipping_address_line2=address_line2,
                city=city,
                state=state,
                postal_code=postal_code,
                policy_version='1.0',
            )

            # 4. Create OrderItems & Deduct Inventory
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    sku=item.product.sku,
                    size=item.size,
                    quantity=item.quantity,
                    price_at_purchase=item.unit_price,
                    total_price=item.total_price,
                )
                # Deduct Stock
                ps = ProductSize.objects.select_for_update().get(product=item.product, size=item.size)
                ps.stock_quantity -= item.quantity
                ps.save()

            # 5. Create Payment Record
            txn_id = f"TXN-{secrets.token_hex(6).upper()}"
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                transaction_id=txn_id,
                amount=total_amount,
                status=Payment.Status.COMPLETED,
                paid_at=timezone.now()
            )

            # 6. Record Context-Aware Policy Acceptance
            PolicyAcceptance.objects.create(
                user=request.user,
                order=order,
                policy_version='1.0',
                acceptance_type=PolicyAcceptance.AcceptanceType.CHECKOUT,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            # 7. Customer Notification
            Notification.objects.create(
                user=request.user,
                title=f"Order Placed #{order.order_id}",
                message=f"Thank you for your order! Total amount: ₹{order.total_amount}. Your items are being prepared for dispatch across Tamil Nadu.",
                link=f"/orders/detail/{order.order_id}/",
                notification_type=Notification.NotificationType.ORDER_STATUS
            )

            # 8. Clear Cart
            cart.items.all().delete()

            messages.success(request, f"Order #{order.order_id} successfully placed! Thank you for choosing THE VALORY.")
            return redirect('orders:detail', order_id=order.order_id)

    except Exception as e:
        messages.error(request, f"An unexpected error occurred while placing your order: {e}")
        return redirect('orders:checkout')


@login_required
def customer_dashboard_view(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related('items').order_by('-created_at')
    recently_viewed = RecentlyViewedProduct.objects.filter(user=request.user).select_related('product')[:6]
    return render(request, 'dashboard/customer_dashboard.html', {
        'orders': orders,
        'recently_viewed': recently_viewed
    })


@login_required
def order_detail_view(request, order_id):
    if request.user.is_main_admin or request.user.is_manager:
        order = get_object_or_404(Order.objects.prefetch_related('items', 'payment'), order_id=order_id)
    else:
        order = get_object_or_404(Order.objects.prefetch_related('items', 'payment'), order_id=order_id, customer=request.user)

    return render(request, 'dashboard/order_detail.html', {'order': order})


@login_required
@require_POST
def cancel_order_view(request, order_id):
    """
    CRITICAL CANCELLATION BUSINESS LOGIC:
    Customer can cancel ONLY before dispatch (status is PLACED, PAYMENT_CONFIRMED, PROCESSING, or PACKED).
    Once DISPATCHED or DELIVERED, backend strictly rejects cancellation!
    """
    order = get_object_or_404(Order, order_id=order_id, customer=request.user)

    # Server-side verification
    if not order.can_cancel:
        messages.error(
            request,
            f"Cancellation Rejected: Order #{order.order_id} has already been DISPATCHED/DELIVERED. "
            "Under THE VALORY policy, orders cannot be cancelled after dispatch."
        )
        return redirect('orders:detail', order_id=order.order_id)

    reason = request.POST.get('cancellation_reason', 'Customer requested cancellation before dispatch.')

    with transaction.atomic():
        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.cancellation_reason = reason
        order.save()

        # Restore Product Stock
        for item in order.items.all():
            if item.product:
                ps = ProductSize.objects.select_for_update().filter(product=item.product, size=item.size).first()
                if ps:
                    ps.stock_quantity += item.quantity
                    ps.save()

        # Update Payment Status if exists
        if hasattr(order, 'payment'):
            order.payment.status = Payment.Status.REFUNDED
            order.payment.save()

        # Create Notification & Audit Log
        Notification.objects.create(
            user=request.user,
            title=f"Order Cancelled #{order.order_id}",
            message=f"Your order #{order.order_id} has been cancelled prior to dispatch. Refund processed if applicable.",
            link=f"/orders/detail/{order.order_id}/",
            notification_type=Notification.NotificationType.ORDER_STATUS
        )

        AuditLog.objects.create(
            actor=request.user,
            action='CANCEL_ORDER',
            target_model='Order',
            target_id=str(order.id),
            details=f"Customer cancelled order {order.order_id} before dispatch."
        )

    messages.success(request, f"Order #{order.order_id} has been cancelled successfully.")
    return redirect('orders:customer_dashboard')


# --- MANAGER ORDER DASHBOARD ---

@manager_required
def manager_dashboard_view(request):
    orders = Order.objects.all().select_related('customer').prefetch_related('items').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter and status_filter in Order.Status.values:
        orders = orders.filter(status=status_filter)

    query = request.GET.get('q', '').strip()
    if query:
        orders = orders.filter(
            order_id__icontains=query
        ) | orders.filter(
            customer__email__icontains=query
        ) | orders.filter(
            shipping_full_name__icontains=query
        )

    pending_count = Order.objects.filter(status__in=[Order.Status.PLACED, Order.Status.PAYMENT_CONFIRMED]).count()
    processing_count = Order.objects.filter(status=Order.Status.PROCESSING).count()
    packed_count = Order.objects.filter(status=Order.Status.PACKED).count()
    dispatched_count = Order.objects.filter(status=Order.Status.DISPATCHED).count()

    return render(request, 'dashboard/manager_orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': query,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'packed_count': packed_count,
        'dispatched_count': dispatched_count,
        'status_choices': Order.Status.choices,
    })


@manager_required
@require_POST
def manager_update_order_status_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    new_status = request.POST.get('status')
    courier_name = request.POST.get('courier_name', '').strip()
    tracking_number = request.POST.get('tracking_number', '').strip()

    if new_status in Order.Status.values:
        old_status = order.get_status_display()
        order.status = new_status

        if new_status == Order.Status.DISPATCHED:
            order.courier_name = courier_name or 'Professional Courier (Tamil Nadu)'
            order.tracking_number = tracking_number or f"TPC{secrets.randbelow(900000) + 100000}IN"
            order.dispatched_at = timezone.now()

        order.save()

        # Send Notification to Customer
        Notification.objects.create(
            user=order.customer,
            title=f"Order Status Update #{order.order_id}",
            message=f"Your order status has been updated to: {order.get_status_display()}." + 
                    (f" Tracking: {order.tracking_number} via {order.courier_name}" if new_status == Order.Status.DISPATCHED else ""),
            link=f"/orders/detail/{order.order_id}/",
            notification_type=Notification.NotificationType.ORDER_STATUS
        )

        AuditLog.objects.create(
            actor=request.user,
            action='UPDATE_ORDER_STATUS',
            target_model='Order',
            target_id=str(order.id),
            details=f"Order #{order.order_id} status changed from {old_status} to {order.get_status_display()}"
        )

        messages.success(request, f"Order #{order.order_id} status updated to {order.get_status_display()}.")

    return redirect('orders:manager_dashboard')
