from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.orders.models import Order
from apps.payments.models import Payment

@login_required
def payment_process_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, customer=request.user)
    payment = getattr(order, 'payment', None)
    return render(request, 'storefront/payment.html', {'order': order, 'payment': payment})
