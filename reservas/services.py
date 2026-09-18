from urllib.parse import quote

from .models import Cliente


def _normalizar_telefono_cl(telefono_crudo):
    """
    Normaliza un teléfono a formato E.164 sin "+" (ej. 56912345678) para
    armar un link wa.me válido. Devuelve None si no calza con un celular
    chileno real, en vez de mandar lo que sea a wa.me y generar un link roto.

    Acepta los formatos más comunes en los que alguien tipearía su celular:
    "+56 9 1234 5678", "56912345678", "912345678" (sin el 56) o
    "09 1234 5678" (con el 0 de marcado local).
    """
    digitos = "".join(ch for ch in telefono_crudo if ch.isdigit())
    if not digitos:
        return None
    if len(digitos) == 9 and digitos.startswith("9"):
        digitos = "56" + digitos
    elif len(digitos) == 10 and digitos.startswith("09"):
        digitos = "56" + digitos[1:]
    if len(digitos) == 11 and digitos.startswith("569"):
        return digitos
    return None


def whatsapp_link_pago(reserva):
    """
    Link wa.me con mensaje pre-armado para que Fabiola coordine el pago
    manualmente con el cliente (RF-B-04/05: no hay pasarela en el MVP).

    Devuelve None tanto si no hay teléfono guardado como si el que hay no se
    pudo normalizar a un celular chileno válido — usa telefono_pago_invalido()
    para distinguir ambos casos donde haga falta avisarle a Fabiola cuál es.
    """
    if not reserva.pk or not reserva.cliente_id:
        return None
    telefono = _normalizar_telefono_cl(reserva.cliente.telefono)
    if not telefono:
        return None
    mensaje = (
        f"Hola {reserva.cliente.nombre}, te escribo de Casa del Amar Penco para "
        f"coordinar el pago de tu {reserva.get_tipo_sesion_display()} del "
        f"{reserva.fecha.strftime('%d-%m-%Y')} a las {reserva.hora.strftime('%H:%M')}."
    )
    return f"https://wa.me/{telefono}?text={quote(mensaje)}"


def telefono_pago_invalido(reserva):
    """
    True si el cliente tiene ALGO guardado en teléfono pero no se pudo
    normalizar a un celular chileno válido — para que el admin/panel puedan
    avisar "teléfono con formato inválido" en vez de "sin teléfono", que
    hoy se ven exactamente igual y Fabiola no tiene forma de distinguirlos.
    """
    if not reserva.pk or not reserva.cliente_id:
        return False
    crudo = (reserva.cliente.telefono or "").strip()
    if not crudo:
        return False
    return _normalizar_telefono_cl(crudo) is None


def get_or_create_cliente(nombre, email, telefono, convenio):
    """
    Crea o reutiliza un Cliente a partir de su email (RF-B-08: sin login).

    Si ya existe un Cliente con ese email, se reutiliza tal cual está guardado
    y NO se sobrescriben nombre/teléfono/convenio con lo que venga en el
    formulario. Antes sí se sobrescribía, lo que permitía a cualquiera que
    conociera el email de un cliente real pisar su teléfono guardado — y ese
    teléfono es justo el que usa whatsapp_link_pago() para coordinar el pago.
    Si el teléfono o nombre de alguien cambió de verdad, se actualiza a mano
    desde el admin.
    """
    cliente, _ = Cliente.objects.get_or_create(
        email=email,
        defaults={"nombre": nombre, "telefono": telefono, "convenio": convenio},
    )
    return cliente
