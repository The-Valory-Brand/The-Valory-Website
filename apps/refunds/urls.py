from django.urls import path
from apps.refunds import views

app_name = 'refunds'

urlpatterns = [
    path('submit/<str:order_id>/', views.submit_refund_claim_view, name='submit_claim'),
    path('claim/<str:claim_id>/', views.claim_detail_view, name='claim_detail'),

    # Admin URLs
    path('admin/list/', views.admin_refund_list_view, name='admin_refunds'),
    path('admin/process/<str:claim_id>/', views.admin_process_claim_view, name='admin_process'),
]
