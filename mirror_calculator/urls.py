from django.urls import path
from mirror_calculator import views

urlpatterns = [
    path('mirror-calculate/', views.mirror_calculate, name='mirror_calculate')
]
