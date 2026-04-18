from .models import SiteSettings


def site_settings(request):
    """Add site settings to template context."""
    try:
        settings = SiteSettings.load()
    except:
        settings = None
    return {'site_settings': settings}
