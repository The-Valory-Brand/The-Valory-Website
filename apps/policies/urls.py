from django.urls import path
from apps.policies import views

app_name = 'policies'

urlpatterns = [
    path('shipping/', views.shipping_policy_view, name='shipping'),
    path('refund/', views.refund_policy_view, name='refund'),
    path('return-exchange/', views.return_exchange_policy_view, name='return_exchange'),
    path('order/', views.order_policy_view, name='order'),
    path('general/', views.general_policy_view, name='general'),
    path('terms/', views.terms_view, name='terms'),
]
