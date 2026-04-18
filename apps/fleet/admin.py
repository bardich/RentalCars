"""Fleet admin configuration."""

from django.contrib import admin
from .models import Category, Brand, CarFeature, RentalCar, CarImage


class CarImageInline(admin.TabularInline):
    """Inline admin for car images."""
    model = CarImage
    extra = 3
    fields = ['image', 'alt_text', 'is_featured', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configuration."""
    list_display = ['name', 'slug', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Brand admin configuration."""
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(CarFeature)
class CarFeatureAdmin(admin.ModelAdmin):
    """Car feature admin configuration."""
    list_display = ['name', 'icon', 'is_active']
    list_editable = ['icon', 'is_active']
    search_fields = ['name']


@admin.register(RentalCar)
class RentalCarAdmin(admin.ModelAdmin):
    """Rental car admin configuration."""
    list_display = [
        'title', 'brand', 'model_name', 'year', 'category',
        'daily_price', 'availability_status', 'featured', 'active'
    ]
    list_editable = ['daily_price', 'availability_status', 'featured', 'active']
    list_filter = ['category', 'brand', 'transmission', 'fuel_type', 'availability_status', 'featured', 'active']
    search_fields = ['title', 'model_name', 'brand__name']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['features']
    inlines = [CarImageInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'category', 'brand', 'model_name', 'year')
        }),
        ('Spécifications', {
            'fields': ('transmission', 'fuel_type', 'seats', 'doors', 'luggage_capacity', 'color', 'mileage')
        }),
        ('Tarification', {
            'fields': ('daily_price', 'weekly_price', 'monthly_price', 'deposit_amount')
        }),
        ('Description', {
            'fields': ('description', 'features')
        }),
        ('Statut', {
            'fields': ('featured', 'active', 'availability_status', 'available_from')
        }),
    )


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    """Car image admin configuration."""
    list_display = ['car', 'alt_text', 'is_featured', 'order']
    list_editable = ['is_featured', 'order']
    list_filter = ['is_featured']
    search_fields = ['car__title', 'alt_text']
