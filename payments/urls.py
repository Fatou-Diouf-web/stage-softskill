from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentView.as_view(), name='payment_page'),
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('course/<int:course_id>/', views.course_payment, name='course_payment'),
    path('init-paytech/<int:course_id>/', views.init_paytech_payment, name='init_paytech_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('paytech/ipn/', views.paytech_ipn, name='paytech_ipn'),
    path('process/<int:course_id>/<str:payment_method>/', views.process_payment, name='process_payment'),
]
