from urllib.parse import urlencode

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from applications.bookings.models import Booking, ExtraService


class BookingAvailabilityForm(forms.Form):
    check_in = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Llegada")
    check_out = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Salida")
    guests = forms.IntegerField(min_value=1, label="Huéspedes")

    def __init__(self, *args, property, **kwargs):
        self.property = property
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        guests = cleaned.get("guests")
        today = timezone.localdate()
        if check_in and check_in < today:
            self.add_error("check_in", "La llegada no puede estar en el pasado.")
        if check_out and check_out < today:
            self.add_error("check_out", "La salida no puede estar en el pasado.")
        if check_in and check_out and check_in >= check_out:
            self.add_error("check_out", "La salida debe ser posterior a la llegada.")
        if guests and guests > self.property.capacity:
            self.add_error("guests", "Esta propiedad no admite tantos huéspedes.")
        if check_in and check_out:
            overlap = Booking.objects.filter(
                property=self.property,
                status__in=["pending", "confirmed"],
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if overlap:
                raise ValidationError("La propiedad no está disponible para esas fechas.")
        return cleaned

    def cleaned_query_params(self):
        return urlencode(
            {
                "check_in": self.cleaned_data["check_in"].isoformat(),
                "check_out": self.cleaned_data["check_out"].isoformat(),
                "guests": self.cleaned_data["guests"],
            }
        )


class CheckoutForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    full_name = forms.CharField(max_length=150, label="Nombre completo")
    phone = forms.CharField(max_length=30, required=False, label="Teléfono")
    nationality = forms.CharField(max_length=80, required=False, label="Nacionalidad")
    password1 = forms.CharField(widget=forms.PasswordInput, required=False, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirmar contraseña")
    services = forms.ModelMultipleChoiceField(
        queryset=ExtraService.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Servicios adicionales",
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["email"].initial = user.email
            self.fields["full_name"].initial = user.get_full_name() or user.email
            self.fields["password1"].required = False
            self.fields["password2"].required = False
            self.fields["password1"].widget = forms.HiddenInput()
            self.fields["password2"].widget = forms.HiddenInput()
            self.fields["email"].disabled = True

    def clean(self):
        cleaned = super().clean()
        if not (self.user and self.user.is_authenticated):
            password1 = cleaned.get("password1")
            password2 = cleaned.get("password2")
            if not password1:
                self.add_error("password1", "Ingresa una contraseña.")
            if password1 != password2:
                self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned


class FlexibleCheckinForm(forms.Form):
    arrival_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        label="Hora estimada de llegada",
    )
    departure_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        required=False,
        label="Hora ideal de salida",
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
        label="Notas para el equipo",
    )


class TransportServiceForm(forms.Form):
    TRANSFER_CHOICES = (
        ("airport_property", "Aeropuerto a propiedad"),
        ("property_airport", "Propiedad a aeropuerto"),
        ("round_trip", "Ida y vuelta"),
    )

    transfer_type = forms.ChoiceField(choices=TRANSFER_CHOICES, label="Tipo de traslado")
    flight_number = forms.CharField(max_length=30, required=False, label="Número de vuelo")
    pickup_address = forms.CharField(max_length=180, label="Dirección de recogida")
    passengers = forms.IntegerField(min_value=1, max_value=8, label="Pasajeros")
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
        label="Notas para el conductor",
    )
