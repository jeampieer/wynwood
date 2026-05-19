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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = getattr(
            self,
            "form",
            SearchForm(self.request.GET or None, language=self.request.session.get("site_language", "es")),
        )
        context["query_string"] = self.request.GET.urlencode()
        return context


class PropertyDetailView(DetailView):
    model = Property
    template_name = "properties/detail.html"
    context_object_name = "property"
    queryset = Property.objects.filter(is_active=True).select_related("city").prefetch_related("amenities", "images")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {
            "check_in": self.request.GET.get("check_in"),
            "check_out": self.request.GET.get("check_out"),
            "guests": self.request.GET.get("guests") or 2,
        }
        context.setdefault("booking_form", BookingAvailabilityForm(property=self.object, data=None, initial=initial))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = BookingAvailabilityForm(property=self.object, data=request.POST)
        if form.is_valid():
            params = form.cleaned_query_params()
            services_url = reverse("bookings:services", kwargs={"slug": self.object.slug})
            return redirect(f"{services_url}?{params}")
        messages.error(request, "Revisa las fechas y disponibilidad antes de continuar.")
        return self.render_to_response(self.get_context_data(booking_form=form))
