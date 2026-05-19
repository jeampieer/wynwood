from django.db import models

from core.models import BaseModel


class Amenity(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    icon = models.CharField(max_length=40, blank=True, verbose_name="Icono")

    class Meta:
        verbose_name = "Comodidad"
        verbose_name_plural = "Comodidades"
        ordering = ["name"]

    def __str__(self):
        return self.name
