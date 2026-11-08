from django.core.management.base import BaseCommand
from django.db import transaction

from core import data
from core.models import (
    Beneficio, Ciudad, ClaseServicio, Destino, Horario, Promocion, Ruta,
    Tarifa,
)
from core.services import asegurar_viajes


class Command(BaseCommand):
    help = "Carga en MySQL los datos de ejemplo de core/data.py."

    @transaction.atomic
    def handle(self, *args, **options):
        ciudades = {}
        for nombre in data.CIUDADES:
            ciudad, _ = Ciudad.objects.get_or_create(nombre=nombre)
            ciudades[nombre] = ciudad

        clases = {}
        for _, nombre_clase in data.HORARIOS:
            clase, _ = ClaseServicio.objects.get_or_create(nombre=nombre_clase)
            clases[nombre_clase] = clase

        for hora, nombre_clase in data.HORARIOS:
            Horario.objects.get_or_create(
                hora=hora,
                clase=clases[nombre_clase],
            )

        for ruta_data in data.RUTAS:
            ruta, _ = Ruta.objects.get_or_create(
                origen=ciudades[ruta_data["origen"]],
                destino=ciudades[ruta_data["destino"]],
                defaults={"minutos": ruta_data["minutos"]},
            )
            for nombre_clase, precio in ruta_data["precios"].items():
                Tarifa.objects.get_or_create(
                    ruta=ruta,
                    clase=clases[nombre_clase],
                    defaults={"precio": precio},
                )

        for orden, destino_data in enumerate(data.DESTINOS):
            Destino.objects.get_or_create(
                nombre=destino_data["nombre"],
                defaults={
                    "provincia": destino_data["provincia"],
                    "desde": destino_data["desde"],
                    "duracion": destino_data["duracion"],
                    "icono": destino_data["icono"],
                    "estilo": destino_data["estilo"],
                    "bajada": destino_data["bajada"],
                    "origen": ciudades[destino_data["origen"]],
                    "orden": orden,
                },
            )

        for orden, promo in enumerate(data.PROMOCIONES):
            Promocion.objects.get_or_create(
                titulo=promo["titulo"],
                defaults={
                    "descuento": promo["descuento"],
                    "bajada": promo["bajada"],
                    "condiciones": promo["condiciones"],
                    "orden": orden,
                },
            )

        for orden, beneficio in enumerate(data.BENEFICIOS):
            Beneficio.objects.get_or_create(
                titulo=beneficio["titulo"],
                defaults={
                    "texto": beneficio["texto"],
                    "icono": beneficio["icono"],
                    "orden": orden,
                },
            )

        viajes = asegurar_viajes()
        self.stdout.write(self.style.SUCCESS(
            f"Datos cargados. Viajes generados: {viajes}"
        ))
