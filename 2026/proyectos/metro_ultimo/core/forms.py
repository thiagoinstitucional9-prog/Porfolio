import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Coche, Cochera, Empleado, Linea, Pasajero, Persona, Viaje


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ["nombre", "apellido", "dni", "telefono", "email", "direccion"]


class EmpleadoForm(PersonaForm):
    """Reutiliza los campos de Persona y agrega los propios del empleado."""

    class Meta(PersonaForm.Meta):
        model = Empleado
        fields = PersonaForm.Meta.fields + [
            "legajo", "cargo", "fecha_ingreso",
        ]


class PasajeroForm(PersonaForm):
    """Reutiliza los campos de Persona y agrega los propios del pasajero."""

    class Meta(PersonaForm.Meta):
        model = Pasajero
        fields = PersonaForm.Meta.fields + ["fecha_nacimiento"]


class LineaForm(forms.ModelForm):
    class Meta:
        model = Linea
        fields = ["nombre", "descripcion"]


class CocheraForm(forms.ModelForm):
    class Meta:
        model = Cochera
        fields = ["nombre", "ubicacion", "capacidad"]


class CocheForm(forms.ModelForm):
    class Meta:
        model = Coche
        fields = ["patente", "modelo", "capacidad", "linea", "cochera"]


class ViajeForm(forms.ModelForm):
    """Formulario para asignar un coche a un viaje ya generado."""

    class Meta:
        model = Viaje
        fields = ["coche"]

    def clean(self):
        datos = super().clean()
        coche = datos.get("coche")
        if coche and self.instance.fecha and self.instance.horario_id:
            if Viaje.coche_duplicado(
                coche.pk,
                self.instance.fecha,
                self.instance.horario_id,
                self.instance.pk,
            ):
                self.add_error(
                    "coche",
                    "Este coche ya está asignado a otro viaje "
                    "en esa fecha y horario.",
                )
                self.instance._validado_en_formulario = True
        return datos


class PagoSimuladoForm(forms.Form):
    """Checkout de demostración: no contacta pasarelas ni cobra dinero."""

    titular = forms.CharField(
        label="Titular de la tarjeta",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "cc-name"}),
    )
    numero_tarjeta = forms.CharField(
        label="Número de tarjeta",
        max_length=19,
        help_text=(
            "Probá con 4111 1111 1111 1111. Para simular un rechazo, "
            "usá una tarjeta terminada en 0000."
        ),
        widget=forms.TextInput(attrs={
            "autocomplete": "cc-number",
            "inputmode": "numeric",
            "placeholder": "4111 1111 1111 1111",
        }),
    )
    vencimiento = forms.CharField(
        label="Vencimiento",
        max_length=5,
        help_text="Formato MM/AA. Por ejemplo: 12/30.",
        widget=forms.TextInput(attrs={
            "autocomplete": "cc-exp",
            "placeholder": "MM/AA",
        }),
    )
    codigo_seguridad = forms.CharField(
        label="Código de seguridad",
        max_length=4,
        help_text="Los 3 o 4 dígitos del dorso de la tarjeta.",
        widget=forms.PasswordInput(attrs={
            "autocomplete": "cc-csc",
            "inputmode": "numeric",
            "placeholder": "123",
        }),
    )
    cuotas = forms.ChoiceField(
        label="Cuotas",
        choices=[
            ("1", "1 pago"),
            ("3", "3 cuotas sin interés"),
            ("6", "6 cuotas sin interés"),
        ],
        initial="1",
    )
    email = forms.EmailField(
        label="Email para el comprobante (opcional)",
        required=False,
    )

    def clean_numero_tarjeta(self):
        valor = self.cleaned_data["numero_tarjeta"]
        digitos = re.sub(r"\D", "", valor)
        if len(digitos) != 16:
            raise ValidationError("Ingresá los 16 dígitos de la tarjeta.")
        return digitos

    def clean_vencimiento(self):
        valor = self.cleaned_data["vencimiento"].strip()
        coincidencia = re.fullmatch(r"(0[1-9]|1[0-2])/(\d{2})", valor)
        if not coincidencia:
            raise ValidationError("Usá el formato MM/AA.")
        mes = int(coincidencia.group(1))
        anio = 2000 + int(coincidencia.group(2))
        hoy = date.today()
        if (anio, mes) < (hoy.year, hoy.month):
            raise ValidationError("La tarjeta está vencida.")
        return valor

    def clean_codigo_seguridad(self):
        valor = self.cleaned_data["codigo_seguridad"].strip()
        if not re.fullmatch(r"\d{3,4}", valor):
            raise ValidationError("El código debe tener 3 o 4 dígitos.")
        return valor

    def pago_aprobado(self):
        """Regla fija del simulador: las tarjetas terminadas en 0000 se rechazan."""
        return not self.cleaned_data["numero_tarjeta"].endswith("0000")

    def tarjeta_enmascarada(self):
        return f"**** **** **** {self.cleaned_data['numero_tarjeta'][-4:]}"
