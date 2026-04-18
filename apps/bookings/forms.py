"""Booking forms."""

from datetime import date
from django import forms
from .models import Booking
from .services import AvailabilityService


class BookingForm(forms.ModelForm):
    """Form for creating a new booking."""

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'input-field',
            'min': date.today().isoformat(),
        }),
        label='Date de début',
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'input-field',
            'min': date.today().isoformat(),
        }),
        label='Date de fin',
    )

    class Meta:
        model = Booking
        fields = ['customer_name', 'customer_phone', 'customer_email', 'start_date', 'end_date', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Votre nom complet'}),
            'customer_phone': forms.TextInput(attrs={'class': 'input-field', 'placeholder': '+212 6XX XXX XXX'}),
            'customer_email': forms.EmailInput(attrs={'class': 'input-field', 'placeholder': 'votre@email.com'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Demandes spéciales...'}),
        }
        labels = {
            'customer_name': 'Nom complet',
            'customer_phone': 'Téléphone',
            'customer_email': 'Email (optionnel)',
            'notes': 'Notes / Commentaires',
        }

    def __init__(self, *args, car=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.car = car

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date < date.today():
                self.add_error('start_date', 'La date de début ne peut pas être dans le passé.')

            if end_date < start_date:
                self.add_error('end_date', 'La date de fin doit être après la date de début.')

            # Check availability
            if self.car and not AvailabilityService.is_available(self.car, start_date, end_date):
                raise forms.ValidationError(
                    'Ce véhicule n\'est pas disponible pour les dates sélectionnées. '
                    'Veuillez choisir d\'autres dates.'
                )

        return cleaned_data


class BookingSearchForm(forms.Form):
    """Form for searching available cars by date."""

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'input-field',
            'min': date.today().isoformat(),
        }),
        label='Date de début',
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'input-field',
            'min': date.today().isoformat(),
        }),
        label='Date de fin',
    )
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='Toutes les catégories',
        widget=forms.Select(attrs={'class': 'input-field'}),
        label='Catégorie',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.fleet.models import Category
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                self.add_error('end_date', 'La date de fin doit être après la date de début.')

        return cleaned_data


class BookingStatusForm(forms.ModelForm):
    """Form for updating booking status (admin use)."""

    class Meta:
        model = Booking
        fields = ['booking_status', 'notes']
        widgets = {
            'booking_status': forms.Select(attrs={'class': 'input-field'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
        }
