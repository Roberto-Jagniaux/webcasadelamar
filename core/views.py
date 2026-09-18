from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone

from actividades.models import Actividad
from autocuidados.models import autocuidados as AutocuidadoEquipo
from reservas.models import Reserva
from reservas.services import telefono_pago_invalido, whatsapp_link_pago

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
        reserva.telefono_invalido = telefono_pago_invalido(reserva)

    actividades_con_espera = Actividad.objects.con_conteos().filter(
        activa=True,
        fecha__gte=timezone.now().date(),
        _en_lista_espera_anotado__gt=0,
    ).order_by("fecha")

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
    autocuidados_u = AutocuidadoEquipo.objects.all()
    return render(request, "core/autocuidado.html", {"autocuidados_u": autocuidados_u})

def inicio(request):
    return render(request,"core/inicio.html")

def escuelaparaelbuentrato(request):
    return render(request,"core/escuelaparaelbuentrato.html")



def contact(request):
    return render(request,"core/contact.html")