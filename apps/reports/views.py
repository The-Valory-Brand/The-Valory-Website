from django.shortcuts import render
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from datetime import timedelta, datetime
import csv
from decimal import Decimal

from apps.accounts.decorators import main_admin_required
from apps.accounts.models import User
from apps.orders.models import Order, OrderItem
from apps.products.models import Product, ProductSize, Category
from apps.refunds.models import RefundClaim
from apps.reviews.models import Review
from apps.audit.models import AuditLog


@main_admin_required
def admin_dashboard_view(request):
    """
    MAIN ADMIN BUSINESS DASHBOARD
    Restricted exclusively to Main Admin. Calculates real database metrics.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Filter parameter
    date_filter = request.GET.get('period', 'this_month')
    start_date = month_start

    if date_filter == 'today':
        start_date = today_start
    elif date_filter == '7days':
        start_date = now - timedelta(days=7)
    elif date_filter == '30days':
        start_date = now - timedelta(days=30)
    elif date_filter == 'all':
        start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)

    # 1. Revenue Metrics (Excluding Cancelled Orders)
    valid_orders = Order.objects.filter(created_at__gte=start_date).exclude(status=Order.Status.CANCELLED)
    total_revenue = valid_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    today_revenue = Order.objects.filter(created_at__gte=today_start).exclude(status=Order.Status.CANCELLED).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    monthly_revenue = Order.objects.filter(created_at__gte=month_start).exclude(status=Order.Status.CANCELLED).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # 2. Order Metrics
    total_orders_count = valid_orders.count()
    today_orders_count = Order.objects.filter(created_at__gte=today_start).count()
    cancelled_orders_count = Order.objects.filter(created_at__gte=start_date, status=Order.Status.CANCELLED).count()

    # Status Distribution
    status_counts = {
        'placed': Order.objects.filter(created_at__gte=start_date, status=Order.Status.PLACED).count(),
        'confirmed': Order.objects.filter(created_at__gte=start_date, status=Order.Status.PAYMENT_CONFIRMED).count(),
        'processing': Order.objects.filter(created_at__gte=start_date, status=Order.Status.PROCESSING).count(),
        'packed': Order.objects.filter(created_at__gte=start_date, status=Order.Status.PACKED).count(),
        'dispatched': Order.objects.filter(created_at__gte=start_date, status=Order.Status.DISPATCHED).count(),
        'delivered': Order.objects.filter(created_at__gte=start_date, status=Order.Status.DELIVERED).count(),
        'cancelled': cancelled_orders_count,
    }

    # 3. Customer Metrics
    total_customers_count = User.objects.filter(role=User.Role.CUSTOMER).count()
    new_customers_count = User.objects.filter(role=User.Role.CUSTOMER, created_at__gte=start_date).count()

    # 4. Monthly Refund & Return Analytics
    refund_claims = RefundClaim.objects.filter(requested_at__gte=start_date)
    total_refund_claims = refund_claims.count()
    approved_refund_claims = refund_claims.filter(status=RefundClaim.Status.APPROVED).count()
    rejected_refund_claims = refund_claims.filter(status=RefundClaim.Status.REJECTED).count()
    pending_refund_claims = refund_claims.filter(status__in=[RefundClaim.Status.CLAIM_SUBMITTED, RefundClaim.Status.UNDER_REVIEW]).count()
    
    approved_refund_amount = Order.objects.filter(
        refund_claim__status=RefundClaim.Status.APPROVED,
        refund_claim__requested_at__gte=start_date
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # 5. Inventory & Low Stock Alert
    low_stock_threshold = 5
    low_stock_items = ProductSize.objects.filter(stock_quantity__lte=low_stock_threshold).select_related('product')[:10]

    # 6. Product Performance (Top Selling)
    top_products = OrderItem.objects.filter(order__created_at__gte=start_date).values(
        'product__name', 'sku'
    ).annotate(
        total_units=Sum('quantity'),
        total_sales=Sum('total_price')
    ).order_by('-total_units')[:5]

    # 7. Audit Log Sample
    recent_audit_logs = AuditLog.objects.all().select_related('actor')[:10]

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'monthly_revenue': monthly_revenue,
        'total_orders_count': total_orders_count,
        'today_orders_count': today_orders_count,
        'cancelled_orders_count': cancelled_orders_count,
        'status_counts': status_counts,
        'total_customers_count': total_customers_count,
        'new_customers_count': new_customers_count,
        'total_refund_claims': total_refund_claims,
        'approved_refund_claims': approved_refund_claims,
        'rejected_refund_claims': rejected_refund_claims,
        'pending_refund_claims': pending_refund_claims,
        'approved_refund_amount': approved_refund_amount,
        'low_stock_items': low_stock_items,
        'top_products': top_products,
        'recent_audit_logs': recent_audit_logs,
        'current_period': date_filter,
    })


# --- CSV EXPORT UTILITIES (MAIN ADMIN ONLY) ---

@main_admin_required
def export_sales_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="VALORY_Sales_Report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer Email', 'Date', 'Status', 'Subtotal (INR)', 'Shipping (INR)', 'Total Amount (INR)'])

    orders = Order.objects.all().select_related('customer').order_by('-created_at')
    for order in orders:
        writer.writerow([
            order.order_id,
            order.customer.email,
            order.created_at.strftime('%Y-%m-%d %H:%M'),
            order.get_status_display(),
            order.subtotal,
            order.shipping_fee,
            order.total_amount
        ])

    return response


@main_admin_required
def export_returns_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="VALORY_Refund_Claims_Report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Claim ID', 'Order ID', 'Customer Email', 'Requested Date', 'Status', 'Damage Description', 'Admin Notes'])

    claims = RefundClaim.objects.all().select_related('order', 'customer').order_by('-requested_at')
    for claim in claims:
        writer.writerow([
            claim.claim_id,
            claim.order.order_id,
            claim.customer.email,
            claim.requested_at.strftime('%Y-%m-%d %H:%M'),
            claim.get_status_display(),
            claim.damage_description,
            claim.admin_notes or ''
        ])

    return response


@main_admin_required
def export_inventory_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="VALORY_Inventory_Report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['SKU', 'Product Name', 'Category', 'Size', 'Stock Quantity', 'Price (INR)', 'Status'])

    sizes = ProductSize.objects.all().select_related('product', 'product__category').order_by('product__name', 'size')
    for ps in sizes:
        writer.writerow([
            ps.product.sku,
            ps.product.name,
            ps.product.category.name,
            ps.size,
            ps.stock_quantity,
            ps.product.price,
            'Active' if ps.product.is_active else 'Inactive'
        ])

    return response
