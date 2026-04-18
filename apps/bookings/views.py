"""Booking views."""

from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.fleet.models import RentalCar
from .models import Booking
from .forms import BookingForm, BookingSearchForm
from .services import AvailabilityService, BookingService


def search_availability(request):
    """Search for available cars by date range."""
    form = BookingSearchForm(request.GET or None)
    available_cars = []
    search_params = {}

    if request.GET and form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        category = form.cleaned_data.get('category')

        search_params = {
            'start_date': start_date,
            'end_date': end_date,
            'category': category,
        }

        available_cars = AvailabilityService.find_available_cars(
            start_date, end_date,
            category_id=category.id if category else None
        )

    context = {
        'form': form,
        'available_cars': available_cars,
        'search_params': search_params,
        'total_results': len(available_cars),
    }
    return render(request, 'bookings/search.html', context)


def create_booking(request, car_id):
    """Create a new booking for a specific car."""
    car = get_object_or_404(RentalCar, id=car_id, active=True)

    # Get dates from query params if provided
    initial_data = {}
    if request.GET.get('start_date'):
        initial_data['start_date'] = request.GET.get('start_date')
    if request.GET.get('end_date'):
        initial_data['end_date'] = request.GET.get('end_date')

    if request.method == 'POST':
        form = BookingForm(request.POST, car=car)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.car = car

            # Calculate totals
            booking.total_days = (booking.end_date - booking.start_date).days + 1
            booking.total_price = car.daily_price * booking.total_days

            booking.save()

            # Update car status
            car.availability_status = 'reserved'
            car.save(update_fields=['availability_status'])

            messages.success(request, 'Votre réservation a été créée avec succès! Nous vous contacterons bientôt.')
            return redirect('bookings:confirmation', booking_id=booking.id)
    else:
        form = BookingForm(initial=initial_data, car=car)

    # Get unavailable dates for calendar
    unavailable_dates = AvailabilityService.get_unavailable_dates(car)

    context = {
        'form': form,
        'car': car,
        'unavailable_dates': unavailable_dates,
        'next_available': AvailabilityService.get_next_available_date(car),
    }
    return render(request, 'bookings/create.html', context)


def booking_confirmation(request, booking_id):
    """Show booking confirmation page."""
    booking = get_object_or_404(Booking, id=booking_id)

    # Generate WhatsApp message
    whatsapp_message = (
        f"Bonjour, je viens de faire une réservation pour {booking.car} "
        f"du {booking.start_date.strftime('%d/%m/%Y')} au {booking.end_date.strftime('%d/%m/%Y')}. "
        f"Réf: #{booking.id}"
    )

    context = {
        'booking': booking,
        'whatsapp_message': whatsapp_message,
    }
    return render(request, 'bookings/confirmation.html', context)


@login_required
def booking_list(request):
    """List all bookings (admin view)."""
    bookings = Booking.objects.select_related('car').order_by('-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(booking_status=status_filter)

    # Filter by upcoming
    if request.GET.get('upcoming'):
        bookings = bookings.filter(
            booking_status__in=['pending', 'confirmed'],
            start_date__gte=date.today(),
        )

    context = {
        'bookings': bookings,
        'total_bookings': bookings.count(),
        'pending_count': Booking.objects.filter(booking_status='pending').count(),
        'confirmed_count': Booking.objects.filter(booking_status='confirmed').count(),
    }
    return render(request, 'dashboard/bookings.html', context)


@login_required
def booking_detail(request, pk):
    """View booking details."""
    booking = get_object_or_404(Booking.objects.select_related('car'), pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            if BookingService.confirm_booking(booking):
                messages.success(request, 'Réservation confirmée.')
            else:
                messages.error(request, 'Impossible de confirmer cette réservation.')
        elif action == 'cancel':
            reason = request.POST.get('reason', '')
            if BookingService.cancel_booking(booking, reason):
                messages.success(request, 'Réservation annulée.')
            else:
                messages.error(request, 'Impossible d\'annuler cette réservation.')
        elif action == 'complete':
            if BookingService.complete_booking(booking):
                messages.success(request, 'Réservation marquée comme terminée.')
            else:
                messages.error(request, 'Impossible de terminer cette réservation.')

        return redirect('dashboard:booking_detail', pk=pk)

    context = {
        'booking': booking,
    }
    return render(request, 'dashboard/booking_detail.html', context)

