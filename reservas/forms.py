from django import forms

from .models import BloqueoFecha, Cliente, Reserva
from .services import get_or_create_cliente


INPUT_CLASSES = (
    "w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 "
    "focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
)


class ReservaForm(forms.ModelForm):
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
    tipo_sesion = forms.ChoiceField(
        choices=Reserva.TIPO_SESION_CHOICES,
        label="Tipo de sesión",
        widget=forms.RadioSelect(attrs={"class": "mt-1 h-4 w-4 accent-primary"}),
    )
    modalidad = forms.ChoiceField(
        choices=[("", "Selecciona modalidad")] + list(Reserva.MODALIDAD_CHOICES),
        label="Modalidad",
        widget=forms.Select(attrs={"class": INPUT_CLASSES}),
    )

    class Meta:
        model = Reserva
        fields = ["tipo_sesion", "modalidad", "fecha", "hora"]
        widgets = {
            "fecha": forms.DateInput(
                attrs={"type": "date", "class": INPUT_CLASSES, "x-model": "fecha"}
            ),
            "hora": forms.TimeInput(attrs={"type": "time", "class": INPUT_CLASSES}),
        }

    def clean_empresa(self):
        if self.cleaned_data.get("empresa"):
            raise forms.ValidationError("No se pudo procesar la solicitud.")
        return self.cleaned_data.get("empresa")

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if BloqueoFecha.objects.filter(fecha=fecha).exists():
            raise forms.ValidationError(
                "Esa fecha no está disponible para reservar. Elige otra."
            )
        return fecha

    def save(self, commit=True):
        cliente = get_or_create_cliente(
            nombre=self.cleaned_data["nombre"],
            email=self.cleaned_data["email"],
            telefono=self.cleaned_data["telefono"],
            convenio=self.cleaned_data["convenio"],
        )
        reserva = super().save(commit=False)
        reserva.cliente = cliente
        if commit:
            reserva.save()
        return reserva
