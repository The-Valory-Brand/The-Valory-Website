from django.urls import path
from apps.orders import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('place/', views.place_order_view, name='place'),
    path('my-orders/', views.customer_dashboard_view, name='customer_dashboard'),
    path('detail/<str:order_id>/', views.order_detail_view, name='detail'),
    path('cancel/<str:order_id>/', views.cancel_order_view, name='cancel'),

    # Manager URLs
    path('manager/dashboard/', views.manager_dashboard_view, name='manager_dashboard'),
    path('manager/update-status/<str:order_id>/', views.manager_update_order_status_view, name='manager_update_status'),
]
