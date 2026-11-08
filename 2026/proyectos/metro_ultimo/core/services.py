"""Lógica de negocio: genera y consulta las salidas guardadas en MySQL."""

from datetime import date, timedelta

from django.db import transaction
from django.db.models import Max

from .models import Horario, Ruta, Tarifa, Viaje

DIAS_DE_SALIDAS = 15


def asegurar_viajes(hoy=None, dias=DIAS_DE_SALIDAS):
    """Completa en MySQL las salidas de los próximos ``dias`` días.

    Es idempotente: si un viaje ya existe no se duplica, y va generando
    únicamente los días que faltan. Así la base no se queda con fechas
    viejas y el sitio sigue funcionando sin tareas manuales.
    """
    hoy = hoy or date.today()
    hasta = hoy + timedelta(days=dias - 1)

    ultima = Viaje.objects.aggregate(ultima=Max("fecha"))["ultima"]
    desde = hoy if ultima is None or ultima < hoy else ultima + timedelta(days=1)

    # Limpia salidas vencidas sin coche. Las que ya tienen coche asignado
    # se conservan como historial.
    Viaje.objects.filter(fecha__lt=hoy, coche__isnull=True).delete()

    if desde > hasta:
        return 0

    tarifas = {
        (tarifa.ruta_id, tarifa.clase_id): tarifa.precio
        for tarifa in Tarifa.objects.all()
    }
    rutas = list(Ruta.objects.all())
    horarios = list(Horario.objects.all())

    nuevos = []
    dia = desde
    while dia <= hasta:
        for ruta in rutas:
            for horario in horarios:
                precio = tarifas.get((ruta.id, horario.clase_id))
                if precio is None:
                    continue
                asientos = 2 + (
                    (dia.toordinal() * 31 + ruta.id * 13 + horario.id * 7) % 34
                )
                nuevos.append(Viaje(
                    fecha=dia,
                    ruta=ruta,
                    horario=horario,
                    precio=precio,
                    asientos=asientos,
                ))
        dia += timedelta(days=1)

    with transaction.atomic():
        Viaje.objects.bulk_create(nuevos, ignore_conflicts=True, batch_size=500)

    return len(nuevos)


def buscar_viajes(origen="", destino="", fecha=None):
    """Filtra las salidas guardadas. Un campo vacío no filtra."""
    viajes = Viaje.objects.select_related(
        "ruta__origen", "ruta__destino", "horario__clase",
    )
    if origen:
        viajes = viajes.filter(ruta__origen__nombre=origen)
    if destino:
        viajes = viajes.filter(ruta__destino__nombre=destino)
    if fecha:
        viajes = viajes.filter(fecha=fecha)
    return viajes.order_by("fecha", "horario__hora", "ruta__origen__nombre")
