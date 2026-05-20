from django.db import models

from applications.bookings.models.booking import Booking
from core.models import BaseModel


class PaymentStatusChoices(models.TextChoices):
    PENDING = "pending", "Pendiente"
    PAID = "paid", "Pagado"
    FAILED = "failed", "Fallido"


class Payment(BaseModel):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name="Reserva",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING,
        verbose_name="Estado",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    reference = models.CharField(max_length=80, unique=True, verbose_name="Referencia")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"{self.reference} · {self.get_status_display()}"
