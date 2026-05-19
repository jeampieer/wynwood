from django.views.generic import TemplateView

from applications.pages.models import LandingBenefit, LandingDestination, LandingSection, LandingService
from applications.properties.forms import SearchForm
from applications.properties.models import Property


DEFAULT_COPY = {
    "es": {
        "promo": "10% de descuento en estadías seleccionadas",
        "promo_cta": "Reservar ahora",
        "eyebrow": "Lo mejor de ambos mundos",
        "headline": "HOME EXPERIENCE, HOTEL QUALITY",
        "search": "Buscar",
        "district": "Distrito",
        "destinations": "Discover our destinations",
        "featured": "Propiedades destacadas",
        "featured_body": (
            "Descubre nuestras propiedades exclusivas, de diseños únicos y cercanas a nuestros puntos más interesantes."
        ),
        "services": "Servicios en Wynwood House",
        "services_body": (
            "Descubre los servicios que ponemos a tu disposición para hacer de tu estancia una experiencia más cómoda."
        ),
        "events_title": "Disfruta de nuestros eventos!",
        "events_body": "Vive la experiencia al máximo mientras te sumerges en los eventos Wynwood.",
        "events_cta": "Ver todos los eventos",
        "benefits": "Beneficios de Wynwood House",
        "long_title": "Alquileres a largo plazo",
        "long_body": "Descubre el confort y la conveniencia de hospedarte con nosotros durante períodos prolongados.",
        "contact": "Contáctanos",
        "invest_title": "Invierte en real estate",
        "invest_body": "Compra o renta una propiedad y obtén asesoramiento profesional.",
        "learn_more": "Saber más",
    },
    "en": {
        "promo": "10% off selected stays",
        "promo_cta": "Book now",
        "eyebrow": "Best of both worlds",
        "headline": "HOME EXPERIENCE, HOTEL QUALITY",
        "search": "Search",
        "district": "District",
        "destinations": "Discover our destinations",
        "featured": "Featured properties",
        "featured_body": "Explore exclusive homes with distinctive design, selected locations and hotel-quality services.",
        "services": "Services at Wynwood House",
        "services_body": "Discover the services available to make your stay more comfortable and memorable.",
        "events_title": "Enjoy our events!",
        "events_body": "Live the experience while you immerse yourself in Wynwood events.",
        "events_cta": "See all events",
        "benefits": "Wynwood House benefits",
        "long_title": "Long-term rentals",
        "long_body": "Find comfort and convenience for extended stays with furnished apartments and monthly rates.",
        "contact": "Contact us",
        "invest_title": "Invest in real estate",
        "invest_body": "Buy or rent a property with professional advice.",
        "learn_more": "Learn more",
    },
}


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.request.session.get("site_language", "es")
        context["copy"] = self._build_copy(language)
        context["form"] = SearchForm(language=language)
        context["featured_properties"] = (
            Property.objects.filter(is_active=True, featured=True)
            .select_related("city")
            .prefetch_related("images")[:3]
        )
        context["destinations"] = LandingDestination.objects.filter(is_active=True).order_by("position", "id")
        context["services"] = [
            {"name": service.title(language), "image": service.image}
            for service in LandingService.objects.filter(is_active=True).order_by("position", "id")
        ]
        context["benefits"] = [
            benefit.localized(language)
            for benefit in LandingBenefit.objects.filter(is_active=True).order_by("position", "id")
        ]
        return context

    def _build_copy(self, language):
        copy = DEFAULT_COPY.get(language, DEFAULT_COPY["es"]).copy()
        sections = LandingSection.objects.filter(is_active=True)
        for section in sections:
            data = section.localized(language)
            if section.section_type == LandingSection.PROMO:
                copy["promo"] = data["title"]
            elif section.section_type == LandingSection.HERO:
                copy["eyebrow"] = data["eyebrow"] or copy["eyebrow"]
                copy["headline"] = data["title"]
            elif section.section_type == LandingSection.DESTINATIONS:
                copy["destinations"] = data["title"]
            elif section.section_type == LandingSection.FEATURED:
                copy["featured"] = data["title"]
                copy["featured_body"] = data["body"]
            elif section.section_type == LandingSection.SERVICES:
                copy["services"] = data["title"]
                copy["services_body"] = data["body"]
            elif section.section_type == LandingSection.EVENTS:
                copy["events_title"] = data["title"]
                copy["events_body"] = data["body"]
                copy["events_cta"] = data["cta"] or copy["events_cta"]
            elif section.section_type == LandingSection.BENEFITS:
                copy["benefits"] = data["title"]
            elif section.section_type == LandingSection.LONG_STAY:
                copy["long_title"] = data["title"]
                copy["long_body"] = data["body"]
                copy["contact"] = data["cta"] or copy["contact"]
            elif section.section_type == LandingSection.INVEST:
                copy["invest_title"] = data["title"]
                copy["invest_body"] = data["body"]
                copy["learn_more"] = data["cta"] or copy["learn_more"]
        return copy
