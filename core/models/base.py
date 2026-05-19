from django.db import models


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    modified = models.DateTimeField(auto_now=True, verbose_name="Modificado")

    class Meta:
        abstract = True
        ordering = ["-created"]
