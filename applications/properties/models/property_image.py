import uuid
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.db import models
from PIL import Image

from core.models import BaseModel


def upload_property_image(instance, filename):
    uid = str(uuid.uuid4())[:8]
    return f"properties/images/{uid}.webp"


class PropertyImage(BaseModel):
    property = models.ForeignKey(
        "properties.Property",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Propiedad",
    )
    image = models.ImageField(upload_to=upload_property_image, verbose_name="Imagen")
    alt_text = models.CharField(max_length=160, blank=True, verbose_name="Texto alternativo")
    is_cover = models.BooleanField(default=False, verbose_name="Portada")

    class Meta:
        verbose_name = "Imagen de propiedad"
        verbose_name_plural = "Imágenes de propiedades"
        ordering = ["-is_cover", "created"]

    def __str__(self):
        return self.alt_text or f"Imagen de {self.property}"

    def save(self, *args, **kwargs):
        if self.image and self._should_optimize_image():
            self.image = self._optimize_to_webp(self.image)
        super().save(*args, **kwargs)

    def _should_optimize_image(self):
        if not self.pk:
            return True
        if not getattr(self.image, "_committed", True):
            return True
        try:
            previous = type(self).objects.only("image").get(pk=self.pk)
        except type(self).DoesNotExist:
            return True
        return previous.image.name != self.image.name

    def _optimize_to_webp(self, uploaded_file):
        image = Image.open(uploaded_file)
        image = image.convert("RGB")
        image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        buffer = BytesIO()
        image.save(buffer, format="WEBP", quality=84, method=6)
        filename = f"{Path(uploaded_file.name).stem or uuid.uuid4().hex[:8]}.webp"
        return ContentFile(buffer.getvalue(), name=filename)
