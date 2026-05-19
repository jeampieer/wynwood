from django.contrib import admin

from applications.bookings.models import Booking, ExtraService, Payment
from core.admin import BaseModelAdmin


@admin.register(ExtraService)
class ExtraServiceAdmin(BaseModelAdmin):
    list_display = ("name", "service_type", "price", "is_active")
    list_filter = ("service_type", "is_active")
    search_fields = ("name",)


@admin.register(Booking)
class BookingAdmin(BaseModelAdmin):
    list_display = ("property", "user", "check_in", "check_out", "guests", "status", "total")
    list_filter = ("status", "check_in", "is_active")
    search_fields = ("property__name", "user__email")
    filter_horizontal = ("extra_services",)


@admin.register(Payment)
class PaymentAdmin(BaseModelAdmin):
    list_display = ("reference", "booking", "status", "amount", "created")
    list_filter = ("status", "created")
    search_fields = ("reference", "booking__user__email", "booking__property__name")
