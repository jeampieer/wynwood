from django.contrib import admin

from applications.pages.models import (
    FooterLink,
    LandingBenefit,
    LandingDestination,
    LandingSection,
    LandingService,
    SocialLink,
)
from core.admin import BaseModelAdmin


@admin.register(LandingSection)
class LandingSectionAdmin(BaseModelAdmin):
    list_display = ("section_type", "title_es", "position", "is_active")
    list_filter = ("section_type", "is_active")
    search_fields = ("title_es", "title_en", "body_es", "body_en")


@admin.register(LandingDestination)
class LandingDestinationAdmin(BaseModelAdmin):
    list_display = ("name", "country", "position", "is_active")
    search_fields = ("name", "country")


@admin.register(LandingService)
class LandingServiceAdmin(BaseModelAdmin):
    list_display = ("title_es", "position", "is_active")
    search_fields = ("title_es", "title_en")


@admin.register(LandingBenefit)
class LandingBenefitAdmin(BaseModelAdmin):
    list_display = ("title_es", "position", "is_active")
    search_fields = ("title_es", "title_en", "text_es", "text_en")


@admin.register(FooterLink)
class FooterLinkAdmin(BaseModelAdmin):
    list_display = ("group", "label_es", "position", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("group", "label_es", "label_en")


@admin.register(SocialLink)
class SocialLinkAdmin(BaseModelAdmin):
    list_display = ("name", "position", "is_active")
    search_fields = ("name",)
