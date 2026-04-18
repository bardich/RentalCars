"""Management command to set up WhatsApp number."""
from django.core.management.base import BaseCommand
from apps.core.models import SiteSettings


class Command(BaseCommand):
    help = 'Set up WhatsApp number for the site'

    def add_arguments(self, parser):
        parser.add_argument(
            'number',
            type=str,
            help='WhatsApp number (with country code, e.g., +212612345678)'
        )

    def handle(self, *args, **options):
        number = options['number']
        settings = SiteSettings.load()
        settings.whatsapp_number = number
        settings.save()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully set WhatsApp number to: {number}')
        )
