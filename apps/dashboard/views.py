"""Dashboard views for rental management."""
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count, Q, Max, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.fleet.models import RentalCar, Category, Brand, CarFeature, CarImage
from apps.bookings.models import Booking


# Admin required decorator - only superusers can access dashboard
def admin_required(view_func):
    """Decorator to restrict access to admin/superuser only."""
    decorated_view = login_required(
        user_passes_test(lambda u: u.is_superuser, login_url='dashboard:login')(view_func)
    )
    return decorated_view


# ============================================================================
# Dashboard Home
# ============================================================================
@admin_required
def dashboard_home(request):
    """Dashboard home view with statistics."""
    today = date.today()
    month_start = today.replace(day=1)

    # Car statistics
    total_cars = RentalCar.objects.filter(active=True).count()
    available_cars = RentalCar.objects.filter(
        active=True, availability_status='available'
    ).count()
    reserved_cars = RentalCar.objects.filter(
        active=True, availability_status='reserved'
    ).count()
    rented_cars = RentalCar.objects.filter(
        active=True, availability_status='rented'
    ).count()
    maintenance_cars = RentalCar.objects.filter(
        active=True, availability_status='maintenance'
    ).count()

    # Booking statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(booking_status='pending').count()
    confirmed_bookings = Booking.objects.filter(booking_status='confirmed').count()
    completed_bookings = Booking.objects.filter(booking_status='completed').count()
    cancelled_bookings = Booking.objects.filter(booking_status='cancelled').count()

    # Upcoming returns (bookings ending in next 7 days)
    upcoming_returns = Booking.objects.filter(
        booking_status__in=['confirmed', 'rented'],
        end_date__gte=today,
        end_date__lte=today + timedelta(days=7)
    ).select_related('car').order_by('end_date')

    # Recent bookings
    recent_bookings = Booking.objects.select_related('car').order_by('-created_at')[:10]

    # Revenue statistics
    monthly_revenue = Booking.objects.filter(
        booking_status__in=['confirmed', 'completed'],
        start_date__gte=month_start
    ).aggregate(total=Sum('total_price'))['total'] or 0

    total_revenue = Booking.objects.filter(
        booking_status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Active bookings count
    active_bookings = Booking.objects.filter(
        booking_status__in=['pending', 'confirmed']
    ).count()

    context = {
        # Car stats
        'total_cars': total_cars,
        'available_cars': available_cars,
        'reserved_cars': reserved_cars,
        'rented_cars': rented_cars,
        'maintenance_cars': maintenance_cars,

        # Booking stats
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'active_bookings': active_bookings,

        # Revenue
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,

        # Lists
        'upcoming_returns': upcoming_returns,
        'recent_bookings': recent_bookings,
        'today': today,
    }
    return render(request, 'dashboard/dashboard.html', context)


@admin_required
def booking_list(request):
    """List all bookings."""
    status = request.GET.get('status', '')
    bookings = Booking.objects.select_related('car').order_by('-created_at')

    if status:
        bookings = bookings.filter(booking_status=status)

    paginator = Paginator(bookings, 20)
    page = request.GET.get('page', 1)
    bookings_page = paginator.get_page(page)

    context = {
        'bookings': bookings_page,
        'current_status': status,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'dashboard/booking_list.html', context)


@admin_required
def booking_detail(request, pk):
    """View booking details with status actions."""
    booking = get_object_or_404(
        Booking.objects.select_related('car'),
        pk=pk
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirm':
            booking.booking_status = 'confirmed'
            booking.save()
            # Update car status
            car = booking.car
            car.availability_status = 'reserved'
            car.save()
            messages.success(request, f'Réservation #{booking.id} confirmée!')

        elif action == 'cancel':
            booking.booking_status = 'cancelled'
            booking.save()
            # Free up the car
            car = booking.car
            car.availability_status = 'available'
            car.save()
            messages.success(request, f'Réservation #{booking.id} annulée!')

        elif action == 'complete':
            booking.booking_status = 'completed'
            booking.save()
            # Free up the car
            car = booking.car
            car.availability_status = 'available'
            car.save()
            messages.success(request, f'Réservation #{booking.id} marquée comme terminée!')

        elif action == 'mark_rented':
            booking.booking_status = 'rented'
            booking.save()
            car = booking.car
            car.availability_status = 'rented'
            car.save()
            messages.success(request, f'Voiture marquée comme louée!')

        elif action == 'update':
            # Update customer info
            booking.customer_name = request.POST.get('customer_name')
            booking.customer_email = request.POST.get('customer_email', '')
            booking.customer_phone = request.POST.get('customer_phone', '')
            booking.message = request.POST.get('message', '')

            # Update dates
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            if start_date_str and end_date_str:
                from datetime import datetime
                start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                booking.start_date = start
                booking.end_date = end
                booking.days = (end - start).days + 1

            # Update car if changed
            car_id = request.POST.get('car')
            if car_id and int(car_id) != booking.car_id:
                old_car = booking.car
                new_car = get_object_or_404(RentalCar, pk=car_id)
                booking.car = new_car
                # Recalculate price
                if booking.days >= 30 and new_car.monthly_price:
                    booking.daily_price = new_car.monthly_price / 30
                elif booking.days >= 7 and new_car.weekly_price:
                    booking.daily_price = new_car.weekly_price / 7
                else:
                    booking.daily_price = new_car.daily_price
                booking.total_price = booking.daily_price * booking.days
                # Update old car status
                old_car.availability_status = 'available'
                old_car.save()
                # Update new car status
                if booking.booking_status in ['confirmed', 'rented']:
                    new_car.availability_status = 'reserved' if booking.booking_status == 'confirmed' else 'rented'
                    new_car.save()
            else:
                # Just recalculate price with current car
                car = booking.car
                if booking.days >= 30 and car.monthly_price:
                    booking.daily_price = car.monthly_price / 30
                elif booking.days >= 7 and car.weekly_price:
                    booking.daily_price = car.weekly_price / 7
                else:
                    booking.daily_price = car.daily_price
                booking.total_price = booking.daily_price * booking.days

            # Update status if changed
            new_status = request.POST.get('booking_status')
            if new_status and new_status != booking.booking_status:
                old_status = booking.booking_status
                booking.booking_status = new_status
                # Update car status based on new booking status
                car = booking.car
                if new_status == 'confirmed':
                    car.availability_status = 'reserved'
                elif new_status == 'rented':
                    car.availability_status = 'rented'
                elif new_status in ['completed', 'cancelled']:
                    car.availability_status = 'available'
                elif new_status == 'pending':
                    car.availability_status = 'available'
                car.save()

            booking.save()
            messages.success(request, 'Réservation mise à jour!')

        return redirect('dashboard:booking_detail', pk=booking.pk)

    cars = RentalCar.objects.filter(active=True)
    context = {
        'booking': booking,
        'cars': cars,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'dashboard/booking_detail.html', context)


@admin_required
def booking_create(request):
    """Create manual booking/reservation."""
    cars = RentalCar.objects.filter(active=True, availability_status='available')

    if request.method == 'POST':
        car_id = request.POST.get('car')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email', '')
        customer_phone = request.POST.get('customer_phone', '')
        message = request.POST.get('message', '')

        car = get_object_or_404(RentalCar, pk=car_id)

        # Calculate days and price
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        days = (end - start).days + 1

        # Calculate price
        if days >= 30 and car.monthly_price:
            daily_price = car.monthly_price / 30
        elif days >= 7 and car.weekly_price:
            daily_price = car.weekly_price / 7
        else:
            daily_price = car.daily_price

        total_price = daily_price * days

        # Create booking
        booking = Booking.objects.create(
            car=car,
            start_date=start,
            end_date=end,
            days=days,
            daily_price=daily_price,
            total_price=total_price,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            message=message,
            booking_status='confirmed',
            pickup_location='',
        )

        # Update car status
        car.availability_status = 'reserved'
        car.save()

        messages.success(request, f'Réservation #{booking.id} créée avec succès!')
        return redirect('dashboard:booking_detail', pk=booking.pk)

    context = {
        'cars': cars,
    }
    return render(request, 'dashboard/booking_form.html', context)


# ============================================================================
# Fleet Management - Cars
# ============================================================================
@admin_required
def car_list(request):
    """List all cars for management."""
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    cars = RentalCar.objects.select_related('category', 'brand').prefetch_related('images')

    if status:
        cars = cars.filter(availability_status=status)
    if category:
        cars = cars.filter(category_id=category)

    paginator = Paginator(cars.order_by('-created_at'), 20)
    page = request.GET.get('page', 1)
    cars_page = paginator.get_page(page)

    context = {
        'cars': cars_page,
        'current_status': status,
        'current_category': category,
        'categories': Category.objects.filter(is_active=True),
        'status_choices': RentalCar.STATUS_CHOICES,
    }
    return render(request, 'dashboard/car_list.html', context)


@admin_required
def car_detail(request, pk):
    """View and manage car details."""
    car = get_object_or_404(
        RentalCar.objects.select_related('category', 'brand').prefetch_related('images', 'features'),
        pk=pk
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'toggle_featured':
            car.featured = not car.featured
            car.save()
            messages.success(request, f'Voiture "{car.title}" mise en vedette: {car.featured}')

        elif action == 'update_status':
            new_status = request.POST.get('availability_status')
            if new_status in dict(RentalCar.STATUS_CHOICES):
                car.availability_status = new_status
                car.save()
                messages.success(request, f'Statut mis à jour: {car.get_availability_status_display()}')

        elif action == 'set_available_from':
            available_from = request.POST.get('available_from')
            car.available_from = available_from or None
            car.save()
            messages.success(request, 'Date de disponibilité mise à jour')

        return redirect('dashboard:car_detail', pk=car.pk)

    context = {
        'car': car,
        'status_choices': RentalCar.STATUS_CHOICES,
    }
    return render(request, 'dashboard/car_detail.html', context)


@admin_required
def car_create(request):
    """Create new car."""
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.all()
    features = CarFeature.objects.filter(is_active=True)

    if request.method == 'POST':
        # Basic car info
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        year = request.POST.get('year')
        seats = request.POST.get('seats')
        transmission = request.POST.get('transmission')
        fuel_type = request.POST.get('fuel_type')
        daily_price = request.POST.get('daily_price')
        weekly_price = request.POST.get('weekly_price')
        monthly_price = request.POST.get('monthly_price')
        description = request.POST.get('description')
        featured = request.POST.get('featured') == 'on'

        # Create car
        car = RentalCar.objects.create(
            title=title,
            category_id=category_id,
            brand_id=brand_id or None,
            year=year or None,
            seats=seats or 5,
            transmission=transmission or 'automatic',
            fuel_type=fuel_type or 'petrol',
            daily_price=daily_price or 0,
            weekly_price=weekly_price or None,
            monthly_price=monthly_price or None,
            description=description or '',
            featured=featured,
            availability_status='available',
            active=True,
        )

        # Add features
        feature_ids = request.POST.getlist('features')
        if feature_ids:
            car.features.set(feature_ids)

        # Handle main image
        if request.FILES.get('main_image'):
            car.main_image = request.FILES['main_image']
            car.save()

        # Handle additional images
        images = request.FILES.getlist('images')
        for i, image in enumerate(images):
            CarImage.objects.create(car=car, image=image, order=i)

        messages.success(request, f'Voiture "{car.title}" créée avec succès!')
        return redirect('dashboard:car_detail', pk=car.pk)

    context = {
        'categories': categories,
        'brands': brands,
        'features': features,
        'transmission_choices': RentalCar.TRANSMISSION_CHOICES,
        'fuel_choices': RentalCar.FUEL_CHOICES,
    }
    return render(request, 'dashboard/car_form.html', context)


@admin_required
def car_edit(request, pk):
    """Edit existing car."""
    car = get_object_or_404(RentalCar, pk=pk)
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.all()
    features = CarFeature.objects.filter(is_active=True)

    if request.method == 'POST':
        # Update basic info
        car.title = request.POST.get('title')
        car.category_id = request.POST.get('category')
        car.brand_id = request.POST.get('brand') or None
        car.year = request.POST.get('year') or None
        car.seats = request.POST.get('seats') or 5
        car.transmission = request.POST.get('transmission') or 'automatic'
        car.fuel_type = request.POST.get('fuel_type') or 'petrol'
        car.daily_price = request.POST.get('daily_price') or 0
        car.weekly_price = request.POST.get('weekly_price') or None
        car.monthly_price = request.POST.get('monthly_price') or None
        car.description = request.POST.get('description') or ''
        car.featured = request.POST.get('featured') == 'on'
        car.active = request.POST.get('active') == 'on'

        # Handle main image
        if request.FILES.get('main_image'):
            car.main_image = request.FILES['main_image']

        car.save()

        # Update features
        feature_ids = request.POST.getlist('features')
        car.features.set(feature_ids)

        messages.success(request, f'Voiture "{car.title}" mise à jour!')
        return redirect('dashboard:car_detail', pk=car.pk)

    context = {
        'car': car,
        'categories': categories,
        'brands': brands,
        'features': features,
        'transmission_choices': RentalCar.TRANSMISSION_CHOICES,
        'fuel_choices': RentalCar.FUEL_CHOICES,
    }
    return render(request, 'dashboard/car_form.html', context)


@admin_required
def car_delete(request, pk):
    """Delete car."""
    car = get_object_or_404(RentalCar, pk=pk)

    if request.method == 'POST':
        title = car.title
        car.delete()
        messages.success(request, f'Voiture "{title}" supprimée!')
        return redirect('dashboard:car_list')

    return render(request, 'dashboard/car_delete.html', {'car': car})


# ============================================================================
# Fleet Management - Car Images
# ============================================================================
@admin_required
def car_image_upload(request, car_pk):
    """Upload additional images for a car."""
    car = get_object_or_404(RentalCar, pk=car_pk)
    images = request.FILES.getlist('images')

    # Get max order
    max_order = car.images.aggregate(Max('order'))['order__max'] or 0

    for i, image in enumerate(images):
        CarImage.objects.create(car=car, image=image, order=max_order + i + 1)

    messages.success(request, f'{len(images)} image(s) ajoutée(s)!')
    return redirect('dashboard:car_detail', pk=car.pk)


@admin_required
def car_image_delete(request, image_pk):
    """Delete a car image."""
    image = get_object_or_404(CarImage, pk=image_pk)
    car_pk = image.car.pk
    image.delete()
    messages.success(request, 'Image supprimée!')
    return redirect('dashboard:car_detail', pk=car_pk)


@admin_required
def car_image_reorder(request):
    """Reorder car images via AJAX."""
    data = request.POST
    image_id = data.get('image_id')
    new_order = int(data.get('new_order', 0))

    image = get_object_or_404(CarImage, pk=image_id)
    car = image.car

    # Update orders
    if new_order < image.order:
        # Moving up
        car.images.filter(order__gte=new_order, order__lt=image.order).update(order=F('order') + 1)
    else:
        # Moving down
        car.images.filter(order__gt=image.order, order__lte=new_order).update(order=F('order') - 1)

    image.order = new_order
    image.save()

    return JsonResponse({'success': True})


# ============================================================================
# Category Management
# ============================================================================
@admin_required
def category_list(request):
    """List all categories."""
    categories = Category.objects.all().order_by('order', 'name')
    return render(request, 'dashboard/category_list.html', {'categories': categories})


@admin_required
def category_create(request):
    """Create new category."""
    if request.method == 'POST':
        Category.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            order=int(request.POST.get('order', 0)),
            is_active=request.POST.get('is_active') == 'on',
        )
        messages.success(request, 'Catégorie créée!')
        return redirect('dashboard:category_list')
    return render(request, 'dashboard/category_form.html')


@admin_required
def category_edit(request, pk):
    """Edit category."""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.order = int(request.POST.get('order', 0))
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        messages.success(request, 'Catégorie mise à jour!')
        return redirect('dashboard:category_list')

    return render(request, 'dashboard/category_form.html', {'category': category})


@admin_required
def category_delete(request, pk):
    """Delete category."""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        # Check if category has cars
        if category.rentalcars.exists():
            messages.error(request, 'Impossible de supprimer: cette catégorie contient des voitures')
            return redirect('dashboard:category_list')

        category.delete()
        messages.success(request, 'Catégorie supprimée!')
        return redirect('dashboard:category_list')

    return render(request, 'dashboard/category_delete.html', {'category': category})


# ============================================================================
# Brand Management
# ============================================================================
@admin_required
def brand_list(request):
    """List all brands."""
    brands = Brand.objects.all().order_by('name')
    return render(request, 'dashboard/brand_list.html', {'brands': brands})


@admin_required
def brand_create(request):
    """Create new brand."""
    if request.method == 'POST':
        Brand.objects.create(name=request.POST.get('name'))
        messages.success(request, 'Marque créée!')
        return redirect('dashboard:brand_list')
    return render(request, 'dashboard/brand_form.html')


@admin_required
def brand_edit(request, pk):
    """Edit brand."""
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == 'POST':
        brand.name = request.POST.get('name')
        brand.save()
        messages.success(request, 'Marque mise à jour!')
        return redirect('dashboard:brand_list')

    return render(request, 'dashboard/brand_form.html', {'brand': brand})


def admin_login(request):
    """Custom admin login that redirects superusers to dashboard."""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('dashboard:home')
        else:
            return redirect('home')
    return auth_views.LoginView.as_view(template_name='dashboard/login.html')(request)


@admin_required
def brand_delete(request, pk):
    """Delete brand."""
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == 'POST':
        # Check if brand has cars
        if brand.rentalcars.exists():
            messages.error(request, 'Impossible de supprimer: cette marque contient des voitures')
            return redirect('dashboard:brand_list')

        brand.delete()
        messages.success(request, 'Marque supprimée!')
        return redirect('dashboard:brand_list')

    return render(request, 'dashboard/brand_delete.html', {'brand': brand})
