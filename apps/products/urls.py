from django.urls import path
from apps.products import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('shop/', views.shop_view, name='shop'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('product/<int:product_id>/json/', views.product_detail_json_view, name='product_detail_json'),
    path('api/search/', views.search_json_view, name='search_json'),
    path('recently-viewed/', views.recently_viewed_list_view, name='recently_viewed'),

    # Manager / Admin Product URLs
    path('manager/products/', views.manager_product_list_view, name='manager_products'),
    path('manager/products/create/', views.manager_product_create_view, name='manager_product_create'),
    path('manager/products/<int:product_id>/edit/', views.manager_product_edit_view, name='manager_product_edit'),
    path('manager/products/<int:product_id>/toggle/', views.manager_product_toggle_view, name='manager_product_toggle'),
    path('manager/products/<int:product_id>/delete/', views.manager_product_delete_view, name='manager_product_delete'),
    path('manager/products/image/<int:image_id>/delete/', views.manager_product_image_delete_view, name='manager_product_image_delete'),

    # Manager / Admin Category URLs
    path('manager/categories/', views.manager_category_list_view, name='manager_categories'),
    path('manager/categories/create/', views.manager_category_create_view, name='manager_category_create'),
    path('manager/categories/<int:category_id>/edit/', views.manager_category_edit_view, name='manager_category_edit'),
    path('manager/categories/<int:category_id>/delete/', views.manager_category_delete_view, name='manager_category_delete'),
    path('manager/categories/<int:category_id>/image/delete/', views.manager_category_image_delete_view, name='manager_category_image_delete'),

    # Manager / Admin Site Banners URLs
    path('manager/banners/', views.manager_banners_view, name='manager_banners'),
    path('manager/banners/<int:banner_id>/delete/', views.manager_banner_delete_view, name='manager_banner_delete'),
]
