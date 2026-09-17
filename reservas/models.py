from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    """
    Registro de la persona que solicita una hora o se inscribe a una actividad.
    No requiere cuenta/login (RF-B-08): se crea o reutiliza a partir de
    nombre + correo cada vez que alguien completa un formulario.
    """

    CONVENIO_PARTICULAR = "particular"
    CONVENIO_FONASA = "fonasa"
    CONVENIO_ISAPRE = "isapre"
    CONVENIO_SEGURO = "seguro"
    CONVENIO_CHOICES = [
        (CONVENIO_PARTICULAR, "Particular"),
        (CONVENIO_FONASA, "Fonasa"),
        (CONVENIO_ISAPRE, "Isapre"),
        (CONVENIO_SEGURO, "Seguro"),
    ]

    nombre = models.CharField(max_length=120, verbose_name="Nombre completo")
    email = models.EmailField(verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=30, verbose_name="Teléfono")
    convenio = models.CharField(
        max_length=20,
        choices=CONVENIO_CHOICES,
        default=CONVENIO_PARTICULAR,
        verbose_name="Convenio",
        help_text="Campo informativo, sin validación con la aseguradora (RF-A-06).",
    )
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return f"{self.nombre} ({self.email})"


class Reserva(models.Model):
    """
    Solicitud de hora. Se confirma manualmente por Fabiola (RF-B-02);
    la agenda no restringe días/horarios en esta primera versión (RF-B-01).
    """

    TIPO_PSICOTERAPIA = "psicoterapia_individual"
    TIPO_TALLER_GRUPAL = "taller_grupal"
    TIPO_AUTOCUIDADO = "autocuidado"
    TIPO_SESION_CHOICES = [
        (TIPO_PSICOTERAPIA, "Psicoterapia individual (60 min)"),
        (TIPO_TALLER_GRUPAL, "Taller grupal (180 min)"),
        (TIPO_AUTOCUIDADO, "Autocuidado para equipos (duración a convenir)"),
    ]

    MODALIDAD_ONLINE = "online"
    MODALIDAD_PRESENCIAL = "presencial"
    MODALIDAD_CHOICES = [
        (MODALIDAD_ONLINE, "Online"),
        (MODALIDAD_PRESENCIAL, "Presencial"),
    ]

    ESTADO_PENDIENTE = "pendiente"
    ESTADO_CONFIRMADA = "confirmada"
    ESTADO_CANCELADA = "cancelada"
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente de confirmación"),
        (ESTADO_CONFIRMADA, "Confirmada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="reservas", verbose_name="Cliente"
    )
    tipo_sesion = models.CharField(
        max_length=30, choices=TIPO_SESION_CHOICES, verbose_name="Tipo de sesión"
    )
    modalidad = models.CharField(
        max_length=15, choices=MODALIDAD_CHOICES, verbose_name="Modalidad"
    )
    fecha = models.DateField(verbose_name="Fecha solicitada")
    hora = models.TimeField(verbose_name="Hora solicitada")
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name="Estado",
    )
    notas = models.TextField(blank=True, verbose_name="Notas internas")
    pago_coordinado = models.BooleanField(
        default=False,
        verbose_name="Pago coordinado",
        help_text=(
            "Marcar cuando ya se coordinó el pago con el cliente (transferencia, "
            "link, efectivo, etc.). El MVP no tiene pasarela de pago: esto es "
            "solo un registro manual de Fabiola."
        ),
    )
    creada_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "reserva"
        verbose_name_plural = "reservas"
        ordering = ["-fecha", "-hora"]

    def __str__(self):
        return f"{self.cliente.nombre} — {self.fecha} {self.hora} ({self.get_estado_display()})"


class BloqueoFecha(models.Model):
    """
    Permite a Fabiola bloquear fechas puntuales (vacaciones, feriados,
    imprevistos) sin restringir el resto de la agenda (RF-B-03).
    """

    fecha = models.DateField(unique=True, verbose_name="Fecha bloqueada")
    motivo = models.CharField(max_length=120, blank=True, verbose_name="Motivo")

    class Meta:
        verbose_name = "bloqueo de fecha"
        verbose_name_plural = "bloqueos de fecha"
        ordering = ["fecha"]

    def __str__(self):
        return f"{self.fecha} — {self.motivo or 'sin motivo especificado'}"
