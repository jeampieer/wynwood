from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from applications.accounts.models import User
from applications.bookings.models import ExtraService
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

    assert response.status_code == 200
    assert b"HOME EXPERIENCE" in response.content


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
def test_services_page_loads_with_valid_availability(client, property_obj):
    start = timezone.localdate() + timedelta(days=3)
    url = reverse("bookings:services", kwargs={"slug": property_obj.slug})
    response = client.get(f"{url}?check_in={start}&check_out={start + timedelta(days=2)}&guests=1")

    assert response.status_code == 200
    assert "BIENVENIDO A WYNWOOD HOUSE" in response.content.decode()


@pytest.mark.django_db
def test_flexible_checkin_redirects_to_checkout_with_service(client, property_obj):
    ExtraService.objects.create(name="Check-in & Check-out flexible", price=28)
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
    ExtraService.objects.create(name="Servicio de transporte", price=50)
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
