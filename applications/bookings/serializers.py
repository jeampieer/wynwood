from rest_framework import serializers

from applications.bookings.models import Booking, Payment


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "status", "status_display", "amount", "reference", "created"]


class BookingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "property",
            "user",
            "check_in",
            "check_out",
            "guests",
            "status",
            "status_display",
            "subtotal",
            "cleaning_fee",
            "extras_total",
            "taxes",
            "discount",
            "total",
            "payment",
        ]
        read_only_fields = ["subtotal", "cleaning_fee", "extras_total", "taxes", "discount", "total"]
