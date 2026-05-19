from django.db import models

from core.models import BaseModel


class ExtraService(BaseModel):
    name = models.CharField(max_length=120, verbose_name="Nombre")
    description = models.CharField(max_length=220, blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")

    class Meta:
        verbose_name = "Servicio adicional"
        verbose_name_plural = "Servicios adicionales"
        ordering = ["name"]

    def __str__(self):
        return self.name
