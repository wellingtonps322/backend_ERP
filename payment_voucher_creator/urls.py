from django.urls import path
from payment_voucher_creator import views

urlpatterns = [
    path('payment-voucher/', views.payment_voucher, name='payment_voucher')
]
