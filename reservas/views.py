import json

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from core.ratelimit import demasiados_intentos

from .forms import ReservaForm
from .models import BloqueoFecha, Reserva


def reservar(request):
    if request.method == "POST":
        if demasiados_intentos(request, "reservar"):
            messages.error(
                request,
                "Recibimos demasiadas solicitudes desde tu conexión en poco "
                "tiempo. Espera unos minutos e inténtalo de nuevo.",
            )
            return redirect("reservar")
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "¡Listo! Recibimos tu solicitud de hora. Fabiola se pondrá en "
                "contacto para confirmarla y coordinar el pago.",
            )
            return redirect("reservar")
    else:
        tipo_preseleccionado = request.GET.get("tipo")
        initial = {}
        if tipo_preseleccionado in dict(Reserva.TIPO_SESION_CHOICES):
            initial["tipo_sesion"] = tipo_preseleccionado
        form = ReservaForm(initial=initial)

    fechas_bloqueadas = list(
        BloqueoFecha.objects.filter(fecha__gte=timezone.now().date())
        .values_list("fecha", flat=True)
    )
    context = {
        "form": form,
        "fechas_bloqueadas_json": json.dumps([f.isoformat() for f in fechas_bloqueadas]),
    }
    return render(request, "reservas/reservar.html", context)
