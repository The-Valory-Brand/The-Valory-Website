from django.urls import path
from apps.reports import views

app_name = 'reports'

urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/export/sales/', views.export_sales_report_csv, name='export_sales_csv'),
    path('admin/export/returns/', views.export_returns_report_csv, name='export_returns_csv'),
    path('admin/export/inventory/', views.export_inventory_report_csv, name='export_inventory_csv'),
]
