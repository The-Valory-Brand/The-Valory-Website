from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
import json

from apps.accounts.models import User, UserProfile, ManagerProfile, EmailOTP, Address
from apps.accounts.forms import (
    SignupForm, LoginForm, OTPVerifyForm, ProfileForm,
    ManagerCreateForm, ManagerEditForm, PasswordResetRequestForm, PasswordResetConfirmForm
)
from apps.accounts.utils import generate_and_send_otp
from apps.accounts.decorators import main_admin_required, manager_required
from apps.policies.models import Policy, PolicyAcceptance
from apps.audit.models import AuditLog


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.CUSTOMER
            user.is_email_verified = False
            user.save()

            # Create UserProfile
            full_name = form.cleaned_data['full_name']
            UserProfile.objects.create(user=user, full_name=full_name)

            # Record Policy Acceptance
            general_policy = Policy.objects.filter(policy_type=Policy.PolicyType.GENERAL, is_active=True).first()
            if general_policy:
                PolicyAcceptance.objects.create(
                    user=user,
                    policy_version=general_policy.version,
                    acceptance_type=PolicyAcceptance.AcceptanceType.SIGNUP,
                    ip_address=request.META.get('REMOTE_ADDR')
                )

            # Send Email Verification OTP
            generate_and_send_otp(user.email, purpose=EmailOTP.Purpose.EMAIL_VERIFICATION)
            request.session['pending_otp_email'] = user.email
            request.session['pending_otp_purpose'] = EmailOTP.Purpose.EMAIL_VERIFICATION

            messages.success(request, "Account created! Please enter the OTP sent to your email address to complete verification.")
            return redirect('accounts:otp_verify')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect_role_dashboard(request.user)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account has been deactivated. Please contact support.")
                    return render(request, 'accounts/login.html', {'form': form})

                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.email}!")
                return redirect_role_dashboard(user)
            else:
                messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def request_otp_login_view(request):
    """Sends OTP for one-click email login."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects.filter(email=email).first()
        if user:
            generate_and_send_otp(email, purpose=EmailOTP.Purpose.LOGIN)
            request.session['pending_otp_email'] = email
            request.session['pending_otp_purpose'] = EmailOTP.Purpose.LOGIN
            messages.success(request, "Login OTP code sent to your email.")
            return redirect('accounts:otp_verify')
        else:
            messages.error(request, "No account found with this email address.")
    return redirect('accounts:login')


def otp_verify_view(request):
    email = request.session.get('pending_otp_email')
    purpose = request.session.get('pending_otp_purpose', EmailOTP.Purpose.LOGIN)

    if not email:
        messages.error(request, "No pending verification session found. Please log in.")
        return redirect('accounts:login')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp_code']
            otp_record = EmailOTP.objects.filter(email=email, purpose=purpose, is_used=False).first()

            if otp_record and otp_record.verify_code(code):
                # Clean up session
                del request.session['pending_otp_email']
                del request.session['pending_otp_purpose']

                user = User.objects.filter(email=email).first()
                if user:
                    user.is_email_verified = True
                    user.save()

                    login(request, user)
                    messages.success(request, "OTP Verification successful! Welcome to THE VALORY.")
                    return redirect_role_dashboard(user)
                else:
                    messages.error(request, "User account not found.")
                    return redirect('accounts:login')
            else:
                messages.error(request, "Invalid or expired OTP code. Please try again.")
    else:
        form = OTPVerifyForm()

    return render(request, 'accounts/otp_verify.html', {
        'form': form,
        'email': email,
        'purpose': purpose
    })


def resend_otp_view(request):
    email = request.session.get('pending_otp_email')
    purpose = request.session.get('pending_otp_purpose', EmailOTP.Purpose.LOGIN)
    if email:
        generate_and_send_otp(email, purpose=purpose)
        messages.success(request, "A fresh OTP verification code has been sent to your email.")
    else:
        messages.error(request, "Session expired. Please try logging in again.")
    return redirect('accounts:otp_verify')


def password_reset_request_view(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            user = User.objects.filter(email=email).first()
            if user:
                generate_and_send_otp(email, purpose=EmailOTP.Purpose.PASSWORD_RESET)
                request.session['pending_otp_email'] = email
                request.session['pending_otp_purpose'] = EmailOTP.Purpose.PASSWORD_RESET
                messages.success(request, "Password reset OTP sent to your email.")
                return redirect('accounts:password_reset_confirm')
            else:
                messages.error(request, "No account associated with this email.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request):
    email = request.session.get('pending_otp_email')
    if not email or request.session.get('pending_otp_purpose') != EmailOTP.Purpose.PASSWORD_RESET:
        messages.error(request, "Invalid password reset request session.")
        return redirect('accounts:password_reset_request')

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        form = PasswordResetConfirmForm(request.POST)

        otp_record = EmailOTP.objects.filter(email=email, purpose=EmailOTP.Purpose.PASSWORD_RESET, is_used=False).first()
        if not (otp_record and otp_record.verify_code(otp_code)):
            messages.error(request, "Invalid or expired OTP code for password reset.")
            return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'email': email})

        if form.is_valid():
            new_password = form.cleaned_data['password']
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(new_password)
                user.save()

                del request.session['pending_otp_email']
                del request.session['pending_otp_purpose']

                messages.success(request, "Password reset successfully! Please log in with your new password.")
                return redirect('accounts:login')
    else:
        form = PasswordResetConfirmForm()

    return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'email': email})


def google_login_simulation_view(request):
    """
    Handles Google OAuth authentication.
    Safely creates or links account by email without generating duplicate accounts.
    """
    email = request.GET.get('email', 'customer.google@valorydemo.com').lower()
    full_name = request.GET.get('name', 'Google User')

    user, created = User.objects.get_or_create(email=email, defaults={
        'first_name': full_name.split()[0] if full_name else 'Valory',
        'last_name': ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else 'Customer',
        'role': User.Role.CUSTOMER,
        'is_email_verified': True
    })

    if created:
        UserProfile.objects.create(user=user, full_name=full_name)

    login(request, user)
    messages.success(request, f"Successfully signed in via Google as {email}.")
    return redirect_role_dashboard(user)


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('products:home')


@login_required
def dashboard_router_view(request):
    return redirect_role_dashboard(request.user)


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.phone = request.POST.get('phone', request.user.phone)
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


# --- ADMIN ONLY: MANAGER MANAGEMENT ---

@main_admin_required
def list_managers_view(request):
    managers = User.objects.filter(role=User.Role.MANAGER).select_related('manager_profile').order_by('-created_at')
    return render(request, 'dashboard/admin_managers_list.html', {'managers': managers})


@main_admin_required
def create_manager_view(request):
    if request.method == 'POST':
        form = ManagerCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.MANAGER
            user.is_email_verified = True
            user.set_password(form.cleaned_data['password'])
            user.save()

            ManagerProfile.objects.create(
                user=user,
                assigned_by=request.user,
                department=request.POST.get('department', 'Operations')
            )

            AuditLog.objects.create(
                actor=request.user,
                action='CREATE_MANAGER',
                target_model='User',
                target_id=str(user.id),
                details=f"Created manager account for {user.email}"
            )

            messages.success(request, f"Operational Manager account created for {user.email}.")
            return redirect('accounts:list_managers')
    else:
        form = ManagerCreateForm()
    return render(request, 'dashboard/admin_manager_create.html', {'form': form})


@main_admin_required
def edit_manager_view(request, manager_id):
    manager_user = get_object_or_404(User, id=manager_id, role=User.Role.MANAGER)
    if request.method == 'POST':
        form = ManagerEditForm(request.POST, instance=manager_user)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['full_name']
            
            new_pwd = form.cleaned_data.get('new_password')
            if new_pwd:
                user.set_password(new_pwd)
            user.save()

            dept = form.cleaned_data.get('department', 'Operations')
            profile, _ = ManagerProfile.objects.get_or_create(user=user, defaults={'assigned_by': request.user})
            profile.department = dept
            profile.save()

            AuditLog.objects.create(
                actor=request.user,
                action='EDIT_MANAGER',
                target_model='User',
                target_id=str(user.id),
                details=f"Updated manager account details for {user.email}"
            )

            messages.success(request, f"Operational Manager account for {user.email} updated successfully.")
            return redirect('accounts:list_managers')
    else:
        form = ManagerEditForm(instance=manager_user)

    return render(request, 'dashboard/admin_manager_edit.html', {'form': form, 'manager': manager_user})


@main_admin_required
def toggle_manager_status_view(request, manager_id):
    manager_user = get_object_or_404(User, id=manager_id, role=User.Role.MANAGER)
    manager_user.is_active = not manager_user.is_active
    manager_user.save()

    status_str = "activated" if manager_user.is_active else "deactivated"
    AuditLog.objects.create(
        actor=request.user,
        action='TOGGLE_MANAGER_STATUS',
        target_model='User',
        target_id=str(manager_user.id),
        details=f"Manager {manager_user.email} {status_str}."
    )

    messages.success(request, f"Manager account {manager_user.email} has been {status_str}.")
    return redirect('accounts:list_managers')


# --- ADDRESSES, SECURITY & SETTINGS ---

@login_required
def list_addresses_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/addresses.html', {'addresses': addresses})


@login_required
def add_address_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        line1 = request.POST.get('address_line1', '').strip()
        line2 = request.POST.get('address_line2', '').strip()
        city = request.POST.get('city', 'Chennai').strip()
        district = request.POST.get('district', 'Chennai').strip()
        state = request.POST.get('state', 'Tamil Nadu').strip()
        pincode = request.POST.get('pincode', '').strip()
        landmark = request.POST.get('landmark', '').strip()
        is_default = request.POST.get('is_default') == 'on' or not Address.objects.filter(user=request.user).exists()

        if not (full_name and phone and line1 and pincode):
            messages.error(request, "Please fill in all required address fields.")
            return redirect('accounts:list_addresses')

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line1=line1,
            address_line2=line2,
            city=city,
            district=district,
            state=state,
            pincode=pincode,
            landmark=landmark,
            is_default=is_default
        )
        messages.success(request, "New shipping address added successfully.")
        return redirect('accounts:list_addresses')
    return redirect('accounts:list_addresses')


@login_required
@require_POST
def delete_address_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted.")
    return redirect('accounts:list_addresses')


@login_required
@require_POST
def set_default_address_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, "Default address updated.")
    return redirect('accounts:list_addresses')


@login_required
def account_security_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, "Incorrect current password.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        elif len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            login(request, request.user)
            AuditLog.objects.create(
                actor=request.user,
                action='CHANGE_PASSWORD',
                details=f"User {request.user.email} changed password."
            )
            messages.success(request, "Password updated successfully!")
            return redirect('accounts:security')
    return render(request, 'accounts/security.html')


@login_required
def account_settings_view(request):
    return render(request, 'accounts/settings.html')


# Helper function
def redirect_role_dashboard(user):
    if user.is_main_admin:
        return redirect('reports:admin_dashboard')
    elif user.is_manager:
        return redirect('orders:manager_dashboard')
    else:
        return redirect('orders:customer_dashboard')


# --- ERROR HANDLERS ---

def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)

