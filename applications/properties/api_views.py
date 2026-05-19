from rest_framework.generics import ListAPIView, RetrieveAPIView

from applications.properties.models import Property
from applications.properties.serializers import PropertySerializer


class PropertyListApiView(ListAPIView):
    serializer_class = PropertySerializer

    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True).select_related("city").prefetch_related("amenities", "images")
        city = self.request.query_params.get("city")
        guests = self.request.query_params.get("guests")
        if city:
            queryset = queryset.filter(city__name__icontains=city)
        if guests:
            queryset = queryset.filter(capacity__gte=guests)
        return queryset.distinct()


class PropertyDetailApiView(RetrieveAPIView):
    queryset = Property.objects.filter(is_active=True).select_related("city").prefetch_related("amenities", "images")
    serializer_class = PropertySerializer
    lookup_field = "slug"
