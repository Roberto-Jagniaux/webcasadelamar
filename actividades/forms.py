from django import forms

from reservas.models import Cliente
from reservas.services import get_or_create_cliente

from .models import Inscripcion


INPUT_CLASSES = (
    "w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 "
    "focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
)


class InscripcionForm(forms.Form):
    # Honeypot: campo invisible para personas, que un bot de envío
    # automático sí suele completar. No hay CAPTCHA configurado (falta
    # credencial de reCAPTCHA/hCaptcha, mismo bloqueo que las notificaciones
    # por email) — esta es la defensa real contra bots simples.
    empresa = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "style": "position:absolute; left:-9999px; width:1px; height:1px;",
                "aria-hidden": "true",
            }
        ),
    )
    nombre = forms.CharField(
        max_length=120,
        label="Nombre completo",
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": INPUT_CLASSES}),
    )
    telefono = forms.CharField(
        max_length=30,
        label="Teléfono",
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES}),
    )
    convenio = forms.ChoiceField(
        choices=Cliente.CONVENIO_CHOICES,
        label="Convenio",
        widget=forms.Select(attrs={"class": INPUT_CLASSES}),
    )

    def __init__(self, *args, actividad=None, **kwargs):
        self.actividad = actividad
        super().__init__(*args, **kwargs)

    def clean_empresa(self):
        if self.cleaned_data.get("empresa"):
            raise forms.ValidationError("No se pudo procesar la solicitud.")
        return self.cleaned_data.get("empresa")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if (
            self.actividad
            and Inscripcion.objects.filter(actividad=self.actividad, cliente__email=email)
            .exclude(estado=Inscripcion.ESTADO_CANCELADA)
            .exists()
        ):
            raise forms.ValidationError(
                "Ya hay una inscripción con este correo para esta actividad."
            )
        return email

    def save(self):
        cliente = get_or_create_cliente(
            nombre=self.cleaned_data["nombre"],
            email=self.cleaned_data["email"],
            telefono=self.cleaned_data["telefono"],
            convenio=self.cleaned_data["convenio"],
        )
        return Inscripcion.objects.create(actividad=self.actividad, cliente=cliente)
