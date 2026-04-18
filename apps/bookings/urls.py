from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('recherche/', views.search_availability, name='search'),
    path('create/<int:car_id>/', views.create_booking, name='create'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='confirmation'),
    path('admin/', views.booking_list, name='list'),
    path('admin/<int:pk>/', views.booking_detail, name='detail'),
]
