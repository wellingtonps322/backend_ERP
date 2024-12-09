from django.urls import path
from route_finder import views

urlpatterns = [
    path('route-finder/', views.route_finder, name='route_finder')
]
