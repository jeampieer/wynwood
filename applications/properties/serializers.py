from rest_framework import serializers

from applications.properties.models import Amenity, City, Property, PropertyImage


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "country"]


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name", "icon"]


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "image", "alt_text", "is_cover"]


class PropertySerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "name",
            "slug",
            "city",
            "neighborhood",
            "address",
            "short_description",
            "description",
            "capacity",
            "bedrooms",
            "beds",
            "bathrooms",
            "nightly_price",
            "cleaning_fee",
            "featured",
            "amenities",
            "images",
        ]
