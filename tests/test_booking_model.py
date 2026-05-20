from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from applications.accounts.models import User
from applications.bookings.models import Booking
from applications.properties.models import City, Property


@pytest.fixture
def user(db):
    return User.objects.create_user(email="guest@example.com", password="StrongPass123")


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
    )


@pytest.mark.django_db
def test_booking_rejects_past_dates(user, property_obj):
    yesterday = timezone.localdate() - timedelta(days=1)
    tomorrow = timezone.localdate() + timedelta(days=1)
    booking = Booking(guest=user, property=property_obj, check_in=yesterday, check_out=tomorrow, guests=1)

    with pytest.raises(ValidationError):
        booking.full_clean()


@pytest.mark.django_db
def test_booking_rejects_checkout_before_checkin(user, property_obj):
    tomorrow = timezone.localdate() + timedelta(days=1)
    booking = Booking(guest=user, property=property_obj, check_in=tomorrow, check_out=tomorrow, guests=1)

    with pytest.raises(ValidationError):
        booking.full_clean()


@pytest.mark.django_db
def test_booking_rejects_overlapping_dates(user, property_obj):
    start = timezone.localdate() + timedelta(days=5)
    end = start + timedelta(days=3)
    Booking.objects.create(guest=user, property=property_obj, check_in=start, check_out=end, guests=1)
    overlap = Booking(guest=user, property=property_obj, check_in=start + timedelta(days=1), check_out=end, guests=1)

    with pytest.raises(ValidationError):
        overlap.full_clean()


@pytest.mark.django_db
def test_booking_calculates_totals(user, property_obj):
    start = timezone.localdate() + timedelta(days=2)
    booking = Booking(guest=user, property=property_obj, check_in=start, check_out=start + timedelta(days=2), guests=1)
    booking.calculate_totals([])

    assert booking.subtotal == 160
    assert booking.cleaning_fee == 20
    assert booking.total > booking.subtotal
