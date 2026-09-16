from django.db import models
from django.utils import timezone
from reservas.models import Reserva
from actividades.models import Inscripcion


class Producto(models.Model):
    """
    Modelo genérico preparado para la Fase 5 del plan (venta de productos
    y/o sesiones empaquetadas). No se usa activamente en el MVP: hoy el
    pago se coordina manualmente (RF-B-04/05). `activo=False` por defecto
    para que no aparezca en ningún listado público todavía.
    """

    TIPO_SERVICIO = "servicio"
    TIPO_PRODUCTO_FISICO = "producto_fisico"
    TIPO_CHOICES = [
        (TIPO_SERVICIO, "Servicio / sesión"),
        (TIPO_PRODUCTO_FISICO, "Producto físico"),
    ]

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_SERVICIO)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    activo = models.BooleanField(
        default=False,
        verbose_name="Activo para venta",
        help_text="Se mantiene en False hasta activar venta de productos (Fase 5).",
    )
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return self.nombre


class Transaccion(models.Model):
    """
    Registro de un intento/resultado de pago. Se vincula opcionalmente a una
    Reserva, una Inscripción o un Producto, para que cuando se integre una
    pasarela real (Webpay/Mercado Pago) no haya que rediseñar el modelo.
    Hoy (MVP) no se usa: el pago se coordina manualmente fuera del sitio.
    """

    MEDIO_MANUAL = "manual"
    MEDIO_WEBPAY = "webpay"
    MEDIO_MERCADOPAGO = "mercadopago"
    MEDIO_TRANSFERENCIA = "transferencia"
    MEDIO_CHOICES = [
        (MEDIO_MANUAL, "Coordinado manualmente"),
        (MEDIO_WEBPAY, "Webpay"),
        (MEDIO_MERCADOPAGO, "Mercado Pago"),
        (MEDIO_TRANSFERENCIA, "Transferencia"),
    ]

    ESTADO_PENDIENTE = "pendiente"
    ESTADO_PAGADO = "pagado"
    ESTADO_FALLIDO = "fallido"
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_PAGADO, "Pagado"),
        (ESTADO_FALLIDO, "Fallido"),
    ]

    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, blank=True, related_name="transacciones"
    )
    reserva = models.ForeignKey(
        Reserva, on_delete=models.SET_NULL, null=True, blank=True, related_name="transacciones"
    )
    inscripcion = models.ForeignKey(
        Inscripcion, on_delete=models.SET_NULL, null=True, blank=True, related_name="transacciones"
    )
    monto = models.DecimalField(max_digits=10, decimal_places=0)
    medio_pago = models.CharField(max_length=20, choices=MEDIO_CHOICES, default=MEDIO_MANUAL)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    referencia_externa = models.CharField(
        max_length=100, blank=True,
        help_text="ID de transacción de la pasarela de pago, cuando se integre.",
    )
    creada_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "transacción"
        verbose_name_plural = "transacciones"
        ordering = ["-creada_en"]

    def __str__(self):
        return f"{self.get_medio_pago_display()} — ${self.monto} ({self.get_estado_display()})"
