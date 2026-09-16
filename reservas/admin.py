from django.contrib import admin
from django.utils.html import format_html

from .models import Cliente, Reserva, BloqueoFecha
from .services import whatsapp_link_pago


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "convenio", "creado_en")
    search_fields = ("nombre", "email", "telefono")
    list_filter = ("convenio",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "cliente", "tipo_sesion", "modalidad", "fecha", "hora", "estado",
        "pago_coordinado", "coordinar_pago",
    )
    list_filter = ("estado", "pago_coordinado", "tipo_sesion", "modalidad")
    search_fields = ("cliente__nombre", "cliente__email")
    date_hierarchy = "fecha"
    actions = ["marcar_confirmada", "marcar_cancelada", "marcar_pago_coordinado"]
    readonly_fields = ("link_whatsapp_pago",)
    fields = (
        "cliente", "tipo_sesion", "modalidad", "fecha", "hora", "estado",
        "pago_coordinado", "link_whatsapp_pago", "notas",
    )

    @admin.action(description="Marcar como confirmada")
    def marcar_confirmada(self, request, queryset):
        queryset.update(estado=Reserva.ESTADO_CONFIRMADA)

    @admin.action(description="Marcar como cancelada")
    def marcar_cancelada(self, request, queryset):
        queryset.update(estado=Reserva.ESTADO_CANCELADA)

    @admin.action(description="Marcar pago como coordinado")
    def marcar_pago_coordinado(self, request, queryset):
        queryset.update(pago_coordinado=True)

    @admin.display(description="Coordinar pago")
    def coordinar_pago(self, reserva):
        link = whatsapp_link_pago(reserva)
        if not link:
            return "sin teléfono"
        return format_html('<a href="{}" target="_blank">WhatsApp</a>', link)

    @admin.display(description="Link de WhatsApp para coordinar el pago")
    def link_whatsapp_pago(self, reserva):
        if not reserva.pk:
            return "Disponible después de guardar la reserva."
        link = whatsapp_link_pago(reserva)
        if not link:
            return "El cliente no tiene teléfono registrado."
        return format_html(
            '<a href="{}" target="_blank">Abrir WhatsApp con mensaje pre-armado</a>',
            link,
        )


@admin.register(BloqueoFecha)
class BloqueoFechaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "motivo")
