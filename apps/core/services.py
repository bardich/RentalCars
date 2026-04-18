"""Core services for the application."""
import urllib.parse
from datetime import date
from typing import Optional

from .models import SiteSettings


class WhatsAppService:
    """Service for generating WhatsApp inquiry links and messages."""

    @classmethod
    def get_whatsapp_number(cls) -> Optional[str]:
        """Get the WhatsApp number from site settings."""
        settings = SiteSettings.load()
        return settings.whatsapp_number

    @classmethod
    def generate_inquiry_link(
        cls,
        car_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        availability_info: Optional[str] = None,
        customer_name: Optional[str] = None,
    ) -> str:
        """
        Generate a WhatsApp link with a pre-filled inquiry message.

        Args:
            car_name: Name of the car
            start_date: Optional rental start date
            end_date: Optional rental end date
            availability_info: Optional availability status text
            customer_name: Optional customer name

        Returns:
            WhatsApp URL with pre-filled message
        """
        phone = cls.get_whatsapp_number()
        if not phone:
            return "#"

        message = cls.generate_inquiry_message(
            car_name=car_name,
            start_date=start_date,
            end_date=end_date,
            availability_info=availability_info,
            customer_name=customer_name,
        )

        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{phone}?text={encoded_message}"

    @classmethod
    def generate_inquiry_message(
        cls,
        car_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        availability_info: Optional[str] = None,
        customer_name: Optional[str] = None,
    ) -> str:
        """Generate the inquiry message text."""
        site_settings = SiteSettings.load()
        site_name = site_settings.site_name or "Rental Cars Morocco"

        if customer_name:
            greeting = f"Bonjour, je m'appelle {customer_name}."
        else:
            greeting = "Bonjour,"

        message_parts = [greeting]
        message_parts.append(f"Je suis intéressé(e) par la location de la {car_name}.")

        if start_date and end_date:
            date_range = f"du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
            message_parts.append(f"Je souhaite louer cette voiture {date_range}.")
        elif start_date:
            message_parts.append(f"Je souhaite louer cette voiture à partir du {start_date.strftime('%d/%m/%Y')}.")

        if availability_info:
            message_parts.append(f"{availability_info}")

        message_parts.append("Est-ce que cette voiture est disponible ?")
        message_parts.append(f"Merci, {site_name}!")

        return "\n\n".join(message_parts)

    @classmethod
    def generate_general_inquiry_link(
        cls,
        message: Optional[str] = None,
        customer_name: Optional[str] = None,
    ) -> str:
        """Generate a WhatsApp link for general inquiries."""
        phone = cls.get_whatsapp_number()
        if not phone:
            return "#"

        site_settings = SiteSettings.load()
        site_name = site_settings.site_name or "Rental Cars Morocco"

        if message:
            full_message = message
        else:
            if customer_name:
                greeting = f"Bonjour, je m'appelle {customer_name}."
            else:
                greeting = "Bonjour,"
            full_message = f"{greeting}\n\nJe souhaite avoir plus d'informations sur vos services de location de voitures.\n\nMerci!"

        encoded_message = urllib.parse.quote(full_message)
        return f"https://wa.me/{phone}?text={encoded_message}"
