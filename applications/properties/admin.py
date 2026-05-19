from django.contrib import admin

from core.admin import BaseModelAdmin
from applications.properties.models import Amenity, City, Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ("image", "alt_text", "is_cover")


@admin.register(City)
class CityAdmin(BaseModelAdmin):
    list_display = ("name", "country", "is_active")
    search_fields = ("name", "country")


@admin.register(Amenity)
class AmenityAdmin(BaseModelAdmin):
    list_display = ("name", "icon", "is_active")
    search_fields = ("name",)


@admin.register(Property)
class PropertyAdmin(BaseModelAdmin):
    list_display = ("name", "city", "nightly_price", "capacity", "featured", "is_active")
    list_filter = ("city", "featured", "is_active")
    search_fields = ("name", "neighborhood", "address")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("amenities",)
    inlines = [PropertyImageInline]


@admin.register(PropertyImage)
class PropertyImageAdmin(BaseModelAdmin):
    list_display = ("property", "alt_text", "is_cover", "is_active")
    list_filter = ("is_cover", "is_active")
    search_fields = ("property__name", "alt_text")
