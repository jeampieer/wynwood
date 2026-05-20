from urllib.parse import urlencode

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from applications.bookings.models import Booking, ExtraService


class BookingAvailabilityForm(forms.Form):
    check_in = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "data-date-start": ""}), label="Llegada")
    check_out = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "data-date-end": ""}), label="Salida")
    guests = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"data-guest-count": "", "min": "1"}),
        label="Huéspedes",
    )

    def __init__(self, *args, property, language="es", **kwargs):
        self.property = property
        self.language = language
        super().__init__(*args, **kwargs)
        today = timezone.localdate().isoformat()
        self.fields["check_in"].widget.attrs["min"] = today
        self.fields["check_out"].widget.attrs["min"] = today
        if language == "en":
            self.fields["check_in"].label = "Arrival"
            self.fields["check_out"].label = "Departure"
            self.fields["guests"].label = "Guests"

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        guests = cleaned.get("guests")
        today = timezone.localdate()
        messages = {
            "past_check_in": {
                "es": "La llegada no puede estar en el pasado.",
                "en": "Arrival cannot be in the past.",
            },
            "past_check_out": {
                "es": "La salida no puede estar en el pasado.",
                "en": "Departure cannot be in the past.",
            },
            "order": {
                "es": "La salida debe ser posterior a la llegada.",
                "en": "Departure must be after arrival.",
            },
            "capacity": {
                "es": "Esta propiedad no admite tantos huéspedes.",
                "en": "This property does not allow that many guests.",
            },
            "unavailable": {
                "es": "La propiedad no está disponible para esas fechas.",
                "en": "The property is not available for those dates.",
            },
        }
        language = self.language if self.language in {"es", "en"} else "es"
        if check_in and check_in < today:
            self.add_error("check_in", messages["past_check_in"][language])
        if check_out and check_out < today:
            self.add_error("check_out", messages["past_check_out"][language])
        if check_in and check_out and check_in >= check_out:
            self.add_error("check_out", messages["order"][language])
        if guests and guests > self.property.capacity:
            self.add_error("guests", messages["capacity"][language])
        if check_in and check_out:
            overlap = Booking.objects.filter(
                property=self.property,
                status__in=["pending", "confirmed"],
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if overlap:
                raise ValidationError(messages["unavailable"][language])
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

    def __init__(self, *args, user=None, language="es", **kwargs):
        self.user = user
        self.language = language
        super().__init__(*args, **kwargs)
        if language == "en":
            self.fields["email"].label = "Email"
            self.fields["full_name"].label = "Full name"
            self.fields["phone"].label = "Phone"
            self.fields["nationality"].label = "Nationality"
            self.fields["password1"].label = "Password"
            self.fields["password2"].label = "Confirm password"
            self.fields["services"].label = "Additional services"
        self.fields["email"].widget.attrs.update(
            {
                "autocomplete": "email",
                "inputmode": "email",
            }
        )
        self.fields["full_name"].widget.attrs.update({"autocomplete": "name"})
        self.fields["phone"].widget.attrs.update(
            {
                "autocomplete": "tel",
                "inputmode": "tel",
            }
        )
        self.fields["nationality"].widget.attrs.update({"autocomplete": "country-name"})
        self.fields["password1"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "data-checkout-password": "primary",
                "minlength": "8",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "data-checkout-password": "confirm",
                "minlength": "8",
            }
        )
        if user and user.is_authenticated:
            self.fields["email"].initial = user.email
            self.fields["full_name"].initial = user.get_full_name() or user.email
            self.fields["password1"].required = False
            self.fields["password2"].required = False
            self.fields["password1"].widget = forms.HiddenInput()
            self.fields["password2"].widget = forms.HiddenInput()
            self.fields["email"].disabled = True
        else:
            self.fields["password1"].required = True
            self.fields["password2"].required = True

    def clean(self):
        cleaned = super().clean()
        if not (self.user and self.user.is_authenticated):
            language = self.language if self.language in {"es", "en"} else "es"
            password1 = cleaned.get("password1")
            password2 = cleaned.get("password2")
            if not password1:
                self.add_error(
                    "password1",
                    "Ingresa una contraseña." if language == "es" else "Enter a password.",
                )
            if not password2:
                self.add_error(
                    "password2",
                    "Confirma tu contraseña." if language == "es" else "Confirm your password.",
                )
            elif password1 and password1 != password2:
                self.add_error(
                    "password2",
                    "Las contraseñas no coinciden." if language == "es" else "Passwords do not match.",
                )
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

    def __init__(self, *args, language="es", **kwargs):
        super().__init__(*args, **kwargs)
        if language == "en":
            self.fields["arrival_time"].label = "Estimated arrival time"
            self.fields["departure_time"].label = "Ideal departure time"
            self.fields["notes"].label = "Notes for the team"


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

    def __init__(self, *args, language="es", **kwargs):
        super().__init__(*args, **kwargs)
        if language == "en":
            self.fields["transfer_type"].label = "Transfer type"
            self.fields["transfer_type"].choices = (
                ("airport_property", "Airport to property"),
                ("property_airport", "Property to airport"),
                ("round_trip", "Round trip"),
            )
            self.fields["flight_number"].label = "Flight number"
            self.fields["pickup_address"].label = "Pickup address"
            self.fields["passengers"].label = "Passengers"
            self.fields["notes"].label = "Notes for the driver"
