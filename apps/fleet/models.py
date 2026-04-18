"""Fleet models for car rental management."""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Car category model."""
    name = models.CharField(max_length=100, verbose_name='Nom')
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to='categories/icons/', blank=True, verbose_name='Icône')
    image = models.ImageField(upload_to='categories/images/', blank=True, verbose_name='Image')
    description = models.TextField(blank=True, verbose_name='Description')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('fleet:category', kwargs={'slug': self.slug})


class Brand(models.Model):
    """Car brand model."""
    name = models.CharField(max_length=100, verbose_name='Nom')
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/logos/', blank=True, verbose_name='Logo')

    class Meta:
        verbose_name = 'Marque'
        verbose_name_plural = 'Marques'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CarFeature(models.Model):
    """Car feature model for many-to-many relationship."""
    name = models.CharField(max_length=100, verbose_name='Nom')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icône (classe CSS)')
    is_active = models.BooleanField(default=True, verbose_name='Actif')

    class Meta:
        verbose_name = 'Équipement'
        verbose_name_plural = 'Équipements'
        ordering = ['name']

    def __str__(self):
        return self.name


class RentalCar(models.Model):
    """Rental car model with full specifications."""

    TRANSMISSION_CHOICES = [
        ('manual', 'Manuelle'),
        ('automatic', 'Automatique'),
        ('semi_auto', 'Semi-automatique'),
    ]

    FUEL_CHOICES = [
        ('gasoline', 'Essence'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybride'),
        ('electric', 'Électrique'),
    ]

    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('reserved', 'Réservé'),
        ('rented', 'Loué'),
        ('maintenance', 'Maintenance'),
    ]

    title = models.CharField(max_length=200, verbose_name='Titre')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='cars', verbose_name='Catégorie')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='cars', verbose_name='Marque')
    model_name = models.CharField(max_length=100, verbose_name='Modèle')
    year = models.PositiveIntegerField(verbose_name='Année')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='manual', verbose_name='Transmission')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='gasoline', verbose_name='Carburant')
    seats = models.PositiveIntegerField(default=5, verbose_name='Places')
    doors = models.PositiveIntegerField(default=4, verbose_name='Portes')
    luggage_capacity = models.PositiveIntegerField(default=2, verbose_name='Capacité bagages (valises)')
    color = models.CharField(max_length=50, blank=True, verbose_name='Couleur')
    mileage = models.PositiveIntegerField(default=0, verbose_name='Kilométrage')
    registration_city = models.CharField(max_length=100, blank=True, verbose_name='Ville d\'immatriculation')

    daily_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix journalier (MAD)')
    weekly_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Prix hebdomadaire (MAD)')
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Prix mensuel (MAD)')
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Caution (MAD)')

    description = models.TextField(blank=True, verbose_name='Description')
    features = models.ManyToManyField(CarFeature, blank=True, related_name='cars', verbose_name='Équipements')

    featured = models.BooleanField(default=False, verbose_name='En vedette')
    active = models.BooleanField(default=True, verbose_name='Actif')
    availability_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='Statut de disponibilité')
    available_from = models.DateField(blank=True, null=True, verbose_name='Disponible à partir du')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Véhicule'
        verbose_name_plural = 'Véhicules'
        ordering = ['-featured', '-created_at']

    def __str__(self):
        return f"{self.brand} {self.model_name} {self.year}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand}-{self.model_name}-{self.year}")
        if not self.weekly_price:
            self.weekly_price = self.daily_price * 6
        if not self.monthly_price:
            self.monthly_price = self.daily_price * 25
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('fleet:car_detail', kwargs={'slug': self.slug})

    @property
    def main_image(self):
        """Get the main/featured image or first image."""
        featured = self.images.filter(is_featured=True).first()
        if featured:
            return featured
        return self.images.first()

    def is_available_for_dates(self, start_date, end_date):
        """Check if car is available for given date range."""
        from apps.bookings.models import Booking
        overlapping = Booking.objects.filter(
            car=self,
            booking_status__in=['pending', 'confirmed'],
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists()
        return not overlapping and self.availability_status == 'available'


class CarImage(models.Model):
    """Car images model."""
    car = models.ForeignKey(RentalCar, on_delete=models.CASCADE, related_name='images', verbose_name='Véhicule')
    image = models.ImageField(upload_to='cars/images/', verbose_name='Image')
    alt_text = models.CharField(max_length=200, blank=True, verbose_name='Texte alternatif')
    is_featured = models.BooleanField(default=False, verbose_name='Image principale')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        ordering = ['order', '-is_featured']

    def __str__(self):
        return f"Image de {self.car}"

    def save(self, *args, **kwargs):
        if self.is_featured:
            CarImage.objects.filter(car=self.car, is_featured=True).update(is_featured=False)
        super().save(*args, **kwargs)
