import uuid
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, TemplateView

from applications.accounts.models import User
from applications.bookings.forms import (
    BookingAvailabilityForm,
    CheckoutForm,
    FlexibleCheckinForm,
    TransportServiceForm,
)
from applications.bookings.models import (
    Booking,
    BookingStatusChoices,
    ExtraService,
    ExtraServiceTypeChoices,
    Payment,
    PaymentStatusChoices,
)
from applications.properties.models import Property


class AvailabilityContextMixin:
    def dispatch(self, request, *args, **kwargs):
        self.property = get_object_or_404(Property, slug=kwargs["slug"], is_active=True)
        self.availability_form = BookingAvailabilityForm(property=self.property, data=request.GET or None)
        if not self.availability_form.is_valid():
            messages.error(request, "Selecciona fechas disponibles para continuar.")
            return redirect(self.property.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def booking_query(self, extra_params=None):
        params = {
            "check_in": self.availability_form.cleaned_data["check_in"].isoformat(),
            "check_out": self.availability_form.cleaned_data["check_out"].isoformat(),
            "guests": self.availability_form.cleaned_data["guests"],
        }
        if extra_params:
            params.update(extra_params)
        return urlencode(params, doseq=True)

    def checkout_url(self, services=None):
        services = services or self.request.GET.getlist("services")
        url = reverse("bookings:checkout", kwargs={"slug": self.property.slug})
        params = {}
        if services:
            params["services"] = services
        return f"{url}?{self.booking_query(params)}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["property"] = self.property
        context["availability"] = self.availability_form.cleaned_data
        context["checkout_url"] = self.checkout_url()
        return context


class ServiceCatalogView(AvailabilityContextMixin, TemplateView):
    template_name = "bookings/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = list(ExtraService.objects.filter(is_active=True))
        context["services"] = services
        context["service_options"] = [
            {
                "service": service,
                "checkout_url": self._service_checkout_url(service),
                "kind": service.service_type,
                "image": service.display_image(),
            }
            for service in services
        ]
        context["selected_services"] = self.request.GET.getlist("services")
        return context

    def _service_checkout_url(self, service):
        selected = set(self.request.GET.getlist("services"))
        selected.add(str(service.pk))
        return self.checkout_url(sorted(selected))


class FlexibleCheckinView(AvailabilityContextMixin, FormView):
    template_name = "bookings/flexible_checkin.html"
    form_class = FlexibleCheckinForm

    def form_valid(self, form):
        messages.success(self.request, "Agregamos la solicitud de check-in flexible a tu reserva.")
        service = ExtraService.objects.filter(service_type=ExtraServiceTypeChoices.CHECKIN, is_active=True).first()
        selected = set(self.request.GET.getlist("services"))
        if service:
            selected.add(str(service.pk))
        return redirect(self.checkout_url(sorted(selected)))


class TransportServiceView(AvailabilityContextMixin, FormView):
    template_name = "bookings/transport.html"
    form_class = TransportServiceForm

    def get_initial(self):
        initial = super().get_initial()
        initial["passengers"] = self.availability_form.cleaned_data["guests"]
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Agregamos el servicio de transporte a tu reserva.")
        service = ExtraService.objects.filter(service_type=ExtraServiceTypeChoices.TRANSPORT, is_active=True).first()
        selected = set(self.request.GET.getlist("services"))
        if service:
            selected.add(str(service.pk))
        return redirect(self.checkout_url(sorted(selected)))


class CheckoutView(AvailabilityContextMixin, FormView):
    template_name = "bookings/checkout.html"
    form_class = CheckoutForm

    def get_initial(self):
        initial = super().get_initial()
        service_ids = self.request.GET.getlist("services")
        if service_ids:
            initial["services"] = service_ids
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = context["form"].fields["services"].queryset
        selected_ids = self.request.POST.getlist("services") or self.request.GET.getlist("services")
        selected_services = list(services.filter(pk__in=selected_ids))
        context["services"] = services
        context["service_options"] = [
            {
                "service": service,
                "image": service.display_image(),
                "selected": str(service.pk) in selected_ids,
            }
            for service in services
        ]
        context["selected_services"] = selected_services
        context["preview"] = self._build_preview(selected_services)
        context["services_url"] = (
            reverse("bookings:services", kwargs={"slug": self.property.slug})
            + f"?{self.booking_query({'services': self.request.GET.getlist('services')})}"
        )
        return context

    def form_valid(self, form):
        user = self._get_or_create_user(form)
        if not user:
            return self.form_invalid(form)
        services = list(form.cleaned_data["services"])
        booking = Booking(
            user=user,
            property=self.property,
            check_in=self.availability_form.cleaned_data["check_in"],
            check_out=self.availability_form.cleaned_data["check_out"],
            guests=self.availability_form.cleaned_data["guests"],
            status=BookingStatusChoices.CONFIRMED,
        )
        booking.calculate_totals(services)
        booking.full_clean()
        booking.save()
        booking.extra_services.set(services)
        Payment.objects.create(
            booking=booking,
            status=PaymentStatusChoices.PAID,
            amount=booking.total,
            reference=f"WH-{uuid.uuid4().hex[:10].upper()}",
        )
        self._send_confirmation(booking)
        login(self.request, user)
        return redirect("bookings:confirmation", pk=booking.pk)

    def _get_or_create_user(self, form):
        if self.request.user.is_authenticated:
            return self.request.user
        email = form.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            form.add_error("email", "Ya existe una cuenta con este correo. Inicia sesión para continuar.")
            return None
        password = form.cleaned_data["password1"]
        try:
            validate_password(password)
        except Exception as error:
            form.add_error("password1", error)
            return None
        full_name = form.cleaned_data["full_name"].strip()
        first_name, _, last_name = full_name.partition(" ")
        return User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

    def _build_preview(self, services):
        booking = Booking(
            property=self.property,
            check_in=self.availability_form.cleaned_data["check_in"],
            check_out=self.availability_form.cleaned_data["check_out"],
            guests=self.availability_form.cleaned_data["guests"],
        )
        booking.calculate_totals(services)
        return booking

    def _send_confirmation(self, booking):
        send_mail(
            subject=f"Reserva confirmada en {booking.property.name}",
            message=(
                f"Tu reserva quedó confirmada.\n\n"
                f"Propiedad: {booking.property.name}\n"
                f"Llegada: {booking.check_in}\n"
                f"Salida: {booking.check_out}\n"
                f"Huéspedes: {booking.guests}\n"
                f"Total: USD {booking.total}\n"
            ),
            from_email=None,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )


class BookingConfirmationView(DetailView):
    model = Booking
    template_name = "bookings/confirmation.html"
    context_object_name = "booking"
