"""Booking models for car reservations."""

from django.db import models
from django.urls import reverse


class Booking(models.Model):
    """Booking/Reservation model."""

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
        ('completed', 'Terminée'),
    ]

    car = models.ForeignKey('fleet.RentalCar', on_delete=models.CASCADE, related_name='bookings', verbose_name='Véhicule')
    customer_name = models.CharField(max_length=200, verbose_name='Nom du client')
    customer_phone = models.CharField(max_length=20, verbose_name='Téléphone')
    customer_email = models.EmailField(blank=True, verbose_name='Email')

    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    total_days = models.PositiveIntegerField(verbose_name='Nombre de jours')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix total (MAD)')

    booking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Statut')
    notes = models.TextField(blank=True, verbose_name='Notes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.car} ({self.start_date} au {self.end_date})"

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            from datetime import timedelta
            self.total_days = (self.end_date - self.start_date).days + 1
            if self.car and not self.total_price:
                self.total_price = self.car.daily_price * self.total_days
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('dashboard:booking_detail', kwargs={'pk': self.pk})

    @property
    def is_active(self):
        """Check if booking is active (pending or confirmed)."""
        return self.booking_status in ['pending', 'confirmed']

    @property
    def whatsapp_message(self):
        """Generate WhatsApp inquiry message."""
        return (
            f"Bonjour, je suis intéressé par la location de {self.car} "
            f"du {self.start_date.strftime('%d/%m/%Y')} au {self.end_date.strftime('%d/%m/%Y')}. "
            f"Est-elle disponible ?"
        )
