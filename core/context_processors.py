from collections import defaultdict

from django.db import OperationalError, ProgrammingError


UI_COPY = {
    "es": {
        "menu": "Menú",
        "home": "Casa Wynwood",
        "collection": "The Collection",
        "list_property": "Publica tu propiedad",
        "invest": "Invierte en Bienes Raíces",
        "login": "Iniciar sesión",
        "logout": "Salir",
        "book_now": "Reservar Ahora",
        "footer_line": "Home experience, hotel quality.",
        "per_night": "noche",
        "bedroom_short": "hab",
        "bed_short": "cama",
        "bath_short": "baño",
        "instagram": "Instagram",
        "linkedin": "LinkedIn",
        "destination": "Destino",
        "dates": "Llegada - Salida",
        "add_dates": "Agregar fechas",
        "guests": "Huéspedes",
        "guest_count": "2 Huéspedes",
        "search": "Buscar",
        "reservations": "Reservas",
        "services": "Servicios",
        "groups_long_stays": "Grupos & Largas Estadías",
        "events_productions": "Eventos & Producciones",
        "about": "Nosotros",
        "who_we_are": "¿Quiénes somos?",
        "blog_news": "Blog & News",
        "work_with_us": "Trabaja con nosotros",
        "owners_investors": "Propietarios<br />& Inversionistas",
        "real_estate": "Wynwood Real Estate",
        "benefits": "Beneficios",
        "guides": "Guías",
        "rewards": "Programa de recompensas",
        "destinations": "Destinos",
        "terms": "Términos<br />y Condiciones",
        "terms_service": "Términos de servicio",
        "privacy": "Políticas de privacidad",
        "cancellation": "Políticas de cancelación",
        "contact_us": "Contáctanos",
        "write_us": "Escríbenos",
        "faq": "F.A.Q.",
        "download_app": "Descarga nuestra app gratis",
        "app_store": "Download on the<br /><strong>App Store</strong>",
        "google_play": "Get it on<br /><strong>Google Play</strong>",
    },
    "en": {
        "menu": "Menu",
        "home": "Wynwood Home",
        "collection": "The Collection",
        "list_property": "List your property",
        "invest": "Invest in Real Estate",
        "login": "Sign in",
        "logout": "Sign out",
        "book_now": "Book Now",
        "footer_line": "Home experience, hotel quality.",
        "per_night": "night",
        "bedroom_short": "bed",
        "bed_short": "bed",
        "bath_short": "bath",
        "instagram": "Instagram",
        "linkedin": "LinkedIn",
        "destination": "Destination",
        "dates": "Arrival - Departure",
        "add_dates": "Add dates",
        "guests": "Guests",
        "guest_count": "2 Guests",
        "search": "Search",
        "reservations": "Reservations",
        "services": "Services",
        "groups_long_stays": "Groups & Long Stays",
        "events_productions": "Events & Productions",
        "about": "About us",
        "who_we_are": "Who we are",
        "blog_news": "Blog & News",
        "work_with_us": "Work with us",
        "owners_investors": "Owners<br />& Investors",
        "real_estate": "Wynwood Real Estate",
        "benefits": "Benefits",
        "guides": "Guides",
        "rewards": "Rewards Program",
        "destinations": "Destinations",
        "terms": "Terms<br />and Conditions",
        "terms_service": "Terms of service",
        "privacy": "Privacy policy",
        "cancellation": "Cancellation policy",
        "contact_us": "Contact us",
        "write_us": "Write to us",
        "faq": "F.A.Q.",
        "download_app": "Download our app for free",
        "app_store": "Download on the<br /><strong>App Store</strong>",
        "google_play": "Get it on<br /><strong>Google Play</strong>",
    },
}


def site_language(request):
    language = request.session.get("site_language", "es")
    return {
        "current_language": language,
        "ui": UI_COPY.get(language, UI_COPY["es"]),
        "footer_search_form": _footer_search_form(request, language),
        "footer_groups": _footer_groups(language),
        "social_links": _social_links(),
    }


def _footer_search_form(request, language):
    try:
        from applications.properties.forms import SearchForm

        return SearchForm(request.GET or None, language=language)
    except (OperationalError, ProgrammingError):
        return None


def _footer_groups(language):
    try:
        from applications.pages.models import FooterLink

        groups = defaultdict(list)
        links = FooterLink.objects.filter(is_active=True).order_by("position", "id")
        for link in links:
            groups[link.group].append({"label": link.label(language), "url": link.url})
        return dict(groups)
    except (OperationalError, ProgrammingError):
        return {}


def _social_links():
    try:
        from applications.pages.models import SocialLink

        return SocialLink.objects.filter(is_active=True).order_by("position", "id")
    except (OperationalError, ProgrammingError):
        return []
