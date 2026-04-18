from django.urls import path
from . import views

app_name = 'fleet'

urlpatterns = [
    path('', views.car_list, name='cars'),
    path('<slug:slug>/', views.car_detail, name='car_detail'),
]
