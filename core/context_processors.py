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
    },
}


def site_language(request):
    language = request.session.get("site_language", "es")
    return {
        "current_language": language,
        "ui": UI_COPY.get(language, UI_COPY["es"]),
    }
