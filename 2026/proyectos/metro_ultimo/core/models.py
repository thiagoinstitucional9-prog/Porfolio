"""Modelos del sitio. Toda la información vive en MySQL."""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from .utils import DIAS_SEMANA, MESES, duracion_texto, formato_miles


class Ciudad(models.Model):
    nombre = models.CharField("nombre", max_length=100, unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "ciudad"
        verbose_name_plural = "ciudades"

    def __str__(self):
        return self.nombre


class ClaseServicio(models.Model):
    nombre = models.CharField("nombre", max_length=50, unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "clase de servicio"
        verbose_name_plural = "clases de servicio"

    def __str__(self):
        return self.nombre


class Horario(models.Model):
    hora = models.TimeField("hora de salida")
    clase = models.ForeignKey(
        ClaseServicio, on_delete=models.PROTECT, related_name="horarios",
        verbose_name="clase de servicio",
    )

    class Meta:
        ordering = ["hora"]
        constraints = [
            models.UniqueConstraint(fields=["hora", "clase"],
                                    name="horario_unico"),
        ]
        verbose_name = "horario"
        verbose_name_plural = "horarios"

    def __str__(self):
        return f"{self.hora:%H:%M} · {self.clase}"


class Ruta(models.Model):
    origen = models.ForeignKey(
        Ciudad, on_delete=models.PROTECT, related_name="rutas_origen",
        verbose_name="origen",
    )
    destino = models.ForeignKey(
        Ciudad, on_delete=models.PROTECT, related_name="rutas_destino",
        verbose_name="destino",
    )
    minutos = models.PositiveIntegerField("duración en minutos")

    class Meta:
        ordering = ["origen__nombre", "destino__nombre"]
        constraints = [
            models.UniqueConstraint(fields=["origen", "destino"],
                                    name="ruta_unica"),
        ]
        verbose_name = "ruta"
        verbose_name_plural = "rutas"

    def __str__(self):
        return f"{self.origen} → {self.destino}"

    @property
    def duracion(self):
        return duracion_texto(self.minutos)


class Tarifa(models.Model):
    ruta = models.ForeignKey(
        Ruta, on_delete=models.CASCADE, related_name="tarifas",
        verbose_name="ruta",
    )
    clase = models.ForeignKey(
        ClaseServicio, on_delete=models.PROTECT, related_name="tarifas",
        verbose_name="clase de servicio",
    )
    precio = models.PositiveIntegerField("precio")

    class Meta:
        ordering = ["ruta", "clase__nombre"]
        constraints = [
            models.UniqueConstraint(fields=["ruta", "clase"],
                                    name="tarifa_unica"),
        ]
        verbose_name = "tarifa"
        verbose_name_plural = "tarifas"

    def __str__(self):
        return f"{self.ruta} · {self.clase}: ${formato_miles(self.precio)}"


class Viaje(models.Model):
    """Una salida concreta: ruta + horario + fecha."""

    fecha = models.DateField("fecha", db_index=True)
    ruta = models.ForeignKey(
        Ruta, on_delete=models.CASCADE, related_name="viajes",
        verbose_name="ruta",
    )
    horario = models.ForeignKey(
        Horario, on_delete=models.PROTECT, related_name="viajes",
        verbose_name="horario",
    )
    coche = models.ForeignKey(
        "Coche", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="viajes", verbose_name="coche",
    )
    precio = models.PositiveIntegerField("precio por pasajero")
    asientos = models.PositiveIntegerField("butacas disponibles")

    class Meta:
        ordering = ["fecha", "horario__hora", "ruta__origen__nombre"]
        constraints = [
            models.UniqueConstraint(fields=["fecha", "ruta", "horario"],
                                    name="viaje_unico"),
        ]
        verbose_name = "viaje"
        verbose_name_plural = "viajes"

    def __str__(self):
        return f"{self.ruta} · {self.fecha:%d/%m/%Y} {self.hora}"

    def clean(self):
        """Un coche no puede repetirse en la misma fecha y horario."""
        super().clean()
        # El formulario ya agregó el error; evitamos que ModelForm lo
        # duplique al llamar a full_clean().
        if getattr(self, "_validado_en_formulario", False):
            return
        if self.coche_duplicado(
            self.coche_id, self.fecha, self.horario_id, self.pk
        ):
            raise ValidationError({
                "coche": (
                    "Este coche ya está asignado a otro viaje "
                    "en esa fecha y horario."
                )
            })

    @staticmethod
    def coche_duplicado(coche_id, fecha, horario_id, pk=None):
        if not coche_id or not fecha or not horario_id:
            return False
        consulta = Viaje.objects.filter(
            coche_id=coche_id,
            fecha=fecha,
            horario_id=horario_id,
        )
        if pk:
            consulta = consulta.exclude(pk=pk)
        return consulta.exists()

    # Propiedades que usan las plantillas y las vistas.
    @property
    def origen(self):
        return self.ruta.origen

    @property
    def destino(self):
        return self.ruta.destino

    @property
    def clase(self):
        return self.horario.clase.nombre

    @property
    def hora(self):
        return self.horario.hora.strftime("%H:%M")

    @property
    def fecha_iso(self):
        return self.fecha.isoformat()

    @property
    def dia_largo(self):
        return (f"{DIAS_SEMANA[self.fecha.weekday()]} {self.fecha.day} de "
                f"{MESES[self.fecha.month - 1]}")

    @property
    def duracion(self):
        return self.ruta.duracion

    @property
    def hora_llegada(self):
        hora, _ = self._llegada()
        return hora

    @property
    def llegada_dia_siguiente(self):
        _, dia_siguiente = self._llegada()
        return dia_siguiente

    def _llegada(self):
        """Suma la duración a la hora de salida y avisa si llega al día siguiente."""
        hora_salida, minuto_salida = (int(parte) for parte in self.hora.split(":"))
        total = hora_salida * 60 + minuto_salida + self.ruta.minutos
        dia_siguiente = total >= 24 * 60
        total %= 24 * 60
        return f"{total // 60:02d}:{total % 60:02d}", dia_siguiente

    @property
    def precio_txt(self):
        return formato_miles(self.precio)

    @property
    def es_futuro(self):
        return self.fecha >= date.today()


class Destino(models.Model):
    nombre = models.CharField("nombre", max_length=100)
    provincia = models.CharField("provincia", max_length=100)
    desde = models.PositiveIntegerField("precio desde")
    duracion = models.CharField("duración", max_length=50)
    icono = models.CharField("ícono", max_length=50)
    estilo = models.CharField("estilo", max_length=50)
    bajada = models.TextField("bajada")
    origen = models.ForeignKey(
        Ciudad, on_delete=models.PROTECT, related_name="destinos",
        verbose_name="origen",
    )
    orden = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "destino"
        verbose_name_plural = "destinos"

    def __str__(self):
        return self.nombre

    @property
    def desde_txt(self):
        return formato_miles(self.desde)


class Promocion(models.Model):
    titulo = models.CharField("título", max_length=150)
    descuento = models.CharField("descuento", max_length=50)
    bajada = models.TextField("bajada")
    condiciones = models.TextField("condiciones")
    orden = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "promoción"
        verbose_name_plural = "promociones"

    def __str__(self):
        return self.titulo


class Beneficio(models.Model):
    titulo = models.CharField("título", max_length=150)
    texto = models.TextField("texto")
    icono = models.CharField("ícono", max_length=50)
    orden = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "beneficio"
        verbose_name_plural = "beneficios"

    def __str__(self):
        return self.titulo


# ------------------------------------------------------------------
# Sistema de transporte: personas, empleados, pasajeros y flota
# ------------------------------------------------------------------

class Persona(models.Model):
    nombre = models.CharField("nombre", max_length=100)
    apellido = models.CharField("apellido", max_length=100)
    dni = models.CharField("DNI", max_length=20, unique=True)
    telefono = models.CharField("teléfono", max_length=30, blank=True)
    email = models.EmailField("email", blank=True)
    direccion = models.CharField("dirección", max_length=200, blank=True)

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "persona"
        verbose_name_plural = "personas"

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI {self.dni})"


class Empleado(Persona):
    legajo = models.CharField("legajo", max_length=20, unique=True)
    cargo = models.CharField("cargo", max_length=100)
    fecha_ingreso = models.DateField("fecha de ingreso")

    class Meta:
        verbose_name = "empleado"
        verbose_name_plural = "empleados"

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (Legajo {self.legajo})"


class Pasajero(Persona):
    fecha_nacimiento = models.DateField(
        "fecha de nacimiento", null=True, blank=True,
    )

    class Meta:
        verbose_name = "pasajero"
        verbose_name_plural = "pasajeros"

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI {self.dni})"


class Linea(models.Model):
    nombre = models.CharField("nombre", max_length=100, unique=True)
    descripcion = models.CharField("descripción", max_length=200, blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "línea"
        verbose_name_plural = "líneas"

    def __str__(self):
        return self.nombre


class Cochera(models.Model):
    nombre = models.CharField("nombre", max_length=100, unique=True)
    ubicacion = models.CharField("ubicación", max_length=200)
    capacidad = models.PositiveIntegerField("capacidad")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "cochera"
        verbose_name_plural = "cocheras"

    def __str__(self):
        return f"{self.nombre} ({self.ubicacion})"


class Coche(models.Model):
    patente = models.CharField("patente", max_length=20, unique=True)
    modelo = models.CharField("modelo", max_length=100)
    capacidad = models.PositiveIntegerField("capacidad")
    linea = models.ForeignKey(
        Linea, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="línea",
    )
    cochera = models.ForeignKey(
        Cochera, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="cochera",
    )

    class Meta:
        ordering = ["patente"]
        verbose_name = "coche"
        verbose_name_plural = "coches"

    def __str__(self):
        return f"{self.patente} - {self.modelo}"
