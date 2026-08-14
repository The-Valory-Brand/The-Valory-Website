from django.urls import path
from apps.audit import views

app_name = 'audit'

urlpatterns = [
    path('audit-logs/', views.audit_logs_list_view, name='audit_logs'),
]
