from django.db import models

from core.models import BaseModel


class City(BaseModel):
    name = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    country = models.CharField(max_length=120, default="Colombia", verbose_name="País")

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.country}"
