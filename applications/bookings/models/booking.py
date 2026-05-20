from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from applications.bookings.models.extra_service import ExtraService
from applications.properties.models import Property
from core.models import BaseModel


class BookingStatusChoices(models.TextChoices):
    PENDING = "pending", "Pendiente"
    CONFIRMED = "confirmed", "Confirmada"
    CANCELLED = "cancelled", "Cancelada"


class Booking(BaseModel):
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Huésped",
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Propiedad",
    )
    extra_services = models.ManyToManyField(
        ExtraService,
        blank=True,
        related_name="bookings",
        verbose_name="Servicios adicionales",
    )
    check_in = models.DateField(verbose_name="Llegada")
    check_out = models.DateField(verbose_name="Salida")
    guests = models.PositiveSmallIntegerField(verbose_name="Huéspedes")
    status = models.CharField(
        max_length=20,
        choices=BookingStatusChoices.choices,
        default=BookingStatusChoices.PENDING,
        verbose_name="Estado",
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal")
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Tarifa de limpieza")
    extras_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total servicios")
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Impuestos")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total")

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.property} · {self.check_in} - {self.check_out}"

    def nights(self):
        return max((self.check_out - self.check_in).days, 0)

    def clean(self):
        today = timezone.localdate()
        if self.check_in and self.check_in < today:
            raise ValidationError({"check_in": "La llegada no puede estar en el pasado."})
        if self.check_out and self.check_out < today:
            raise ValidationError({"check_out": "La salida no puede estar en el pasado."})
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValidationError({"check_out": "La salida debe ser posterior a la llegada."})
        if self.property_id and self.guests and self.guests > self.property.capacity:
            raise ValidationError({"guests": "La propiedad no admite esa cantidad de huéspedes."})
        if self.property_id and self.check_in and self.check_out:
            overlaps = Booking.objects.filter(
                property=self.property,
                status__in=[BookingStatusChoices.PENDING, BookingStatusChoices.CONFIRMED],
                check_in__lt=self.check_out,
                check_out__gt=self.check_in,
            )
            if self.pk:
                overlaps = overlaps.exclude(pk=self.pk)
            if overlaps.exists():
                raise ValidationError("La propiedad ya tiene una reserva para esas fechas.")

    def calculate_totals(self, extras=None):
        extras = extras or []
        self.subtotal = self.property.nightly_price * Decimal(self.nights())
        self.cleaning_fee = self.property.cleaning_fee
        self.extras_total = sum((service.price for service in extras), Decimal("0"))
        self.discount = Decimal("18.00") if self.subtotal >= Decimal("300.00") else Decimal("0")
        taxable = self.subtotal + self.cleaning_fee + self.extras_total - self.discount
        self.taxes = (taxable * Decimal("0.16")).quantize(Decimal("0.01"))
        self.total = taxable + self.taxes
