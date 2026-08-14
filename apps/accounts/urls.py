from django.urls import path
from apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('login/otp-request/', views.request_otp_login_view, name='request_otp_login'),
    path('otp-verify/', views.otp_verify_view, name='otp_verify'),
    path('otp-resend/', views.resend_otp_view, name='resend_otp'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('google-login/', views.google_login_simulation_view, name='google_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_router_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('addresses/', views.list_addresses_view, name='list_addresses'),
    path('addresses/add/', views.add_address_view, name='add_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address_view, name='delete_address'),
    path('addresses/<int:address_id>/default/', views.set_default_address_view, name='set_default_address'),
    path('security/', views.account_security_view, name='security'),
    path('settings/', views.account_settings_view, name='settings'),
    
    # Main Admin Manager Management
    path('admin/managers/', views.list_managers_view, name='list_managers'),
    path('admin/managers/create/', views.create_manager_view, name='create_manager'),
    path('admin/managers/<int:manager_id>/edit/', views.edit_manager_view, name='edit_manager'),
    path('admin/managers/<int:manager_id>/toggle/', views.toggle_manager_status_view, name='toggle_manager_status'),
]
