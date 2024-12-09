from django.urls import path
from invoice_reader import views


urlpatterns = [
    path('invoice-reader/', views.insert_invoice, name='insert_invoice')
]
