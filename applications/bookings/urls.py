from django.urls import path

from applications.bookings.api_views import MyBookingDetailApiView, MyBookingListApiView
from applications.bookings.views import (
    BookingConfirmationView,
    CheckoutView,
    FlexibleCheckinView,
    ServiceCatalogView,
    TransportServiceView,
)


app_name = "bookings"

urlpatterns = [
    path("services/<slug:slug>/", ServiceCatalogView.as_view(), name="services"),
    path("services/<slug:slug>/flexible-checkin/", FlexibleCheckinView.as_view(), name="flexible-checkin"),
    path("services/<slug:slug>/transport/", TransportServiceView.as_view(), name="transport"),
    path("checkout/<slug:slug>/", CheckoutView.as_view(), name="checkout"),
    path("booking/<int:pk>/confirmation/", BookingConfirmationView.as_view(), name="confirmation"),
    path("api/my-bookings/", MyBookingListApiView.as_view(), name="api-my-bookings"),
    path("api/my-bookings/<int:pk>/", MyBookingDetailApiView.as_view(), name="api-my-booking-detail"),
]
