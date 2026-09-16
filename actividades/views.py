from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import InscripcionForm
from .models import Actividad, Inscripcion


def listado(request):
    actividades = Actividad.objects.filter(
        activa=True, fecha__gte=timezone.now().date()
    )
    return render(request, "actividades/listado.html", {"actividades": actividades})


def pasadas(request):
    actividades = Actividad.objects.filter(
        activa=True, fecha__lt=timezone.now().date()
    )
    return render(request, "actividades/pasadas.html", {"actividades": actividades})


def detalle(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk, activa=True)
    mensaje_compartir = f"{actividad.titulo} — {request.build_absolute_uri()}"

    if actividad.es_pasada:
        return render(
            request,
            "actividades/detalle.html",
            {"actividad": actividad, "form": None, "mensaje_compartir": mensaje_compartir},
        )

    if request.method == "POST":
        form = InscripcionForm(request.POST, actividad=actividad)
        if form.is_valid():
            inscripcion = form.save()
            if inscripcion.estado == Inscripcion.ESTADO_LISTA_ESPERA:
                messages.info(
                    request,
                    "Los cupos ya están completos: quedaste en lista de espera y "
                    "te avisaremos si se libera un cupo.",
                )
            else:
                messages.success(request, "¡Inscripción confirmada!")
            return redirect("actividad_detalle", pk=pk)
    else:
        form = InscripcionForm(actividad=actividad)

    return render(
        request,
        "actividades/detalle.html",
        {"actividad": actividad, "form": form, "mensaje_compartir": mensaje_compartir},
    )
