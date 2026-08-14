from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from apps.refunds.models import RefundClaim
from apps.orders.models import Order
from apps.accounts.decorators import main_admin_required, manager_required
from apps.policies.models import Policy, PolicyAcceptance
from apps.notifications.models import Notification
from apps.audit.models import AuditLog


@login_required
def submit_refund_claim_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, customer=request.user)

    # 1. Order Status Check (Must be DELIVERED)
    if order.status != Order.Status.DELIVERED:
        messages.error(request, "Refund claims apply strictly for DELIVERED products with damaged package evidence.")
        return redirect('orders:detail', order_id=order.order_id)

    # 2. Check if claim already exists
    if hasattr(order, 'refund_claim'):
        messages.info(request, "You have already submitted a refund claim for this order.")
        return redirect('refunds:claim_detail', claim_id=order.refund_claim.claim_id)

    # 3. 24-Hour Policy Window Validation
    delivery_time = order.updated_at
    hours_since_delivery = (timezone.now() - delivery_time).total_seconds() / 3600
    if hours_since_delivery > 24:
        messages.error(
            request,
            "Refund Claim Expired: Under THE VALORY Refund Policy, damage claims MUST be submitted "
            "within 24 hours of delivery. This order was delivered more than 24 hours ago."
        )
        return redirect('orders:detail', order_id=order.order_id)

    if request.method == 'POST':
        description = request.POST.get('damage_description', '').strip()
        video_url = request.POST.get('unboxing_video_url', '').strip()
        video_file = request.FILES.get('unboxing_video_file')
        photo_1 = request.FILES.get('photo_evidence_1')
        photo_2 = request.FILES.get('photo_evidence_2')
        policy_agreed = request.POST.get('refund_policy_accepted') == 'on'

        if not policy_agreed:
            messages.error(request, "You MUST agree to THE VALORY Refund Policy conditions (Unboxing video + clear photos required).")
            return render(request, 'refunds/submit_claim.html', {'order': order})

        if not (video_url or video_file):
            messages.error(request, "Mandatory Requirement Missing: An unboxing video (File or URL link) is REQUIRED to verify damage claims.")
            return render(request, 'refunds/submit_claim.html', {'order': order})

        if not photo_1:
            messages.error(request, "Mandatory Requirement Missing: At least one clear photo of the damaged product is REQUIRED.")
            return render(request, 'refunds/submit_claim.html', {'order': order})

        claim_id = RefundClaim.generate_claim_id()
        claim = RefundClaim.objects.create(
            claim_id=claim_id,
            order=order,
            customer=request.user,
            damage_description=description,
            unboxing_video_url=video_url,
            unboxing_video_file=video_file,
            photo_evidence_1=photo_1,
            photo_evidence_2=photo_2,
            status=RefundClaim.Status.CLAIM_SUBMITTED
        )

        # Record Policy Acceptance
        PolicyAcceptance.objects.create(
            user=request.user,
            order=order,
            policy_version='1.0',
            acceptance_type=PolicyAcceptance.AcceptanceType.REFUND_CLAIM,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        # Notify Admin / Manager
        Notification.objects.create(
            user=request.user,
            title=f"Refund Claim Submitted #{claim.claim_id}",
            message=f"Your refund claim for Order #{order.order_id} has been received and is under review by THE VALORY quality team.",
            link=f"/refunds/claim/{claim.claim_id}/",
            notification_type=Notification.NotificationType.REFUND_UPDATE
        )

        messages.success(request, f"Refund Claim #{claim.claim_id} submitted successfully. Our team will review your unboxing video within 24-48 hours.")
        return redirect('refunds:claim_detail', claim_id=claim.claim_id)

    return render(request, 'refunds/submit_claim.html', {'order': order, 'hours_left': round(24 - hours_since_delivery, 1)})


@login_required
def claim_detail_view(request, claim_id):
    if request.user.is_main_admin or request.user.is_manager:
        claim = get_object_or_404(RefundClaim.objects.select_related('order', 'customer'), claim_id=claim_id)
    else:
        claim = get_object_or_404(RefundClaim.objects.select_related('order', 'customer'), claim_id=claim_id, customer=request.user)

    return render(request, 'refunds/claim_detail.html', {'claim': claim})


# --- ADMIN ONLY REFUND REVIEW ---

@main_admin_required
def admin_refund_list_view(request):
    claims = RefundClaim.objects.all().select_related('order', 'customer').order_by('-requested_at')
    status_filter = request.GET.get('status')
    if status_filter:
        claims = claims.filter(status=status_filter)
    return render(request, 'dashboard/admin_refunds.html', {'claims': claims, 'status_choices': RefundClaim.Status.choices})


@main_admin_required
def admin_process_claim_view(request, claim_id):
    claim = get_object_or_404(RefundClaim, claim_id=claim_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '').strip()

        if new_status in RefundClaim.Status.values:
            claim.status = new_status
            claim.admin_notes = admin_notes
            claim.reviewed_at = timezone.now()
            claim.save()

            Notification.objects.create(
                user=claim.customer,
                title=f"Refund Claim #{claim.claim_id} Status: {claim.get_status_display()}",
                message=f"Your refund claim for Order #{claim.order.order_id} has been set to: {claim.get_status_display()}.",
                link=f"/refunds/claim/{claim.claim_id}/",
                notification_type=Notification.NotificationType.REFUND_UPDATE
            )

            AuditLog.objects.create(
                actor=request.user,
                action='PROCESS_REFUND_CLAIM',
                target_model='RefundClaim',
                target_id=str(claim.id),
                details=f"Admin updated claim #{claim.claim_id} to status {claim.get_status_display()}"
            )

            messages.success(request, f"Refund Claim #{claim.claim_id} status updated to {claim.get_status_display()}.")

    return redirect('refunds:admin_refunds')
