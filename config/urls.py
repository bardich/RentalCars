"""URL configuration for Rental Cars Morocco."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('contact/', core_views.contact, name='contact'),
    path('a-propos/', core_views.about, name='about'),
    path('faq/', core_views.faq, name='faq'),
    path('conditions/', core_views.terms, name='terms'),
    path('voitures/', include('apps.fleet.urls', namespace='fleet')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('reservations/', include('apps.bookings.urls', namespace='bookings')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
