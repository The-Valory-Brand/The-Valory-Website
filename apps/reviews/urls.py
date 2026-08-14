from django.urls import path
from apps.reviews import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:product_id>/', views.add_review_view, name='add'),
    
    # Admin URLs
    path('admin/list/', views.admin_review_list_view, name='admin_reviews'),
    path('admin/toggle/<int:review_id>/', views.admin_review_toggle_view, name='admin_toggle'),
]
