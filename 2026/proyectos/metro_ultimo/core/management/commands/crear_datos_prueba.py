from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Coche, Cochera, Linea, Viaje


class Command(BaseCommand):
    help = "Crea una línea, dos coches y asigna coches a algunos viajes."

    @transaction.atomic
    def handle(self, *args, **options):
        cochera = Cochera.objects.order_by("id").first()
        if cochera is None:
            cochera = Cochera.objects.create(
                nombre="Cochera Retiro",
                ubicacion="Terminal Retiro",
                capacidad=20,
            )

        linea, _ = Linea.objects.get_or_create(
            nombre="Línea Retiro - Rosario",
            defaults={"descripcion": "Línea de prueba"},
        )

        coches = []
        for patente, modelo, capacidad in [
            ("AA111AA", "Mercedes-Benz Tourismo", 40),
            ("BB222BB", "Scania Irizar i6", 45),
        ]:
            coche, _ = Coche.objects.get_or_create(
                patente=patente,
                defaults={
                    "modelo": modelo,
                    "capacidad": capacidad,
                    "linea": linea,
                    "cochera": cochera,
                },
            )
            # Los coches de prueba quedan siempre en la línea y cochera
            # indicadas, aunque ya existieran de una ejecución anterior.
            coche.modelo = modelo
            coche.capacidad = capacidad
            coche.linea = linea
            coche.cochera = cochera
            coche.save(
                update_fields=["modelo", "capacidad", "linea", "cochera"]
            )
            coches.append(coche)

        asignados = 0
        combinaciones = list(
            Viaje.objects.filter(fecha__gte=date.today())
            .values_list("fecha", "horario_id")
            .distinct()
            .order_by("fecha", "horario_id")[:4]
        )
        for fecha, horario_id in combinaciones:
            viaje = (
                Viaje.objects.filter(fecha=fecha, horario_id=horario_id)
                .order_by("id")
                .first()
            )
            if viaje is None or viaje.coche_id is not None:
                continue

            coche = coches[asignados % len(coches)]
            if Viaje.coche_duplicado(
                coche.pk, viaje.fecha, viaje.horario_id, viaje.pk
            ):
                continue

            viaje.coche = coche
            viaje.save(update_fields=["coche"])
            asignados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Línea: {linea}. "
            f"Coches: {', '.join(coche.patente for coche in coches)}. "
            f"Cochera: {cochera.nombre}. "
            f"Viajes asignados en esta ejecución: {asignados}."
        ))
