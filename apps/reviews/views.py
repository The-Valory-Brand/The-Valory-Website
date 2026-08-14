from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from apps.reviews.models import Review
from apps.products.models import Product
from apps.orders.models import Order
from apps.accounts.decorators import main_admin_required
from apps.audit.models import AuditLog


@login_required
@require_POST
def add_review_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    rating = int(request.POST.get('rating', 5))
    title = request.POST.get('title', '').strip()
    comment = request.POST.get('comment', '').strip()

    if not (title and comment):
        messages.error(request, "Please provide a review title and comment.")
        return redirect('products:product_detail', slug=product.slug)

    # Verify if customer purchased product
    has_purchased = Order.objects.filter(
        customer=request.user,
        items__product=product,
        status__in=[Order.Status.DELIVERED, Order.Status.DISPATCHED]
    ).exists()

    review, created = Review.objects.update_or_create(
        product=product,
        customer=request.user,
        defaults={
            'rating': max(1, min(5, rating)),
            'title': title,
            'comment': comment,
            'is_verified_purchaser': has_purchased,
            'is_approved': True
        }
    )

    msg = "Thank you! Your product review has been submitted." if created else "Your review has been updated."
    messages.success(request, msg)
    return redirect('products:product_detail', slug=product.slug)


@main_admin_required
def admin_review_list_view(request):
    reviews = Review.objects.all().select_related('product', 'customer').order_by('-created_at')
    return render(request, 'dashboard/admin_reviews.html', {'reviews': reviews})


@main_admin_required
@require_POST
def admin_review_toggle_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = not review.is_approved
    review.save()

    status_str = "approved" if review.is_approved else "hidden"
    AuditLog.objects.create(
        actor=request.user,
        action='TOGGLE_REVIEW_MODERATION',
        target_model='Review',
        target_id=str(review.id),
        details=f"Review #{review.id} {status_str}"
    )

    messages.success(request, f"Review has been {status_str}.")
    return redirect('reviews:admin_reviews')
