from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from applications.bookings.models import ExtraService
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
            prop.images.all().delete()
            for index, image_name in enumerate(item["images"]):
                PropertyImage.objects.create(
                    property=prop,
                    image=self._load_static_image(image_name),
                    alt_text=f"{prop.name} interior {index + 1}",
                    is_cover=index == 0,
                )

        for name, description, price in [
            ("Check-in & Check-out flexible", "Extiende tu llegada o salida cuando el calendario lo permita.", 28),
            ("Servicio de transporte", "Traslado cómodo desde o hacia el aeropuerto.", 50),
            ("Llena tu nevera", "Compra inicial de básicos antes de tu llegada.", 35),
            ("Cuna para bebé", "Cuna preparada para huéspedes pequeños.", 18),
        ]:
            ExtraService.objects.get_or_create(name=name, defaults={"description": description, "price": price})

        self.stdout.write(self.style.SUCCESS("Datos demo Wynwood cargados correctamente."))

    def _load_static_image(self, image_name):
        path = Path(settings.BASE_DIR) / "staticfiles" / "img" / "figma" / image_name
        return ContentFile(path.read_bytes(), name=image_name)
