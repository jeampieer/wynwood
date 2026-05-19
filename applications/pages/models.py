from django.db import models

from core.models import BaseModel


class PositionedContent(BaseModel):
    position = models.PositiveSmallIntegerField(default=0, verbose_name="Posición")

    class Meta:
        abstract = True
        ordering = ["position", "id"]


class LandingSection(PositionedContent):
    HERO = "hero"
    PROMO = "promo"
    DESTINATIONS = "destinations"
    FEATURED = "featured"
    SERVICES = "services"
    EVENTS = "events"
    BENEFITS = "benefits"
    LONG_STAY = "long_stay"
    INVEST = "invest"

    SECTION_CHOICES = [
        (HERO, "Hero"),
        (PROMO, "Promoción"),
        (DESTINATIONS, "Destinos"),
        (FEATURED, "Propiedades destacadas"),
        (SERVICES, "Servicios"),
        (EVENTS, "Eventos"),
        (BENEFITS, "Beneficios"),
        (LONG_STAY, "Largas estadías"),
        (INVEST, "Inversión"),
    ]

    section_type = models.CharField(max_length=40, choices=SECTION_CHOICES, unique=True, verbose_name="Sección")
    eyebrow_es = models.CharField(max_length=160, blank=True, verbose_name="Eyebrow ES")
    eyebrow_en = models.CharField(max_length=160, blank=True, verbose_name="Eyebrow EN")
    title_es = models.CharField(max_length=180, verbose_name="Título ES")
    title_en = models.CharField(max_length=180, verbose_name="Título EN")
    body_es = models.TextField(blank=True, verbose_name="Cuerpo ES")
    body_en = models.TextField(blank=True, verbose_name="Cuerpo EN")
    cta_es = models.CharField(max_length=80, blank=True, verbose_name="CTA ES")
    cta_en = models.CharField(max_length=80, blank=True, verbose_name="CTA EN")
    url = models.CharField(max_length=240, blank=True, verbose_name="URL")
    image = models.CharField(max_length=240, blank=True, verbose_name="Imagen")

    class Meta(PositionedContent.Meta):
        verbose_name = "Sección de landing"
        verbose_name_plural = "Secciones de landing"

    def __str__(self):
        return self.get_section_type_display()

    def localized(self, language):
        suffix = "en" if language == "en" else "es"
        return {
            "eyebrow": getattr(self, f"eyebrow_{suffix}"),
            "title": getattr(self, f"title_{suffix}"),
            "body": getattr(self, f"body_{suffix}"),
            "cta": getattr(self, f"cta_{suffix}"),
            "url": self.url,
            "image": self.image,
        }


class LandingDestination(PositionedContent):
    name = models.CharField(max_length=80, verbose_name="Nombre")
    country = models.CharField(max_length=80, blank=True, verbose_name="País")
    image = models.CharField(max_length=240, verbose_name="Imagen")

    class Meta(PositionedContent.Meta):
        verbose_name = "Destino de landing"
        verbose_name_plural = "Destinos de landing"

    def __str__(self):
        return self.name


class LandingService(PositionedContent):
    title_es = models.CharField(max_length=120, verbose_name="Título ES")
    title_en = models.CharField(max_length=120, verbose_name="Título EN")
    image = models.CharField(max_length=240, verbose_name="Imagen")

    class Meta(PositionedContent.Meta):
        verbose_name = "Servicio visual de landing"
        verbose_name_plural = "Servicios visuales de landing"

    def __str__(self):
        return self.title_es

    def title(self, language):
        return self.title_en if language == "en" else self.title_es


class LandingBenefit(PositionedContent):
    title_es = models.CharField(max_length=140, verbose_name="Título ES")
    title_en = models.CharField(max_length=140, verbose_name="Título EN")
    text_es = models.TextField(blank=True, verbose_name="Texto ES")
    text_en = models.TextField(blank=True, verbose_name="Texto EN")
    image = models.CharField(max_length=240, blank=True, verbose_name="Imagen")

    class Meta(PositionedContent.Meta):
        verbose_name = "Beneficio de landing"
        verbose_name_plural = "Beneficios de landing"

    def __str__(self):
        return self.title_es

    def localized(self, language):
        suffix = "en" if language == "en" else "es"
        return {
            "title": getattr(self, f"title_{suffix}"),
            "text": getattr(self, f"text_{suffix}"),
            "image": self.image,
        }


class FooterLink(PositionedContent):
    group = models.CharField(max_length=80, verbose_name="Grupo")
    label_es = models.CharField(max_length=120, verbose_name="Etiqueta ES")
    label_en = models.CharField(max_length=120, verbose_name="Etiqueta EN")
    url = models.CharField(max_length=240, verbose_name="URL")

    class Meta(PositionedContent.Meta):
        verbose_name = "Enlace de footer"
        verbose_name_plural = "Enlaces de footer"

    def __str__(self):
        return f"{self.group}: {self.label_es}"

    def label(self, language):
        return self.label_en if language == "en" else self.label_es


class SocialLink(PositionedContent):
    name = models.CharField(max_length=80, verbose_name="Nombre")
    url = models.CharField(max_length=240, verbose_name="URL")
    icon = models.CharField(max_length=240, verbose_name="Icono")

    class Meta(PositionedContent.Meta):
        verbose_name = "Red social"
        verbose_name_plural = "Redes sociales"

    def __str__(self):
        return self.name
