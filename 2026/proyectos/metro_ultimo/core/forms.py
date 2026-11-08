from django import forms

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
