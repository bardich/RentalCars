from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'email', 'phone']

    def has_add_permission(self, request):
        if SiteSettings.objects.exists():
            return False
        return True
