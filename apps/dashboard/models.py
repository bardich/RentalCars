"""Dashboard models for site settings and configuration."""

from django.db import models


class SiteSettings(models.Model):
    """Site-wide settings and configuration."""
    
    THEME_CHOICES = [
        ('light', 'Clair'),
        ('dark', 'Sombre'),
        ('auto', 'Automatique'),
    ]
    
    # Site Identity
    site_name = models.CharField(max_length=100, default='Rental Cars Morocco', verbose_name='Nom du site')
    site_description = models.TextField(blank=True, verbose_name='Description du site')
    site_logo = models.ImageField(upload_to='site/logo/', blank=True, verbose_name='Logo du site')
    site_favicon = models.ImageField(upload_to='site/favicon/', blank=True, verbose_name='Favicon')
    
    # Contact Information
    site_email = models.EmailField(blank=True, verbose_name='Email de contact')
    site_phone = models.CharField(max_length=50, blank=True, verbose_name='Téléphone')
    site_address = models.TextField(blank=True, verbose_name='Adresse')
    
    # Footer
    site_footer = models.TextField(blank=True, verbose_name='Texte du pied de page')
    
    # Social Media Links
    facebook_url = models.URLField(blank=True, verbose_name='Facebook')
    instagram_url = models.URLField(blank=True, verbose_name='Instagram')
    twitter_url = models.URLField(blank=True, verbose_name='Twitter/X')
    linkedin_url = models.URLField(blank=True, verbose_name='LinkedIn')
    youtube_url = models.URLField(blank=True, verbose_name='YouTube')
    whatsapp_number = models.CharField(max_length=50, blank=True, verbose_name='WhatsApp')
    
    # Theme
    site_theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light', verbose_name='Thème')
    
    # Meta
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')
    
    class Meta:
        verbose_name = 'Paramètres du site'
        verbose_name_plural = 'Paramètres du site'
    
    def __str__(self):
        return f"Paramètres - {self.site_name}"
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings singleton."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
