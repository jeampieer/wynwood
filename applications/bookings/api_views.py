from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from applications.bookings.models import Booking
from applications.bookings.serializers import BookingSerializer
from core.api.responses import ApiResponse


class MyBookingListApiView(ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related("property", "payment")

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.filter_queryset(self.get_queryset()), many=True)
        return ApiResponse.success(serializer.data)


class MyBookingDetailApiView(RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related("property", "payment")

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return ApiResponse.success(serializer.data)
