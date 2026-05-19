from django.views.generic import TemplateView

from applications.properties.forms import SearchForm
from applications.properties.models import Property


LANDING_COPY = {
    "es": {
        "eyebrow": "Lo mejor de ambos mundos",
        "headline": "HOME EXPERIENCE, HOTEL QUALITY",
        "promo": "Corre 10% de descuento en todos tus viajes · Quédate con nosotros 01 · 08 · 59",
        "search": "Buscar",
        "district": "Distrito",
        "destinations": "Discover our destinations",
        "collection_eyebrow": "Wynwood Collection",
        "featured": "Propiedades destacadas",
        "featured_body": (
            "Descubre nuestras propiedades exclusivas, de diseños únicos y "
            "cercanas a nuestros puntos más interesantes."
        ),
        "services": "Servicios en Wynwood House",
        "services_body": (
            "Descubre los servicios que ponemos a tu disposición para hacer de tu "
            "estancia una experiencia más cómoda, emocionante y memorable."
        ),
        "events_title": "Disfruta de nuestros eventos!",
        "events_body": (
            "Vive la experiencia al máximo mientras te sumerges en el vibrante mundo "
            "de los eventos Wynwood. Disfruta de arte, cultura e inspiración como nunca antes."
        ),
        "events_cta": "Ver todos los eventos",
        "benefits": "Beneficios de Wynwood House",
        "long_title": "Alquileres a largo plazo",
        "long_body": (
            "Descubre el confort y la conveniencia de hospedarte con nosotros durante "
            "periodos prolongados. Apartamentos amoblados, tarifas mensuales y atención personalizada."
        ),
        "contact": "Contáctanos",
        "invest_title": "Invierte en real estate",
        "invest_body": "Compra o renta una propiedad y obtén asesoramiento profesional y una experiencia sin igual.",
        "learn_more": "Saber más",
    },
    "en": {
        "eyebrow": "Best of both worlds",
        "headline": "HOME EXPERIENCE, HOTEL QUALITY",
        "promo": "Get 10% off every trip · Stay with us 01 · 08 · 59",
        "search": "Search",
        "district": "District",
        "destinations": "Discover our destinations",
        "collection_eyebrow": "Wynwood Collection",
        "featured": "Featured properties",
        "featured_body": (
            "Explore exclusive homes with distinctive design, selected locations and "
            "hotel-quality services."
        ),
        "services": "Services at Wynwood House",
        "services_body": (
            "Discover the services available to make your stay more comfortable, "
            "memorable and effortless."
        ),
        "events_title": "Enjoy our events!",
        "events_body": (
            "Live the experience while you immerse yourself in the vibrant world of "
            "Wynwood events, culture and inspiration."
        ),
        "events_cta": "See all events",
        "benefits": "Wynwood House benefits",
        "long_title": "Long-term rentals",
        "long_body": (
            "Find comfort and convenience for extended stays with furnished apartments, "
            "monthly rates and personalized support."
        ),
        "contact": "Contact us",
        "invest_title": "Invest in real estate",
        "invest_body": "Buy or rent a property with professional advice and a seamless experience.",
        "learn_more": "Learn more",
    },
}

DESTINATIONS = [
    {"name": "Colombia", "image": "img/homepage/destination-colombia.png"},
    {"name": "México", "image": "img/homepage/destination-mexico.png"},
    {"name": "Perú", "image": "img/homepage/destination-peru.png"},
    {"name": "Panamá", "image": "img/homepage/destination-panama.png"},
    {"name": "España", "image": "img/homepage/destination-spain.png"},
]

SERVICES = [
    {"name": "Check-in sin contacto", "image": "img/figma/service-checkin.webp"},
    {"name": "Limpieza profesional", "image": "img/figma/property-bedroom.webp"},
    {"name": "Wifi", "image": "img/figma/property-kitchen.webp"},
    {"name": "Kit de baño", "image": "img/figma/service-crib.webp"},
    {"name": "Cocina equipada", "image": "img/figma/property-dining.webp"},
    {"name": "Pet friendly", "image": "img/figma/property-card-3.webp"},
    {"name": "Soporte 24/7", "image": "img/figma/service-transport.webp"},
    {"name": "Cama premium", "image": "img/figma/property-living.webp"},
]

BENEFITS = [
    {"title": "Guías de ciudades", "text": "Conoce qué visitar y cómo moverte en cada destino.", "image": ""},
    {"title": "Servicios adicionales", "text": "", "image": "img/figma/service-fridge.webp"},
    {"title": "Programa de rewards", "text": "", "image": "img/figma/property-bedroom.webp"},
]


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.request.session.get("site_language", "es")
        context["copy"] = LANDING_COPY.get(language, LANDING_COPY["es"])
        context["form"] = SearchForm(language=language)
        context["featured_properties"] = (
            Property.objects.filter(is_active=True, featured=True)
            .select_related("city")
            .prefetch_related("images")[:3]
        )
        context["destinations"] = DESTINATIONS
        context["services"] = SERVICES
        context["benefits"] = BENEFITS
        return context
