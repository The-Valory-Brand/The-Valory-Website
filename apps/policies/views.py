from django.shortcuts import render, get_object_or_404
from apps.policies.models import Policy

def shipping_policy_view(request):
    policy = Policy.objects.filter(policy_type=Policy.PolicyType.SHIPPING, is_active=True).first()
    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'title': 'Shipping Policy — THE VALORY',
        'policy_name': 'Shipping Policy'
    })

def refund_policy_view(request):
    policy = Policy.objects.filter(policy_type=Policy.PolicyType.REFUND, is_active=True).first()
    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'title': 'Refund Policy — THE VALORY',
        'policy_name': 'Refund Policy'
    })

def return_exchange_policy_view(request):
    policy = Policy.objects.filter(policy_type=Policy.PolicyType.RETURN_EXCHANGE, is_active=True).first()
    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'title': 'Return & Exchange Policy — THE VALORY',
        'policy_name': 'Return & Exchange Policy'
    })

def order_policy_view(request):
    policy = Policy.objects.filter(policy_type=Policy.PolicyType.ORDER, is_active=True).first()
    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'title': 'Order Terms & Cancellation Policy — THE VALORY',
        'policy_name': 'Order Policy'
    })

def general_policy_view(request):
    policy = Policy.objects.filter(policy_type=Policy.PolicyType.GENERAL, is_active=True).first()
    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'title': 'General Terms — THE VALORY',
        'policy_name': 'General Policy'
    })

def terms_view(request):
    policy = Policy.objects.filter(policy_type=Policy.PolicyType.TERMS, is_active=True).first()
    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'title': 'Terms of Service — THE VALORY',
        'policy_name': 'Terms of Service'
    })
