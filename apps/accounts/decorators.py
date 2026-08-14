from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from apps.accounts.models import User

def main_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not request.user.is_main_admin:
            raise PermissionDenied("Access Denied: Business Reports and System Administration are strictly restricted to Main Admin.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access the management panel.")
            return redirect('accounts:login')
        if not (request.user.is_main_admin or request.user.is_manager):
            raise PermissionDenied("Access Denied: Operational Management area requires Manager or Admin privileges.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to proceed.")
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
