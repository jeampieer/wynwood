from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from applications.bookings.models import ExtraService, ExtraServiceTypeChoices
from applications.pages.models import (
    FooterLink,
    LandingBenefit,
    LandingDestination,
    LandingSection,
    LandingService,
    SocialLink,
)
from applications.properties.models import Amenity, City, Property, PropertyImage


class Command(BaseCommand):
    help = "Carga datos demo para verificar el flujo Wynwood."

    def handle(self, *args, **options):
        bogota, _ = City.objects.get_or_create(name="Bogotá", defaults={"country": "Colombia"})
        medellin, _ = City.objects.get_or_create(name="Medellín", defaults={"country": "Colombia"})

        amenities = []
        for name, icon in [
            ("Wi-Fi", "⌁"),
            ("Cocina equipada", "□"),
            ("Lavadora", "◌"),
            ("Aire acondicionado", "✦"),
            ("Pet friendly", "◇"),
        ]:
            amenity, _ = Amenity.objects.get_or_create(name=name, defaults={"icon": icon})
            amenities.append(amenity)

        properties = [
            {
                "city": bogota,
                "name": "Modern Duplex in Parque Virrey",
                "slug": "modern-duplex-parque-virrey",
                "neighborhood": "Bogotá Virrey",
                "price": 83,
                "capacity": 2,
                "featured": True,
                "images": ["property-living.webp", "property-bedroom.webp", "property-kitchen.webp"],
            },
            {
                "city": bogota,
                "name": "W Cozy Loft in Luxury Building",
                "slug": "cozy-loft-luxury-building",
                "neighborhood": "Parque Virrey",
                "price": 68,
                "capacity": 3,
                "featured": True,
                "images": ["property-card-1.webp", "property-card-2.webp", "property-dining.webp"],
            },
            {
                "city": medellin,
                "name": "Dazzling 2BR in Condesa",
                "slug": "dazzling-2br-condesa",
                "neighborhood": "El Poblado",
                "price": 92,
                "capacity": 4,
                "featured": True,
                "images": ["property-dining.webp", "property-bedroom.webp", "property-kitchen.webp"],
            },
            {
                "city": medellin,
                "name": "Quiet Suite with City View",
                "slug": "quiet-suite-city-view",
                "neighborhood": "Laureles",
                "price": 76,
                "capacity": 2,
                "featured": False,
                "images": ["property-card-3.webp", "property-card-1.webp", "property-bedroom.webp"],
            },
        ]

        for item in properties:
            prop, _ = Property.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "city": item["city"],
                    "name": item["name"],
                    "neighborhood": item["neighborhood"],
                    "address": f"{item['neighborhood']} · Calle 85 #12",
                    "short_description": "Apartamento amoblado con diseño cuidado y servicios hoteleros.",
                    "description": (
                        "Un espacio luminoso, completamente equipado y pensado para que cada estancia "
                        "se sienta privada, cómoda y conectada con la ciudad."
                    ),
                    "capacity": item["capacity"],
                    "bedrooms": 2 if item["capacity"] > 2 else 1,
                    "beds": 2 if item["capacity"] > 2 else 1,
                    "bathrooms": 2 if item["capacity"] > 2 else 1,
                    "nightly_price": item["price"],
                    "featured": item["featured"],
                    "is_active": True,
                },
            )
            prop.amenities.set(amenities)
            self._sync_property_images(prop, item["images"])

        for name, description, price, service_type, image in [
            (
                "Check-in & Check-out flexible",
                "Extiende tu llegada o salida cuando el calendario lo permita.",
                28,
                ExtraServiceTypeChoices.CHECKIN,
                "img/figma/service-checkin.webp",
            ),
            (
                "Servicio de transporte",
                "Traslado cómodo desde o hacia el aeropuerto.",
                50,
                ExtraServiceTypeChoices.TRANSPORT,
                "img/figma/service-transport.webp",
            ),
            (
                "Llena tu nevera",
                "Compra inicial de básicos antes de tu llegada.",
                35,
                ExtraServiceTypeChoices.FRIDGE,
                "img/figma/service-fridge.webp",
            ),
            (
                "Cuna para bebé",
                "Cuna preparada para huéspedes pequeños.",
                18,
                ExtraServiceTypeChoices.CRIB,
                "img/figma/service-crib.webp",
            ),
        ]:
            ExtraService.objects.update_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": price,
                    "service_type": service_type,
                    "image": image,
                    "is_active": True,
                },
            )

        self._seed_landing()

        self.stdout.write(self.style.SUCCESS("Datos demo Wynwood cargados correctamente."))

    def _load_static_image(self, image_name):
        path = Path(settings.BASE_DIR) / "staticfiles" / "img" / "figma" / image_name
        return ContentFile(path.read_bytes(), name=image_name)

    def _sync_property_images(self, prop, image_names):
        images = list(prop.images.all())
        has_expected_count = len(images) == len(image_names)
        has_existing_files = all(image.image and image.image.storage.exists(image.image.name) for image in images)
        if has_expected_count and has_existing_files:
            for index, image in enumerate(images):
                expected_cover = index == 0
                if image.is_cover != expected_cover:
                    image.is_cover = expected_cover
                    image.save(update_fields=["is_cover"])
            return

        for image in images:
            if image.image:
                image.image.delete(save=False)
            image.delete()

        for index, image_name in enumerate(image_names):
            PropertyImage.objects.create(
                property=prop,
                image=self._load_static_image(image_name),
                alt_text=f"{prop.name} interior {index + 1}",
                is_cover=index == 0,
            )

    def _seed_landing(self):
        sections = [
            {
                "section_type": LandingSection.PROMO,
                "title_es": "10% de descuento en estadías seleccionadas",
                "title_en": "10% off selected stays",
                "position": 0,
            },
            {
                "section_type": LandingSection.HERO,
                "eyebrow_es": "Lo mejor de ambos mundos",
                "eyebrow_en": "Best of both worlds",
                "title_es": "HOME EXPERIENCE, HOTEL QUALITY",
                "title_en": "HOME EXPERIENCE, HOTEL QUALITY",
                "position": 1,
            },
            {
                "section_type": LandingSection.DESTINATIONS,
                "title_es": "Discover our destinations",
                "title_en": "Discover our destinations",
                "position": 2,
            },
            {
                "section_type": LandingSection.FEATURED,
                "title_es": "Propiedades destacadas",
                "title_en": "Featured properties",
                "body_es": (
                    "Descubre nuestras propiedades exclusivas, de diseños únicos y cercanas a nuestros puntos "
                    "más interesantes."
                ),
                "body_en": "Explore exclusive homes with distinctive design, selected locations and hotel-quality services.",
                "position": 3,
            },
            {
                "section_type": LandingSection.SERVICES,
                "title_es": "Servicios en Wynwood House",
                "title_en": "Services at Wynwood House",
                "body_es": (
                    "Descubre los servicios que ponemos a tu disposición para hacer de tu estancia una experiencia "
                    "más cómoda, emocionante y memorable."
                ),
                "body_en": "Discover the services available to make your stay more comfortable, memorable and effortless.",
                "position": 4,
            },
            {
                "section_type": LandingSection.EVENTS,
                "title_es": "Disfruta de nuestros eventos!",
                "title_en": "Enjoy our events!",
                "body_es": (
                    "Vive la experiencia al máximo mientras te sumerges en el vibrante mundo de los eventos Wynwood."
                ),
                "body_en": "Live the experience while you immerse yourself in the vibrant world of Wynwood events.",
                "cta_es": "Ver todos los eventos",
                "cta_en": "See all events",
                "position": 5,
            },
            {
                "section_type": LandingSection.BENEFITS,
                "title_es": "Beneficios de Wynwood House",
                "title_en": "Wynwood House benefits",
                "position": 6,
            },
            {
                "section_type": LandingSection.LONG_STAY,
                "title_es": "Alquileres a largo plazo",
                "title_en": "Long-term rentals",
                "body_es": (
                    "Descubre el confort y la conveniencia de hospedarte con nosotros durante períodos prolongados. "
                    "Aprovecha nuestras tarifas especiales diseñadas exclusivamente para estadías largas."
                ),
                "body_en": "Find comfort and convenience for extended stays with furnished apartments and monthly rates.",
                "cta_es": "Contáctanos",
                "cta_en": "Contact us",
                "position": 7,
            },
            {
                "section_type": LandingSection.INVEST,
                "title_es": "Invierte en real estate",
                "title_en": "Invest in real estate",
                "body_es": "Compra o renta una propiedad y obtén asesoramiento profesional y una experiencia sin igual.",
                "body_en": "Buy or rent a property with professional advice and a seamless experience.",
                "cta_es": "Saber más",
                "cta_en": "Learn more",
                "position": 8,
            },
        ]
        for section in sections:
            section_type = section.pop("section_type")
            LandingSection.objects.update_or_create(
                section_type=section_type,
                defaults={**section, "is_active": True},
            )

        for index, item in enumerate(
            [
                ("Colombia", "Colombia", "img/homepage/destination-colombia.png"),
                ("México", "México", "img/homepage/destination-mexico.png"),
                ("Perú", "Perú", "img/homepage/destination-peru.png"),
                ("Panamá", "Panamá", "img/homepage/destination-panama.png"),
                ("España", "España", "img/homepage/destination-spain.png"),
            ]
        ):
            name, country, image = item
            LandingDestination.objects.update_or_create(
                name=name,
                defaults={"country": country, "image": image, "position": index, "is_active": True},
            )

        services = [
            ("Check-in sin contacto", "Contactless check-in", "img/figma/service-checkin.webp"),
            ("Limpieza profesional", "Professional cleaning", "img/figma/property-bedroom.webp"),
            ("Wifi", "Wifi", "img/figma/property-kitchen.webp"),
            ("Kit de baño", "Bathroom kit", "img/figma/service-crib.webp"),
            ("Cocina equipada", "Equipped kitchen", "img/figma/property-dining.webp"),
            ("Pet friendly", "Pet friendly", "img/figma/property-card-3.webp"),
            ("Soporte 24/7", "24/7 support", "img/figma/service-transport.webp"),
            ("Cama premium", "Premium bed", "img/figma/property-living.webp"),
        ]
        for index, (title_es, title_en, image) in enumerate(services):
            LandingService.objects.update_or_create(
                title_es=title_es,
                defaults={"title_en": title_en, "image": image, "position": index, "is_active": True},
            )

        benefits = [
            (
                "Guías de ciudades",
                "City guides",
                "Conoce qué visitar y cómo moverte en cada destino.",
                "Learn what to visit and how to move around each destination.",
                "",
            ),
            ("Servicios adicionales", "Additional services", "", "", "img/figma/service-fridge.webp"),
            ("Programa de rewards", "Rewards program", "", "", "img/figma/property-bedroom.webp"),
        ]
        for index, (title_es, title_en, text_es, text_en, image) in enumerate(benefits):
            LandingBenefit.objects.update_or_create(
                title_es=title_es,
                defaults={
                    "title_en": title_en,
                    "text_es": text_es,
                    "text_en": text_en,
                    "image": image,
                    "position": index,
                    "is_active": True,
                },
            )

        footer_links = [
            ("Reservas", "Buscar estadía", "Search stays", "/properties/search/"),
            ("Servicios", "Grupos & Largas Estadías", "Groups & Long Stays", "#"),
            ("Servicios", "Eventos & Producciones", "Events & Productions", "#"),
            ("Nosotros", "¿Quiénes somos?", "About us", "#"),
            ("Nosotros", "Blog & News", "Blog & News", "#"),
            ("Nosotros", "Casa Wynwood", "Casa Wynwood", "#"),
            ("Propietarios & Inversionistas", "Wynwood Real Estate", "Wynwood Real Estate", "#"),
            ("Propietarios & Inversionistas", "Publica tu propiedad", "List your property", "#"),
            ("Beneficios", "Guides", "Guides", "#"),
            ("Beneficios", "Rewards Program", "Rewards Program", "#"),
        ]
        for index, (group, label_es, label_en, url) in enumerate(footer_links):
            FooterLink.objects.update_or_create(
                group=group,
                label_es=label_es,
                defaults={"label_en": label_en, "url": url, "position": index, "is_active": True},
            )

        for index, (name, url, icon) in enumerate(
            [
                ("Facebook", "#", "img/homepage/Facebook.png"),
                ("Instagram", "#", "img/homepage/Instagram.png"),
                ("LinkedIn", "#", "img/homepage/linkedin.png"),
            ]
        ):
            SocialLink.objects.update_or_create(
                name=name,
                defaults={"url": url, "icon": icon, "position": index, "is_active": True},
            )
