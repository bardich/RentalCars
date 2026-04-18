"""Core views."""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from apps.fleet.models import RentalCar, Category


def home(request):
    """Homepage view with featured cars and categories."""
    featured_cars = RentalCar.objects.filter(active=True, featured=True)[:6]
    available_cars = RentalCar.objects.filter(active=True, availability_status='available')[:6]
    categories = Category.objects.filter(is_active=True)

    context = {
        'featured_cars': featured_cars,
        'available_cars': available_cars,
        'categories': categories,
    }
    return render(request, 'pages/home.html', context)


def contact(request):
    """Contact page with form and WhatsApp integration."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Store in session for potential booking
        request.session['contact_info'] = {
            'name': name,
            'email': email,
            'phone': phone,
        }

        # Send email notification if configured
        if settings.DEFAULT_FROM_EMAIL and email:
            try:
                send_mail(
                    f'Contact: {subject}',
                    f'From: {name} ({email})\nPhone: {phone}\n\n{message}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
                messages.success(request, 'Votre message a été envoyé avec succès. Nous vous répondrons bientôt!')
            except Exception:
                messages.warning(request, 'Message enregistré mais notification email non envoyée.')
        else:
            messages.success(request, 'Votre message a été enregistré. Nous vous contacterons bientôt!')

        return redirect('contact')

    return render(request, 'pages/contact.html')


def about(request):
    """About page."""
    stats = {
        'cars_count': RentalCar.objects.filter(active=True).count(),
        'categories_count': Category.objects.filter(is_active=True).count(),
    }
    return render(request, 'pages/about.html', {'stats': stats})


def faq(request):
    """FAQ page."""
    faqs = [
        {
            'question': 'Quels documents sont nécessaires pour louer une voiture ?',
            'answer': 'Permis de conduire valide, passeport ou carte nationale d\'identité, et une carte de crédit pour la caution.'
        },
        {
            'question': 'Quel est le dépôt de garantie ?',
            'answer': 'Le dépôt de garantie varie selon le véhicule, généralement entre 3 000 et 10 000 MAD. Il est restitué après retour du véhicule en bon état.'
        },
        {
            'question': 'Puis-je annuler ma réservation ?',
            'answer': 'Oui, vous pouvez annuler gratuitement jusqu\'à 48h avant la date de prise en charge. Au-delà, des frais peuvent s\'appliquer.'
        },
        {
            'question': 'Y a-t-il un kilométrage limité ?',
            'answer': 'Oui, le kilométrage inclus est de 200 km/jour. Au-delà, des frais additionnels de 2 MAD/km s\'appliquent.'
        },
        {
            'question': 'Livrez-vous les véhicules ?',
            'answer': 'Oui, nous proposons la livraison à l\'aéroport, à votre hôtel ou à domicile dans la région de Casablanca. Des frais de livraison peuvent s\'appliquer selon la distance.'
        },
        {
            'question': 'Que se passe-t-il en cas d\'accident ?',
            'answer': 'Contactez immédiatement notre assistance 24/7. L\'assurance tous risques est incluse dans nos tarifs avec une franchise selon le véhicule.'
        },
    ]
    return render(request, 'pages/faq.html', {'faqs': faqs})


def terms(request):
    """Terms and conditions page."""
    return render(request, 'pages/terms.html')
