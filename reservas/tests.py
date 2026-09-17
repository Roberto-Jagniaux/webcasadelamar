import datetime

from django.test import TestCase
from django.urls import reverse

from .models import BloqueoFecha, Cliente, Reserva
from .services import get_or_create_cliente, whatsapp_link_pago


class GetOrCreateClienteTests(TestCase):
    def test_crea_cliente_nuevo(self):
        cliente = get_or_create_cliente(
            nombre="Ana Soto", email="ana@example.com", telefono="912345678",
            convenio=Cliente.CONVENIO_PARTICULAR,
        )
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(cliente.nombre, "Ana Soto")

    def test_reutiliza_cliente_existente_por_email_y_actualiza_datos(self):
        get_or_create_cliente(
            nombre="Ana Soto", email="ana@example.com", telefono="912345678",
            convenio=Cliente.CONVENIO_PARTICULAR,
        )
        cliente = get_or_create_cliente(
            nombre="Ana Soto Pérez", email="ana@example.com", telefono="900000000",
            convenio=Cliente.CONVENIO_FONASA,
        )
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(cliente.nombre, "Ana Soto Pérez")
        self.assertEqual(cliente.telefono, "900000000")
        self.assertEqual(cliente.convenio, Cliente.CONVENIO_FONASA)


class WhatsappLinkPagoTests(TestCase):
    def _crear_reserva(self, telefono=""):
        cliente = Cliente.objects.create(
            nombre="Ana Soto", email="ana@example.com", telefono=telefono,
        )
        return Reserva.objects.create(
            cliente=cliente,
            tipo_sesion=Reserva.TIPO_PSICOTERAPIA,
            modalidad=Reserva.MODALIDAD_ONLINE,
            fecha=datetime.date(2026, 12, 1),
            hora=datetime.time(10, 0),
        )

    def test_sin_reserva_guardada_devuelve_none(self):
        reserva = Reserva(
            tipo_sesion=Reserva.TIPO_PSICOTERAPIA,
            modalidad=Reserva.MODALIDAD_ONLINE,
            fecha=datetime.date(2026, 12, 1),
            hora=datetime.time(10, 0),
        )
        self.assertIsNone(whatsapp_link_pago(reserva))

    def test_sin_telefono_devuelve_none(self):
        reserva = self._crear_reserva(telefono="")
        self.assertIsNone(whatsapp_link_pago(reserva))

    def test_con_telefono_genera_link_wa_me(self):
        reserva = self._crear_reserva(telefono="+56 9 1234 5678")
        link = whatsapp_link_pago(reserva)
        self.assertIsNotNone(link)
        self.assertTrue(link.startswith("https://wa.me/56912345678?text="))


class ReservaFormFechaBloqueadaTests(TestCase):
    def setUp(self):
        self.fecha_bloqueada = datetime.date(2026, 12, 25)
        BloqueoFecha.objects.create(fecha=self.fecha_bloqueada, motivo="Feriado")
        self.datos_base = {
            "nombre": "Ana Soto",
            "email": "ana@example.com",
            "telefono": "912345678",
            "convenio": Cliente.CONVENIO_PARTICULAR,
            "tipo_sesion": Reserva.TIPO_PSICOTERAPIA,
            "modalidad": Reserva.MODALIDAD_ONLINE,
            "hora": "10:00",
        }

    def test_rechaza_fecha_bloqueada(self):
        from .forms import ReservaForm

        form = ReservaForm(data={**self.datos_base, "fecha": self.fecha_bloqueada.isoformat()})
        self.assertFalse(form.is_valid())
        self.assertIn("fecha", form.errors)

    def test_acepta_fecha_libre(self):
        from .forms import ReservaForm

        form = ReservaForm(data={**self.datos_base, "fecha": "2026-12-26"})
        self.assertTrue(form.is_valid(), form.errors)


class ReservarViewTests(TestCase):
    def test_get_muestra_formulario(self):
        response = self.client.get(reverse("reservar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_get_con_tipo_preselecciona_tipo_sesion(self):
        response = self.client.get(reverse("reservar"), {"tipo": Reserva.TIPO_AUTOCUIDADO})
        self.assertEqual(response.context["form"].initial.get("tipo_sesion"), Reserva.TIPO_AUTOCUIDADO)

    def test_post_valido_crea_reserva_y_cliente(self):
        response = self.client.post(reverse("reservar"), {
            "nombre": "Ana Soto",
            "email": "ana@example.com",
            "telefono": "912345678",
            "convenio": Cliente.CONVENIO_PARTICULAR,
            "tipo_sesion": Reserva.TIPO_PSICOTERAPIA,
            "modalidad": Reserva.MODALIDAD_ONLINE,
            "fecha": "2026-12-10",
            "hora": "10:00",
        })
        self.assertRedirects(response, reverse("reservar"))
        self.assertEqual(Reserva.objects.count(), 1)
        self.assertEqual(Cliente.objects.count(), 1)

    def test_post_con_fecha_bloqueada_no_crea_reserva(self):
        BloqueoFecha.objects.create(fecha=datetime.date(2026, 12, 25))
        response = self.client.post(reverse("reservar"), {
            "nombre": "Ana Soto",
            "email": "ana@example.com",
            "telefono": "912345678",
            "convenio": Cliente.CONVENIO_PARTICULAR,
            "tipo_sesion": Reserva.TIPO_PSICOTERAPIA,
            "modalidad": Reserva.MODALIDAD_ONLINE,
            "fecha": "2026-12-25",
            "hora": "10:00",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reserva.objects.count(), 0)
