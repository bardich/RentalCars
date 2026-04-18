"""Fleet views."""

from django.shortcuts import render, get_object_or_404
from .models import RentalCar, Category, Brand


def car_list(request):
    """List all available cars with filtering."""
    cars = RentalCar.objects.filter(active=True).select_related('brand', 'category').prefetch_related('images')

    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        cars = cars.filter(category__slug=category_slug)

    # Filter by brand
    brand_slug = request.GET.get('brand')
    if brand_slug:
        cars = cars.filter(brand__slug=brand_slug)

    # Filter by transmission
    transmission = request.GET.get('transmission')
    if transmission:
        cars = cars.filter(transmission=transmission)

    # Filter by fuel type
    fuel = request.GET.get('fuel')
    if fuel:
        cars = cars.filter(fuel_type=fuel)

    # Filter by search query
    query = request.GET.get('q')
    if query:
        cars = cars.filter(title__icontains=query)

    # Sorting
    sort = request.GET.get('sort', '-featured')
    if sort == 'price_asc':
        cars = cars.order_by('daily_price')
    elif sort == 'price_desc':
        cars = cars.order_by('-daily_price')
    elif sort == 'newest':
        cars = cars.order_by('-year', '-created_at')
    else:
        cars = cars.order_by('-featured', '-created_at')

    context = {
        'cars': cars,
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.all(),
        'total_cars': cars.count(),
    }
    return render(request, 'fleet/car_list.html', context)


def car_detail(request, slug):
    """Show car details."""
    car = get_object_or_404(
        RentalCar.objects.select_related('brand', 'category')
        .prefetch_related('images', 'features'),
        slug=slug,
        active=True
    )

    # Get similar cars
    similar_cars = RentalCar.objects.filter(
        category=car.category,
        active=True
    ).exclude(id=car.id)[:3]

    context = {
        'car': car,
        'similar_cars': similar_cars,
        'main_image': car.main_image,
    }
    return render(request, 'fleet/car_detail.html', context)
