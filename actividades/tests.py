import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from reservas.models import Cliente

from .models import Actividad, Inscripcion


def _crear_actividad(cupos=1, fecha=None, **kwargs):
    defaults = {
        "titulo": "Taller de prueba",
        "tipo": Actividad.TIPO_TALLER_SALUD_MENTAL,
        "descripcion": "Descripción de prueba",
        "publico_objetivo": "Adultos",
        "fecha": fecha or (timezone.now().date() + datetime.timedelta(days=7)),
        "hora": datetime.time(10, 0),
        "lugar_modalidad": "Online",
        "cupos": cupos,
        "fecha_cierre_inscripciones": timezone.now().date() + datetime.timedelta(days=6),
    }
    defaults.update(kwargs)
    return Actividad.objects.create(**defaults)


def _crear_cliente(email="cliente@example.com", nombre="Cliente Uno"):
    return Cliente.objects.create(nombre=nombre, email=email, telefono="912345678")


class InscripcionListaEsperaTests(TestCase):
    def test_confirma_si_hay_cupos(self):
        actividad = _crear_actividad(cupos=1)
        inscripcion = Inscripcion.objects.create(
            actividad=actividad, cliente=_crear_cliente()
        )
        self.assertEqual(inscripcion.estado, Inscripcion.ESTADO_CONFIRMADA)

    def test_pasa_a_lista_de_espera_si_no_hay_cupos(self):
        actividad = _crear_actividad(cupos=1)
        Inscripcion.objects.create(actividad=actividad, cliente=_crear_cliente("a@example.com"))
        segunda = Inscripcion.objects.create(
            actividad=actividad, cliente=_crear_cliente("b@example.com")
        )
        self.assertEqual(segunda.estado, Inscripcion.ESTADO_LISTA_ESPERA)
        self.assertEqual(actividad.cupos_disponibles, 0)
        self.assertEqual(actividad.en_lista_espera, 1)


class CancelarInscripcionTests(TestCase):
    def test_cancelar_confirmada_promueve_al_primero_en_espera(self):
        actividad = _crear_actividad(cupos=1)
        confirmada = Inscripcion.objects.create(
            actividad=actividad, cliente=_crear_cliente("a@example.com")
        )
        primero_en_espera = Inscripcion.objects.create(
            actividad=actividad, cliente=_crear_cliente("b@example.com")
        )
        segundo_en_espera = Inscripcion.objects.create(
            actividad=actividad, cliente=_crear_cliente("c@example.com")
        )

        confirmada.cancelar()

        primero_en_espera.refresh_from_db()
        segundo_en_espera.refresh_from_db()
        self.assertEqual(confirmada.estado, Inscripcion.ESTADO_CANCELADA)
        self.assertEqual(primero_en_espera.estado, Inscripcion.ESTADO_CONFIRMADA)
        self.assertEqual(segundo_en_espera.estado, Inscripcion.ESTADO_LISTA_ESPERA)

    def test_cancelar_desde_lista_de_espera_no_promueve_a_nadie(self):
        actividad = _crear_actividad(cupos=1)
        Inscripcion.objects.create(actividad=actividad, cliente=_crear_cliente("a@example.com"))
        en_espera = Inscripcion.objects.create(
            actividad=actividad, cliente=_crear_cliente("b@example.com")
        )
        self.assertEqual(en_espera.estado, Inscripcion.ESTADO_LISTA_ESPERA)

        en_espera.cancelar()

        self.assertEqual(en_espera.estado, Inscripcion.ESTADO_CANCELADA)
        self.assertEqual(actividad.en_lista_espera, 0)


class ActividadPropiedadesTests(TestCase):
    def test_es_pasada(self):
        pasada = _crear_actividad(fecha=timezone.now().date() - datetime.timedelta(days=1))
        futura = _crear_actividad(fecha=timezone.now().date() + datetime.timedelta(days=1))
        self.assertTrue(pasada.es_pasada)
        self.assertFalse(futura.es_pasada)


class InscripcionFormEmailDuplicadoTests(TestCase):
    def test_rechaza_email_duplicado_activo(self):
        from .forms import InscripcionForm

        actividad = _crear_actividad(cupos=5)
        Inscripcion.objects.create(actividad=actividad, cliente=_crear_cliente("dup@example.com"))

        form = InscripcionForm(
            data={
                "nombre": "Otro Nombre",
                "email": "dup@example.com",
                "telefono": "900000000",
                "convenio": Cliente.CONVENIO_PARTICULAR,
            },
            actividad=actividad,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_permite_reinscribirse_si_la_anterior_esta_cancelada(self):
        from .forms import InscripcionForm

        actividad = _crear_actividad(cupos=5)
        previa = Inscripcion.objects.create(
            actividad=actividad, cliente=_crear_cliente("dup@example.com")
        )
        previa.cancelar()

        form = InscripcionForm(
            data={
                "nombre": "Otro Nombre",
                "email": "dup@example.com",
                "telefono": "900000000",
                "convenio": Cliente.CONVENIO_PARTICULAR,
            },
            actividad=actividad,
        )
        self.assertTrue(form.is_valid(), form.errors)


class ListadoPasadasViewTests(TestCase):
    def test_listado_solo_muestra_activas_y_futuras(self):
        futura = _crear_actividad(fecha=timezone.now().date() + datetime.timedelta(days=1))
        _crear_actividad(fecha=timezone.now().date() - datetime.timedelta(days=1))
        _crear_actividad(fecha=timezone.now().date() + datetime.timedelta(days=1), activa=False)

        response = self.client.get(reverse("actividades"))
        actividades = list(response.context["actividades"])
        self.assertEqual(actividades, [futura])

    def test_pasadas_solo_muestra_activas_y_pasadas(self):
        pasada = _crear_actividad(fecha=timezone.now().date() - datetime.timedelta(days=1))
        _crear_actividad(fecha=timezone.now().date() + datetime.timedelta(days=1))

        response = self.client.get(reverse("actividades_pasadas"))
        actividades = list(response.context["actividades"])
        self.assertEqual(actividades, [pasada])


class DetalleViewTests(TestCase):
    def test_detalle_actividad_inactiva_da_404(self):
        actividad = _crear_actividad(activa=False)
        response = self.client.get(reverse("actividad_detalle", args=[actividad.pk]))
        self.assertEqual(response.status_code, 404)

    def test_post_en_actividad_pasada_no_crea_inscripcion(self):
        actividad = _crear_actividad(fecha=timezone.now().date() - datetime.timedelta(days=1))
        response = self.client.post(reverse("actividad_detalle", args=[actividad.pk]), {
            "nombre": "Ana Soto",
            "email": "ana@example.com",
            "telefono": "912345678",
            "convenio": Cliente.CONVENIO_PARTICULAR,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inscripcion.objects.count(), 0)

    def test_post_valido_inscribe_y_redirige(self):
        actividad = _crear_actividad(cupos=5)
        response = self.client.post(reverse("actividad_detalle", args=[actividad.pk]), {
            "nombre": "Ana Soto",
            "email": "ana@example.com",
            "telefono": "912345678",
            "convenio": Cliente.CONVENIO_PARTICULAR,
        })
        self.assertRedirects(response, reverse("actividad_detalle", args=[actividad.pk]))
        self.assertEqual(Inscripcion.objects.count(), 1)
