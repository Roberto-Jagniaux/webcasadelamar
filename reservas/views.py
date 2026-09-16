import json

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import ReservaForm
from .models import BloqueoFecha


def reservar(request):
    if request.method == "POST":
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
        form = ReservaForm()

    fechas_bloqueadas = list(
        BloqueoFecha.objects.filter(fecha__gte=timezone.now().date())
        .values_list("fecha", flat=True)
    )
    context = {
        "form": form,
        "fechas_bloqueadas_json": json.dumps([f.isoformat() for f in fechas_bloqueadas]),
    }
    return render(request, "reservas/reservar.html", context)
