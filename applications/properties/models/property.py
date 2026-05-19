from django.db import models
from django.urls import reverse

from core.models import BaseModel


class Property(BaseModel):
    city = models.ForeignKey(
        "properties.City",
        on_delete=models.PROTECT,
        related_name="properties",
        verbose_name="Ciudad",
    )
    amenities = models.ManyToManyField(
        "properties.Amenity",
        related_name="properties",
        blank=True,
        verbose_name="Comodidades",
    )
    name = models.CharField(max_length=180, verbose_name="Nombre")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    neighborhood = models.CharField(max_length=120, verbose_name="Barrio")
    address = models.CharField(max_length=220, verbose_name="Dirección")
    short_description = models.CharField(max_length=240, verbose_name="Descripción corta")
    description = models.TextField(verbose_name="Descripción")
    capacity = models.PositiveSmallIntegerField(default=2, verbose_name="Capacidad")
    bedrooms = models.PositiveSmallIntegerField(default=1, verbose_name="Habitaciones")
    beds = models.PositiveSmallIntegerField(default=1, verbose_name="Camas")
    bathrooms = models.PositiveSmallIntegerField(default=1, verbose_name="Baños")
    nightly_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por noche")
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, default=54, verbose_name="Tarifa de limpieza")
    featured = models.BooleanField(default=False, verbose_name="Destacada")

    class Meta:
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"
        ordering = ["-featured", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("properties:detail", kwargs={"slug": self.slug})

    @property
    def cover_image(self):
        return self.images.filter(is_cover=True).first() or self.images.first()
