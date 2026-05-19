from io import BytesIO

import pytest
from django.core.files.base import ContentFile
from PIL import Image

from applications.properties.models import City, Property, PropertyImage


@pytest.mark.django_db
def test_property_image_is_converted_to_webp(settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / "test-media"
    city = City.objects.create(name="Bogotá", country="Colombia")
    prop = Property.objects.create(
        city=city,
        name="Image Test",
        slug="image-test",
        neighborhood="Virrey",
        address="Calle 85",
        short_description="Demo",
        description="Demo",
        capacity=2,
        bedrooms=1,
        beds=1,
        bathrooms=1,
        nightly_price=80,
    )
    source = Image.new("RGB", (1800, 1300), "#dad3c8")
    buffer = BytesIO()
    source.save(buffer, format="JPEG")

    image = PropertyImage.objects.create(
        property=prop,
        image=ContentFile(buffer.getvalue(), name="suite.jpg"),
        alt_text="Suite",
    )

    assert image.image.name.endswith(".webp")
    optimized = Image.open(image.image.path)
    assert max(optimized.size) <= 1200
