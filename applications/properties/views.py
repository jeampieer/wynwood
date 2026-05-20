from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView

from applications.bookings.forms import BookingAvailabilityForm
from applications.properties.forms import SearchForm
from applications.properties.models import Property


class PropertySearchView(ListView):
    model = Property
    template_name = "properties/search.html"
    context_object_name = "properties"

    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True).select_related("city").prefetch_related("images")
        self.form = SearchForm(self.request.GET or None, language=self.request.session.get("site_language", "es"))
        if self.form.is_valid():
            city = self.form.cleaned_data.get("city")
            guests = self.form.cleaned_data.get("guests")
            check_in = self.form.cleaned_data.get("check_in")
            check_out = self.form.cleaned_data.get("check_out")
            if city:
                queryset = queryset.filter(city=city)
            if guests:
                queryset = queryset.filter(capacity__gte=guests)
            if check_in and check_out:
                queryset = queryset.exclude(
                    bookings__status__in=["pending", "confirmed"],
                    bookings__check_in__lt=check_out,
                    bookings__check_out__gt=check_in,
                )
        return queryset.distinct()

    def query_params(self):
        form = getattr(self, "form", None)
        if not form:
            return ""
        form.is_valid()
        cleaned_data = getattr(form, "cleaned_data", {})
        params = {}
        city = cleaned_data.get("city")
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        guests = cleaned_data.get("guests")
        if city:
            params["city"] = city.pk
        if check_in:
            params["check_in"] = check_in.isoformat()
        if check_out:
            params["check_out"] = check_out.isoformat()
        if guests:
            params["guests"] = guests
        return urlencode(params)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.request.session.get("site_language", "es")
        context["form"] = getattr(
            self,
            "form",
            SearchForm(self.request.GET or None, language=language),
        )
        context["query_string"] = self.query_params()
        context["copy"] = {
            "es": {
                "title": "Resultados",
                "search": "Buscar",
                "empty_title": "No encontramos disponibilidad",
                "empty_body": "Prueba con otra ciudad, fecha o número de huéspedes.",
                "map": "Mapa",
                "map_body": "Explora propiedades cerca de los mejores barrios.",
            },
            "en": {
                "title": "Results",
                "search": "Search",
                "empty_title": "No availability found",
                "empty_body": "Try another city, date or number of guests.",
                "map": "Map",
                "map_body": "Explore properties near the best neighborhoods.",
            },
        }.get(language, {})
        return context


class PropertyDetailView(DetailView):
    model = Property
    template_name = "properties/detail.html"
    context_object_name = "property"
    queryset = Property.objects.filter(is_active=True).select_related("city").prefetch_related("amenities", "images")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.request.session.get("site_language", "es")
        initial = {
            "check_in": self.request.GET.get("check_in"),
            "check_out": self.request.GET.get("check_out"),
            "guests": self.request.GET.get("guests") or 2,
        }
        context.setdefault(
            "booking_form",
            BookingAvailabilityForm(property=self.object, data=None, initial=initial, language=language),
        )
        context["copy"] = {
            "es": {
                "guests": "invitados",
                "bedroom": "habitación",
                "bed": "cama",
                "bath": "baño",
                "daily": "DIARIO",
                "monthly": "MENSUAL",
                "per_night": "por noche",
                "dates": "Llegada · Salida",
                "book_now": "Reservar ahora",
            },
            "en": {
                "guests": "guests",
                "bedroom": "bedroom",
                "bed": "bed",
                "bath": "bath",
                "daily": "DAILY",
                "monthly": "MONTHLY",
                "per_night": "per night",
                "dates": "Arrival · Departure",
                "book_now": "Book now",
            },
        }.get(language, {})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        language = request.session.get("site_language", "es")
        form = BookingAvailabilityForm(property=self.object, data=request.POST, language=language)
        if form.is_valid():
            params = form.cleaned_query_params()
            city = request.GET.get("city") or request.POST.get("city")
            if city:
                params = f"{params}&{urlencode({'city': city})}"
            services_url = reverse("bookings:services", kwargs={"slug": self.object.slug})
            return redirect(f"{services_url}?{params}")
        error = (
            "Revisa las fechas y disponibilidad antes de continuar."
            if language == "es"
            else "Review dates and availability before continuing."
        )
        messages.error(request, error)
        return self.render_to_response(self.get_context_data(booking_form=form))
