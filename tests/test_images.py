from io import BytesIO
from pathlib import Path

import pytest
from django.core.files.base import ContentFile
from django.core.management import call_command
from PIL import Image

from applications.properties.models import City, Property, PropertyImage


@pytest.mark.django_db
def test_property_image_is_converted_to_webp(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
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


@pytest.mark.django_db
def test_property_image_large_webp_is_resized(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    city = City.objects.create(name="Lima", country="Perú")
    prop = Property.objects.create(
        city=city,
        name="Large WebP",
        slug="large-webp",
        neighborhood="Barranco",
        address="Calle 1",
        short_description="Demo",
        description="Demo",
        capacity=2,
        bedrooms=1,
        beds=1,
        bathrooms=1,
        nightly_price=90,
    )
    source = Image.new("RGB", (2200, 1400), "#c7d7d1")
    buffer = BytesIO()
    source.save(buffer, format="WEBP")

    image = PropertyImage.objects.create(
        property=prop,
        image=ContentFile(buffer.getvalue(), name="large-suite.webp"),
        alt_text="Large suite",
    )

    optimized = Image.open(image.image.path)
    assert image.image.name.endswith(".webp")
    assert max(optimized.size) <= 1200


@pytest.mark.django_db
def test_seed_demo_data_repairs_missing_property_image_files(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_demo_data")
    prop = Property.objects.get(slug="modern-duplex-parque-virrey")
    first_image = prop.images.first()
    missing_path = first_image.image.path
    first_image.image.storage.delete(first_image.image.name)

    assert not Path(missing_path).exists()

    call_command("seed_demo_data")
    prop.refresh_from_db()
    images = list(prop.images.all())

    assert len(images) == 3
    assert all(image.image.storage.exists(image.image.name) for image in images)
