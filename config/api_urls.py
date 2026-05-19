from django.urls import path

from applications.bookings.api_views import MyBookingDetailApiView, MyBookingListApiView
from applications.properties.api_views import PropertyDetailApiView, PropertyListApiView


app_name = "api_v1"

urlpatterns = [
    path("properties/", PropertyListApiView.as_view(), name="property-list"),
    path("properties/<slug:slug>/", PropertyDetailApiView.as_view(), name="property-detail"),
    path("bookings/my-bookings/", MyBookingListApiView.as_view(), name="my-bookings"),
    path("bookings/my-bookings/<int:pk>/", MyBookingDetailApiView.as_view(), name="my-booking-detail"),
]
