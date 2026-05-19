from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from django.core.management import call_command

from applications.accounts.models import User
from applications.bookings.models import ExtraService, ExtraServiceTypeChoices
from applications.pages.models import LandingSection
from applications.properties.models import City, Property


@pytest.fixture
def property_obj(db):
    city = City.objects.create(name="Bogotá", country="Colombia")
    return Property.objects.create(
        city=city,
        name="Modern Duplex",
        slug="modern-duplex",
        neighborhood="Virrey",
        address="Calle 85",
        short_description="Demo",
        description="Demo property",
        capacity=2,
        bedrooms=1,
        beds=1,
        bathrooms=1,
        nightly_price=80,
        cleaning_fee=20,
        featured=True,
    )


@pytest.mark.django_db
def test_home_page_loads(client, property_obj):
    response = client.get(reverse("pages:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "HOME EXPERIENCE" in content
    assert 'data-promo-countdown' in content
    assert "10% de descuento en estadías seleccionadas" in content
    assert "Reservar ahora" in content


@pytest.mark.django_db
def test_home_page_uses_landing_content_from_database(client, property_obj):
    LandingSection.objects.create(
        section_type=LandingSection.HERO,
        eyebrow_es="Texto administrable",
        eyebrow_en="Managed copy",
        title_es="TITULAR CMS",
        title_en="CMS HEADLINE",
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert "TITULAR CMS" in response.content.decode()


@pytest.mark.django_db
def test_home_page_renders_english_copy(client, property_obj):
    LandingSection.objects.create(
        section_type=LandingSection.FEATURED,
        title_es="Propiedades desde DB",
        title_en="DB featured homes",
        body_es="Texto ES",
        body_en="English body",
    )
    session = client.session
    session["site_language"] = "en"
    session.save()

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert "DB featured homes" in response.content.decode()


@pytest.mark.django_db
def test_search_filters_by_guest_capacity(client, property_obj):
    response = client.get(reverse("properties:search"), {"guests": 3})

    assert response.status_code == 200
    assert property_obj.name.encode() not in response.content


@pytest.mark.django_db
def test_detail_posts_available_dates_redirects_to_services(client, property_obj):
    start = timezone.localdate() + timedelta(days=3)
    response = client.post(
        property_obj.get_absolute_url(),
        {"check_in": start, "check_out": start + timedelta(days=2), "guests": 1},
    )

    assert response.status_code == 302
    assert "/services/modern-duplex/" in response["Location"]


@pytest.mark.django_db
def test_detail_shows_field_errors_for_invalid_dates(client, property_obj):
    today = timezone.localdate()
    response = client.post(
        property_obj.get_absolute_url(),
        {"check_in": today, "check_out": today, "guests": 1},
    )

    assert response.status_code == 200
    assert "La salida debe ser posterior" in response.content.decode()


@pytest.mark.django_db
def test_detail_renders_fallback_when_property_has_no_images(client, property_obj):
    response = client.get(property_obj.get_absolute_url())

    assert response.status_code == 200
    assert "wh-image-placeholder" in response.content.decode()


@pytest.mark.django_db
def test_seeded_property_detail_renders_media_images(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_demo_data")
    response = client.get(
        reverse("properties:detail", kwargs={"slug": "modern-duplex-parque-virrey"})
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert content.count("/media/properties/images/") >= 3
    assert "wh-image-placeholder" not in content


@pytest.mark.django_db
def test_services_page_loads_with_valid_availability(client, property_obj):
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:services", kwargs={"slug": property_obj.slug})
    response = client.get(
        f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1"
    )

    assert response.status_code == 200
    assert "BIENVENIDO A WYNWOOD HOUSE" in response.content.decode()


@pytest.mark.django_db
def test_flexible_checkin_redirects_to_checkout_with_service(client, property_obj):
    ExtraService.objects.create(
        name="Check-in & Check-out flexible",
        service_type=ExtraServiceTypeChoices.CHECKIN,
        price=28,
    )
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:flexible-checkin", kwargs={"slug": property_obj.slug})
    response = client.post(
        f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1",
        {"arrival_time": "14:30", "departure_time": "11:00"},
    )

    assert response.status_code == 302
    assert "/checkout/modern-duplex/" in response["Location"]
    assert "services=" in response["Location"]


@pytest.mark.django_db
def test_transport_redirects_to_checkout_with_service(client, property_obj):
    ExtraService.objects.create(
        name="Servicio de transporte",
        service_type=ExtraServiceTypeChoices.TRANSPORT,
        price=50,
    )
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:transport", kwargs={"slug": property_obj.slug})
    response = client.post(
        f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1",
        {
            "transfer_type": "airport_property",
            "pickup_address": "Aeropuerto",
            "passengers": 1,
        },
    )

    assert response.status_code == 302
    assert "/checkout/modern-duplex/" in response["Location"]
    assert "services=" in response["Location"]


@pytest.mark.django_db
def test_checkout_creates_user_booking_and_payment(client, property_obj, mailoutbox):
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:checkout", kwargs={"slug": property_obj.slug})
    response = client.post(
        f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1",
        {
            "email": "newguest@example.com",
            "full_name": "New Guest",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "phone": "+51 999 999 999",
            "nationality": "Peru",
        },
    )

    assert response.status_code == 302
    assert User.objects.filter(email="newguest@example.com").exists()
    assert len(mailoutbox) == 1


@pytest.mark.django_db
def test_checkout_rejects_duplicate_email(client, property_obj):
    User.objects.create_user(email="taken@example.com", password="StrongPass123")
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:checkout", kwargs={"slug": property_obj.slug})
    response = client.post(
        f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1",
        {
            "email": "taken@example.com",
            "full_name": "Taken Guest",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        },
    )

    assert response.status_code == 200
    assert "Ya existe una cuenta" in response.content.decode()


@pytest.mark.django_db
def test_checkout_rejects_password_mismatch(client, property_obj):
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:checkout", kwargs={"slug": property_obj.slug})
    response = client.post(
        f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1",
        {
            "email": "mismatch@example.com",
            "full_name": "Mismatch Guest",
            "password1": "StrongPass123",
            "password2": "DifferentPass123",
        },
    )

    assert response.status_code == 200
    assert "Las contraseñas no coinciden" in response.content.decode()
    assert not User.objects.filter(email="mismatch@example.com").exists()


@pytest.mark.django_db
def test_properties_api_v1_uses_standard_response(client, property_obj):
    response = client.get("/api/v1/properties/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"][0]["slug"] == property_obj.slug


@pytest.mark.django_db
def test_my_bookings_api_v1_requires_authentication(client):
    response = client.get("/api/v1/bookings/my-bookings/")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_extra_service_type_controls_service_option(client, property_obj):
    service = ExtraService.objects.create(
        name="Nombre sin palabra clave",
        service_type=ExtraServiceTypeChoices.TRANSPORT,
        price=50,
    )
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:services", kwargs={"slug": property_obj.slug})
    response = client.get(
        f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1"
    )

    assert response.status_code == 200
    assert service.name in response.content.decode()
    assert (
        reverse("bookings:transport", kwargs={"slug": property_obj.slug})
        in response.content.decode()
    )


@pytest.mark.django_db
def test_checkout_service_images_follow_service_type(client, property_obj):
    service = ExtraService.objects.create(
        name="Traslado premium",
        service_type=ExtraServiceTypeChoices.TRANSPORT,
        price=50,
    )
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:checkout", kwargs={"slug": property_obj.slug})
    response = client.get(
        f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1&services={service.pk}"
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert "img/figma/service-transport.webp" in content
    assert "img/figma/service-checkin.webp" not in content
