from urllib.parse import quote

from .models import Cliente


def whatsapp_link_pago(reserva):
    """
    Link wa.me con mensaje pre-armado para que Fabiola coordine el pago
    manualmente con el cliente (RF-B-04/05: no hay pasarela en el MVP).
    """
    if not reserva.pk or not reserva.cliente_id:
        return None
    telefono = "".join(ch for ch in reserva.cliente.telefono if ch.isdigit())
    if not telefono:
        return None
    mensaje = (
        f"Hola {reserva.cliente.nombre}, te escribo de Casa del Amar Penco para "
        f"coordinar el pago de tu {reserva.get_tipo_sesion_display()} del "
        f"{reserva.fecha.strftime('%d-%m-%Y')} a las {reserva.hora.strftime('%H:%M')}."
    )
    return f"https://wa.me/{telefono}?text={quote(mensaje)}"


def get_or_create_cliente(nombre, email, telefono, convenio):
    """
    Crea o reutiliza un Cliente a partir de su email (RF-B-08: sin login).
    Si ya existe, refresca sus datos con lo último ingresado en el formulario.
    """
    cliente, created = Cliente.objects.get_or_create(
        email=email,
        defaults={"nombre": nombre, "telefono": telefono, "convenio": convenio},
    )
    if not created:
        cliente.nombre = nombre
        cliente.telefono = telefono
        cliente.convenio = convenio
        cliente.save(update_fields=["nombre", "telefono", "convenio"])
    return cliente
