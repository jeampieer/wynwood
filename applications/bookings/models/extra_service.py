from django.db import models

from core.models import BaseModel


class ExtraServiceTypeChoices(models.TextChoices):
    CHECKIN = "checkin", "Check-in flexible"
    TRANSPORT = "transport", "Transporte"
    FRIDGE = "fridge", "Llena tu nevera"
    CRIB = "crib", "Cuna"
    OTHER = "other", "Otro"


class ExtraService(BaseModel):
    name = models.CharField(max_length=120, verbose_name="Nombre")
    description = models.CharField(max_length=220, blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    service_type = models.CharField(
        max_length=30,
        choices=ExtraServiceTypeChoices.choices,
        default=ExtraServiceTypeChoices.OTHER,
        verbose_name="Tipo de servicio",
    )
    image = models.CharField(max_length=240, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Servicio adicional"
        verbose_name_plural = "Servicios adicionales"
        ordering = ["service_type", "name"]

    def __str__(self):
        return self.name

    def display_image(self):
        if self.image:
            return self.image
        return {
            ExtraServiceTypeChoices.CHECKIN: "img/figma/service-checkin.webp",
            ExtraServiceTypeChoices.TRANSPORT: "img/figma/service-transport.webp",
            ExtraServiceTypeChoices.FRIDGE: "img/figma/service-fridge.webp",
            ExtraServiceTypeChoices.CRIB: "img/figma/service-crib.webp",
            ExtraServiceTypeChoices.OTHER: "img/figma/service-crib.webp",
        }[self.service_type]
