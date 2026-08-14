from django.urls import path
from apps.payments import views

app_name = 'payments'

urlpatterns = [
    path('process/<str:order_id>/', views.payment_process_view, name='process'),
]
