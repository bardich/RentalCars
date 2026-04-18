"""Booking services and availability logic."""

from datetime import date, timedelta
from typing import List, Optional, Tuple
from django.db.models import Q
from apps.fleet.models import RentalCar
from .models import Booking


class AvailabilityService:
    """Service for checking and managing car availability."""

    @staticmethod
    def get_unavailable_dates(car: RentalCar) -> List[date]:
        """Get all dates when car is unavailable (booked or in maintenance)."""
        unavailable_dates = []

        # Get active bookings
        bookings = Booking.objects.filter(
            car=car,
            booking_status__in=['pending', 'confirmed'],
        )

        for booking in bookings:
            current_date = booking.start_date
            while current_date <= booking.end_date:
                unavailable_dates.append(current_date)
                current_date += timedelta(days=1)

        return unavailable_dates

    @staticmethod
    def is_available(car: RentalCar, start_date: date, end_date: date) -> bool:
        """Check if car is available for a date range."""
        if car.availability_status == 'maintenance':
            return False

        if car.available_from and start_date < car.available_from:
            return False

        overlapping_bookings = Booking.objects.filter(
            car=car,
            booking_status__in=['pending', 'confirmed'],
            start_date__lte=end_date,
            end_date__gte=start_date,
        ).exists()

        return not overlapping_bookings

    @staticmethod
    def get_next_available_date(car: RentalCar, from_date: Optional[date] = None) -> Optional[date]:
        """Get the next available date for a car."""
        if from_date is None:
            from_date = date.today()

        # Check if car is in maintenance
        if car.availability_status == 'maintenance':
            return None

        # Check available_from date
        if car.available_from and from_date < car.available_from:
            from_date = car.available_from

        # Check for 90 days ahead
        check_date = from_date
        end_check = from_date + timedelta(days=90)

        while check_date <= end_check:
            if AvailabilityService.is_available(car, check_date, check_date):
                return check_date
            check_date += timedelta(days=1)

        return None

    @staticmethod
    def find_available_cars(start_date: date, end_date: date, category_id: Optional[int] = None) -> List[RentalCar]:
        """Find all available cars for a date range."""
        cars = RentalCar.objects.filter(active=True)

        if category_id:
            cars = cars.filter(category_id=category_id)

        available_cars = []
        for car in cars:
            if AvailabilityService.is_available(car, start_date, end_date):
                available_cars.append(car)

        return available_cars


class BookingService:
    """Service for managing bookings."""

    @staticmethod
    def create_booking(car: RentalCar, customer_data: dict, start_date: date, end_date: date) -> Tuple[Optional[Booking], str]:
        """Create a new booking if car is available."""
        if not AvailabilityService.is_available(car, start_date, end_date):
            return None, "Le véhicule n'est pas disponible pour ces dates."

        total_days = (end_date - start_date).days + 1
        total_price = car.daily_price * total_days

        booking = Booking.objects.create(
            car=car,
            customer_name=customer_data.get('name'),
            customer_phone=customer_data.get('phone'),
            customer_email=customer_data.get('email', ''),
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            total_price=total_price,
            booking_status='pending',
            notes=customer_data.get('notes', ''),
        )

        # Update car status if needed
        if car.availability_status == 'available':
            car.availability_status = 'reserved'
            car.save(update_fields=['availability_status'])

        return booking, "Réservation créée avec succès."

    @staticmethod
    def confirm_booking(booking: Booking) -> bool:
        """Confirm a pending booking."""
        if booking.booking_status == 'pending':
            booking.booking_status = 'confirmed'
            booking.save(update_fields=['booking_status'])

            # Update car status
            car = booking.car
            car.availability_status = 'rented'
            car.save(update_fields=['availability_status'])
            return True
        return False

    @staticmethod
    def cancel_booking(booking: Booking, reason: str = '') -> bool:
        """Cancel a booking."""
        if booking.booking_status in ['pending', 'confirmed']:
            booking.booking_status = 'cancelled'
            if reason:
                booking.notes = f"{booking.notes}\nRaison d'annulation: {reason}".strip()
            booking.save(update_fields=['booking_status', 'notes'])

            # Update car status back to available
            car = booking.car
            car.availability_status = 'available'
            car.save(update_fields=['availability_status'])
            return True
        return False

    @staticmethod
    def complete_booking(booking: Booking) -> bool:
        """Mark a booking as completed."""
        if booking.booking_status == 'confirmed':
            booking.booking_status = 'completed'
            booking.save(update_fields=['booking_status'])

            # Update car status back to available
            car = booking.car
            car.availability_status = 'available'
            car.save(update_fields=['availability_status'])
            return True
        return False

    @staticmethod
    def get_upcoming_returns(days: int = 7) -> List[Booking]:
        """Get bookings ending in the next X days."""
        today = date.today()
        end_date = today + timedelta(days=days)

        return Booking.objects.filter(
            booking_status='confirmed',
            end_date__gte=today,
            end_date__lte=end_date,
        ).select_related('car').order_by('end_date')
