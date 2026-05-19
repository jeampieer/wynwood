from django import forms
from django.utils import timezone

from applications.properties.models import City


class SearchForm(forms.Form):
    city = forms.ModelChoiceField(
        queryset=City.objects.filter(is_active=True),
        required=False,
        empty_label="Ciudad de destino",
        label="Ciudad",
    )
    check_in = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Llegada")
    check_out = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Salida")
    guests = forms.IntegerField(min_value=1, required=False, label="Huéspedes")

    def __init__(self, *args, language="es", **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate().isoformat()
        self.fields["check_in"].widget.attrs["min"] = today
        self.fields["check_out"].widget.attrs["min"] = today
        if language == "en":
            self.fields["city"].empty_label = "Destination city"
            self.fields["city"].label = "City"
            self.fields["check_in"].label = "Arrival"
            self.fields["check_out"].label = "Departure"
            self.fields["guests"].label = "Guests"
            self.fields["guests"].widget.attrs["placeholder"] = "Guests"
        else:
            self.fields["guests"].widget.attrs["placeholder"] = "Huéspedes"

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        today = timezone.localdate()
        if check_in and check_in < today:
            self.add_error("check_in", "La fecha de llegada no puede estar en el pasado.")
        if check_out and check_out < today:
            self.add_error("check_out", "La fecha de salida no puede estar en el pasado.")
        if check_in and check_out and check_in >= check_out:
            self.add_error("check_out", "La salida debe ser posterior a la llegada.")
        return cleaned
