from django.db import models
from django.utils import timezone
from reservas.models import Cliente


class Actividad(models.Model):
    """
    Publicación de una actividad (RF-C-01/02). El tipo de retribución se
    configura por publicación (RF-C-04), no como regla fija del sistema.
    """

    TIPO_AUTOCUIDADO = "autocuidado"
    TIPO_TALLER_SALUD_MENTAL = "taller_salud_mental"
    TIPO_PSICOTERAPIA_INDIVIDUAL = "psicoterapia_individual"
    TIPO_ESCUELA_BUEN_TRATO = "escuela_buen_trato"
    TIPO_CHOICES = [
        (TIPO_AUTOCUIDADO, "Autocuidado"),
        (TIPO_TALLER_SALUD_MENTAL, "Taller de salud mental"),
        (TIPO_PSICOTERAPIA_INDIVIDUAL, "Psicoterapia individual"),
        (TIPO_ESCUELA_BUEN_TRATO, "Escuela del buen trato"),
    ]

    RETRIBUCION_GRATIS = "gratis"
    RETRIBUCION_PAGO = "pago"
    RETRIBUCION_DONACION = "donacion"
    RETRIBUCION_CHOICES = [
        (RETRIBUCION_GRATIS, "Gratis"),
        (RETRIBUCION_PAGO, "Pago"),
        (RETRIBUCION_DONACION, "Donación"),
    ]

    titulo = models.CharField(max_length=150, verbose_name="Título")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de actividad")
    descripcion = models.TextField(verbose_name="Descripción")
    publico_objetivo = models.CharField(max_length=150, verbose_name="Público objetivo")
    fecha = models.DateField(verbose_name="Fecha")
    hora = models.TimeField(verbose_name="Hora")
    lugar_modalidad = models.CharField(
        max_length=150, verbose_name="Lugar o modalidad"
    )
    cupos = models.PositiveIntegerField(verbose_name="Cupos totales")
    fecha_cierre_inscripciones = models.DateField(
        verbose_name="Fecha de cierre de inscripciones"
    )
    imagen = models.ImageField(upload_to="actividades", null=True, blank=True)
    tipo_retribucion = models.CharField(
        max_length=15,
        choices=RETRIBUCION_CHOICES,
        default=RETRIBUCION_GRATIS,
        verbose_name="Tipo de retribución",
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Valor (si es pago o sugerencia de donación)",
    )
    activa = models.BooleanField(default=True, verbose_name="Publicada")
    creada_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "actividad"
        verbose_name_plural = "actividades"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.titulo} ({self.fecha})"

    @property
    def cupos_ocupados(self):
        return self.inscripciones.filter(estado=Inscripcion.ESTADO_CONFIRMADA).count()

    @property
    def cupos_disponibles(self):
        return max(self.cupos - self.cupos_ocupados, 0)

    @property
    def en_lista_espera(self):
        return self.inscripciones.filter(estado=Inscripcion.ESTADO_LISTA_ESPERA).count()

    @property
    def es_pasada(self):
        return self.fecha < timezone.now().date()


class Inscripcion(models.Model):
    """
    Inscripción de un cliente a una actividad. Si se agotan los cupos,
    se ofrece lista de espera en vez de cerrar la inscripción (RF-C-08).
    """

    ESTADO_CONFIRMADA = "confirmada"
    ESTADO_LISTA_ESPERA = "lista_espera"
    ESTADO_CANCELADA = "cancelada"
    ESTADO_CHOICES = [
        (ESTADO_CONFIRMADA, "Confirmada"),
        (ESTADO_LISTA_ESPERA, "Lista de espera"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    actividad = models.ForeignKey(
        Actividad, on_delete=models.CASCADE, related_name="inscripciones"
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="inscripciones"
    )
    estado = models.CharField(
        max_length=15, choices=ESTADO_CHOICES, default=ESTADO_CONFIRMADA
    )
    creada_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "inscripción"
        verbose_name_plural = "inscripciones"
        unique_together = ("actividad", "cliente")

    def save(self, *args, **kwargs):
        # Si ya no hay cupos disponibles, la inscripción entra en lista de espera.
        if self.pk is None and self.estado == self.ESTADO_CONFIRMADA:
            if self.actividad.cupos_disponibles <= 0:
                self.estado = self.ESTADO_LISTA_ESPERA
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente.nombre} → {self.actividad.titulo} ({self.get_estado_display()})"

    def cancelar(self):
        """
        Cancela la inscripción. Si estaba confirmada, promueve automáticamente
        a la primera persona en lista de espera (por orden de inscripción),
        para no dejar la promoción como un paso manual (RF-C-08).
        """
        era_confirmada = self.estado == self.ESTADO_CONFIRMADA
        self.estado = self.ESTADO_CANCELADA
        self.save(update_fields=["estado"])

        if era_confirmada:
            siguiente = (
                Inscripcion.objects.filter(
                    actividad=self.actividad, estado=self.ESTADO_LISTA_ESPERA
                )
                .order_by("creada_en")
                .first()
            )
            if siguiente:
                siguiente.estado = self.ESTADO_CONFIRMADA
                siguiente.save(update_fields=["estado"])
        return self
