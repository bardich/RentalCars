"""Bookings admin configuration."""

from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Booking admin configuration."""
    list_display = [
        'id', 'car', 'customer_name', 'customer_phone',
        'start_date', 'end_date', 'total_days', 'total_price',
        'booking_status', 'created_at'
    ]
    list_editable = ['booking_status']
    list_filter = ['booking_status', 'start_date', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'customer_email', 'car__title']
    date_hierarchy = 'start_date'
    readonly_fields = ['total_days', 'total_price', 'created_at', 'updated_at']

    fieldsets = (
        ('Client', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Réservation', {
            'fields': ('car', 'start_date', 'end_date', 'total_days', 'total_price')
        }),
        ('Statut', {
            'fields': ('booking_status', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
