from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone

from actividades.models import Actividad
from reservas.models import Reserva
from reservas.services import whatsapp_link_pago

# Create your views here.


@staff_member_required
def panel(request):
    reservas_pendientes = Reserva.objects.filter(
        estado=Reserva.ESTADO_PENDIENTE
    ).order_by("fecha", "hora")

    reservas_sin_pago = Reserva.objects.filter(
        estado=Reserva.ESTADO_CONFIRMADA, pago_coordinado=False
    ).order_by("fecha", "hora")

    for reserva in reservas_sin_pago:
        reserva.link_whatsapp = whatsapp_link_pago(reserva)

    actividades_con_espera = [
        actividad
        for actividad in Actividad.objects.filter(
            activa=True, fecha__gte=timezone.now().date()
        )
        if actividad.en_lista_espera > 0
    ]

    return render(
        request,
        "core/panel.html",
        {
            "reservas_pendientes": reservas_pendientes,
            "reservas_sin_pago": reservas_sin_pago,
            "actividades_con_espera": actividades_con_espera,
        },
    )

def psicoterapia(request):
    return render(request,"core/psicoterapia.html")

def autocuidado(request):
    return render(request,"core/autocuidado.html")

def inicio(request):
    return render(request,"core/inicio.html")

def escuelaparaelbuentrato(request):
    return render(request,"core/escuelaparaelbuentrato.html")



def contact(request):
    return render(request,"core/contact.html")