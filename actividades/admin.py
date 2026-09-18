from django.contrib import admin
from .models import Actividad, Inscripcion


class InscripcionInline(admin.TabularInline):
    model = Inscripcion
    extra = 0
    readonly_fields = ("cliente", "estado", "creada_en")


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = (
        "titulo", "tipo", "fecha", "tipo_retribucion", "valor",
        "cupos", "cupos_disponibles", "en_lista_espera", "activa",
    )
    list_filter = ("tipo", "tipo_retribucion", "activa")
    search_fields = ("titulo", "descripcion")
    date_hierarchy = "fecha"
    inlines = [InscripcionInline]

    def get_queryset(self, request):
        # cupos_disponibles y en_lista_espera del list_display disparaban un
        # query por fila; con_conteos() los precalcula en un solo query.
        return super().get_queryset(request).con_conteos()


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("cliente", "actividad", "estado", "creada_en")
    list_filter = ("estado", "actividad")
    search_fields = ("cliente__nombre", "actividad__titulo")
    actions = ["cancelar_y_promover"]

    @admin.action(
        description="Cancelar inscripción (promueve automáticamente a quien siga en lista de espera)"
    )
    def cancelar_y_promover(self, request, queryset):
        for inscripcion in queryset.exclude(estado=Inscripcion.ESTADO_CANCELADA):
            inscripcion.cancelar()
