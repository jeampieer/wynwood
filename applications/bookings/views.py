import uuid
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.templatetags.static import static
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


BOOKING_COPY = {
    "es": {
        "availability_error": "Selecciona fechas disponibles para continuar.",
        "services": "Servicios",
        "services_step": "03. Servicios adicionales",
        "services_title": "BIENVENIDO A WYNWOOD HOUSE",
        "services_intro": (
            "Personaliza tu estadía con servicios preparados antes de tu llegada. "
            "Puedes continuar sin seleccionar nada o entrar a los flujos específicos del prototipo."
        ),
        "configure": "Configurar",
        "add": "Añadir",
        "arrival": "Llegada",
        "departure": "Salida",
        "guests": "Huéspedes",
        "continue_payment": "Continuar a pago",
        "flexible_title": "AJUSTA TU LLEGADA A TU RITMO",
        "flexible_step": "04. Check-in & Check-out flexible",
        "flexible_intro": "Déjanos tu horario ideal y coordinaremos la disponibilidad operativa antes de confirmar el pago.",
        "flexible_success": "Agregamos la solicitud de check-in flexible a tu reserva.",
        "transport_title": "MUÉVETE SIN FRICCIÓN",
        "transport_step": "04. Servicio de transporte",
        "transport_intro": "Configura el traslado para que tu llegada o salida mantenga la misma experiencia Wynwood.",
        "add_continue": "Añadir y continuar",
        "transport_success": "Agregamos el servicio de transporte a tu reserva.",
        "checkout_title": "REGISTRO",
        "checkout_page": "Página de pago",
        "checkout_intro": "Te enviaremos la confirmación de tu reserva por correo electrónico.",
        "checkout_error": "Revisa los campos marcados para continuar con el pago simulado.",
        "additional_services": "SERVICIOS ADICIONALES",
        "edit_services": "Editar servicios",
        "payment_method": "MÉTODO DE PAGO",
        "mock_payment": "Mock de pasarela de pago con tarjeta. No se procesa un cobro real.",
        "pay_confirm": "Confirmar pago simulado y reserva",
        "dates": "Fechas",
        "people": "personas",
        "subtotal": "Subtotal",
        "cleaning_fee": "Tarifa de limpieza",
        "taxes": "Impuestos",
        "discount": "Descuento Wynwood Points",
        "total": "Total",
        "points": "Con esta reserva estás generando Wynwood Points.",
        "duplicate_email": "Ya existe una cuenta con este correo. Inicia sesión para continuar.",
        "confirmation_title": "Reserva confirmada",
        "confirmation_heading": "Tu estadía en {property} quedó lista.",
        "confirmation_sent": "Enviamos la constancia a {email}.",
        "total_paid": "Total pagado",
        "reference": "Referencia",
        "back_home": "Volver al inicio",
        "email_subject": "Reserva confirmada en {property}",
        "email_body": "Tu reserva quedó confirmada.",
    },
    "en": {
        "availability_error": "Select available dates to continue.",
        "services": "Services",
        "services_step": "03. Additional services",
        "services_title": "WELCOME TO WYNWOOD HOUSE",
        "services_intro": (
            "Personalize your stay with services prepared before arrival. "
            "You can continue without selecting anything or open the prototype-specific service flows."
        ),
        "configure": "Configure",
        "add": "Add",
        "arrival": "Arrival",
        "departure": "Departure",
        "guests": "Guests",
        "continue_payment": "Continue to payment",
        "flexible_title": "SET ARRIVAL AROUND YOUR PLANS",
        "flexible_step": "04. Flexible check-in & check-out",
        "flexible_intro": "Share your ideal schedule and we will coordinate operational availability before confirming the mock payment.",
        "flexible_success": "We added the flexible check-in request to your reservation.",
        "transport_title": "MOVE WITHOUT FRICTION",
        "transport_step": "04. Transport service",
        "transport_intro": "Configure the transfer so your arrival or departure keeps the same Wynwood experience.",
        "add_continue": "Add and continue",
        "transport_success": "We added transport service to your reservation.",
        "checkout_title": "REGISTRATION",
        "checkout_page": "Payment page",
        "checkout_intro": "We will email your booking confirmation.",
        "checkout_error": "Review the highlighted fields to continue with the simulated payment.",
        "additional_services": "ADDITIONAL SERVICES",
        "edit_services": "Edit services",
        "payment_method": "PAYMENT METHOD",
        "mock_payment": "Card payment gateway mock. No real charge is processed.",
        "pay_confirm": "Confirm simulated payment and booking",
        "dates": "Dates",
        "people": "people",
        "subtotal": "Subtotal",
        "cleaning_fee": "Cleaning fee",
        "taxes": "Taxes",
        "discount": "Wynwood Points discount",
        "total": "Total",
        "points": "This booking earns Wynwood Points.",
        "duplicate_email": "An account already exists with this email. Sign in to continue.",
        "confirmation_title": "Booking confirmed",
        "confirmation_heading": "Your stay at {property} is ready.",
        "confirmation_sent": "We sent the receipt to {email}.",
        "total_paid": "Total paid",
        "reference": "Reference",
        "back_home": "Back to home",
        "email_subject": "Booking confirmed at {property}",
        "email_body": "Your booking is confirmed.",
    },
}


SERVICE_COPY = {
    "en": {
        ExtraServiceTypeChoices.CHECKIN: {
            "name": "Flexible check-in & check-out",
            "description": "Adjust arrival and departure timing with the operations team.",
        },
        ExtraServiceTypeChoices.TRANSPORT: {
            "name": "Transport service",
            "description": "Coordinate airport or city transfers for your stay.",
        },
        ExtraServiceTypeChoices.FRIDGE: {
            "name": "Stocked fridge",
            "description": "Arrive to groceries and drinks already waiting in the apartment.",
        },
        ExtraServiceTypeChoices.CRIB: {
            "name": "Crib",
            "description": "Have a crib ready before check-in.",
        },
    }
}


class AvailabilityContextMixin:
    def dispatch(self, request, *args, **kwargs):
        self.language = request.session.get("site_language", "es")
        self.property = get_object_or_404(Property, slug=kwargs["slug"], is_active=True)
        self.availability_form = BookingAvailabilityForm(
            property=self.property,
            data=request.GET or None,
            language=self.language,
        )
        if not self.availability_form.is_valid():
            messages.error(request, self.copy["availability_error"])
            return redirect(self.property.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    @property
    def copy(self):
        return BOOKING_COPY.get(getattr(self, "language", "es"), BOOKING_COPY["es"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["language"] = self.language
        return kwargs

    def booking_query(self, extra_params=None):
        params = {
            "check_in": self.availability_form.cleaned_data["check_in"].isoformat(),
            "check_out": self.availability_form.cleaned_data["check_out"].isoformat(),
            "guests": self.availability_form.cleaned_data["guests"],
        }
        city = self.request.GET.get("city")
        if city:
            params["city"] = city
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
        context["copy"] = self.copy
        return context

    def service_name(self, service):
        return SERVICE_COPY.get(self.language, {}).get(service.service_type, {}).get("name", service.name)

    def service_description(self, service):
        return SERVICE_COPY.get(self.language, {}).get(service.service_type, {}).get(
            "description",
            service.description,
        )


class ServiceCatalogView(AvailabilityContextMixin, TemplateView):
    template_name = "bookings/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = list(ExtraService.objects.filter(is_active=True))
        context["services"] = services
        context["service_options"] = [
            {
                "service": service,
                "name": self.service_name(service),
                "description": self.service_description(service),
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
        messages.success(self.request, self.copy["flexible_success"])
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
        messages.success(self.request, self.copy["transport_success"])
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
                "name": self.service_name(service),
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
            guest=user,
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
            form.add_error("email", self.copy["duplicate_email"])
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
            subject=self.copy["email_subject"].format(property=booking.property.name),
            message=(
                f"{self.copy['email_body']}\n\n"
                f"Propiedad: {booking.property.name}\n"
                f"Llegada: {booking.check_in}\n"
                f"Salida: {booking.check_out}\n"
                f"Huéspedes: {booking.guests}\n"
                f"Total: USD {booking.total}\n"
            ),
            from_email=None,
            recipient_list=[booking.guest.email],
            fail_silently=False,
        )


class BookingConfirmationView(DetailView):
    model = Booking
    template_name = "bookings/confirmation.html"
    context_object_name = "booking"
    month_names = {
        "es": (
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ),
        "en": (
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ),
    }
    service_cards = (
        {
            "title": "Limpieza adicional",
            "image": "img/confirmation/cleaning.webp",
        },
        {
            "title": "Transporte privado",
            "image": "img/confirmation/transport.webp",
        },
        {
            "title": "Late check-out",
            "image": "img/confirmation/late-checkout.webp",
        },
        {
            "title": "Seguro de viajes",
            "image": "img/confirmation/travel-insurance.webp",
        },
    )
    reward_points = 84
    welcome_copy = {
        "es": {
            "hello": "¡Hola!",
            "eyebrow": "GRACIAS POR ELEGIR WYNWOOD HOUSE / PARA TU PRÓXIMA ESTADÍA",
            "body": (
                "Tu reserva está confirmada. Te estaremos enviando toda la información "
                "previa a tu llegada por correo electrónico. Si tienes alguna consulta, "
                "no dudes en contactarnos."
            ),
            "cta": "Conversa con nosotros 24/7",
            "points_label": "CON ESTA RESERVA ESTÁS ACUMULANDO",
            "points_link": "Descubre tus beneficios",
        },
        "en": {
            "hello": "Hello!",
            "eyebrow": "THANK YOU FOR CHOOSING WYNWOOD HOUSE / FOR YOUR NEXT STAY",
            "body": (
                "Your booking is confirmed. We will send all pre-arrival information "
                "by email. If you have any questions, contact us anytime."
            ),
            "cta": "Chat with us 24/7",
            "points_label": "WITH THIS BOOKING YOU ARE EARNING",
            "points_link": "Discover your benefits",
        },
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.request.session.get("site_language", "es")
        copy = BOOKING_COPY.get(language, BOOKING_COPY["es"])
        cover = self.object.property.cover_image
        context["copy"] = copy
        context["confirmation_heading"] = copy["confirmation_heading"].format(
            property=self.object.property.name
        )
        context["confirmation_sent"] = copy["confirmation_sent"].format(email=self.object.guest.email)
        context["welcome"] = self.welcome_copy.get(language, self.welcome_copy["es"])
        context["hero_image"] = (
            cover.image.url if cover else static("img/figma/property-card-1.webp")
        )
        context["hero_image_alt"] = (
            cover.alt_text if cover and cover.alt_text else self.object.property.name
        )
        context["reward_points"] = self.reward_points
        context["date_range"] = self._date_range(language)
        context["nights_label"] = self._nights_label()
        context["receipt_lines"] = self._receipt_lines()
        context["service_cards"] = self.service_cards
        return context

    def _date_range(self, language):
        check_in = self._format_date(self.object.check_in, language)
        check_out = self._format_date(self.object.check_out, language)
        return f"{check_in} - {check_out}"

    def _format_date(self, value, language):
        months = self.month_names.get(language, self.month_names["es"])
        if language == "en":
            return f"{months[value.month - 1]} {value.day}, {value.year}"
        return f"{value.day} de {months[value.month - 1]} de {value.year}"

    def _nights_label(self):
        nights = self.object.nights()
        noun = "Noche" if nights == 1 else "Noches"
        return f"{nights} {noun}"

    def _receipt_lines(self):
        booking = self.object
        return [
            {"label": self._nights_label(), "amount": self._money(booking.subtotal)},
            {"label": "Tarifa de limpieza", "amount": self._money(booking.cleaning_fee)},
            {
                "label": "Descuento Wynwood Points",
                "amount": f"-{self._money(booking.discount)}",
            },
            {"label": "Total", "amount": self._money(booking.total), "is_total": True},
        ]

    def _money(self, value):
        return f"USD {value:,.2f}"
