from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='dashboard:login'), name='logout'),
    path('', views.dashboard_home, name='home'),

    # Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),

    # Cars
    path('cars/', views.car_list, name='car_list'),
    path('cars/create/', views.car_create, name='car_create'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('cars/<int:pk>/edit/', views.car_edit, name='car_edit'),
    path('cars/<int:pk>/delete/', views.car_delete, name='car_delete'),

    # Car Images
    path('cars/<int:car_pk>/images/upload/', views.car_image_upload, name='car_image_upload'),
    path('images/<int:image_pk>/delete/', views.car_image_delete, name='car_image_delete'),
    path('images/reorder/', views.car_image_reorder, name='car_image_reorder'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Brands
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/create/', views.brand_create, name='brand_create'),
    path('brands/<int:pk>/edit/', views.brand_edit, name='brand_edit'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
]
