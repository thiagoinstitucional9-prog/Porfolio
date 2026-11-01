"""Vistas del sitio. Son funciones simples que arman un diccionario de
contexto y devuelven una plantilla."""

from datetime import date

from django.http import Http404
from django.shortcuts import render

from . import data


def _pasajeros(valor):
    """Convierte el valor del formulario en un número entre 1 y 9."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return 1
    return max(1, min(numero, 9))


def _fecha_legible(valor):
    """'2026-10-20' -> 'martes 20 de octubre'. Devuelve '' si no es válida."""
    try:
        fecha = date.fromisoformat(valor)
    except (TypeError, ValueError):
        return ""
    return (f"{data.DIAS_SEMANA[fecha.weekday()]} {fecha.day} de "
            f"{data.MESES[fecha.month - 1]} de {fecha.year}")


def inicio(request):
    """Página principal: hero, buscador, destinos, promociones y beneficios."""
    contexto = {
        "hoy": data.HOY.isoformat(),
        "ciudades": data.CIUDADES,
        "destinos": data.DESTINOS,
        "promociones": data.PROMOCIONES,
        "beneficios": data.BENEFICIOS,
    }
    return render(request, "core/inicio.html", contexto)


def buscar(request):
    """Muestra las salidas de ejemplo que coinciden con la búsqueda."""
    origen = request.GET.get("origen", "").strip()
    destino = request.GET.get("destino", "").strip()
    fecha = request.GET.get("fecha", "").strip()
    pasajeros = _pasajeros(request.GET.get("pasajeros"))

    viajes = data.buscar_viajes(origen, destino, fecha)
    # Se agrega el total por la cantidad de pasajeros elegida.
    resultados = [
        dict(viaje, total_txt=data.formato_miles(viaje["precio"] * pasajeros))
        for viaje in viajes
    ]

    contexto = {
        "hoy": data.HOY.isoformat(),
        "ciudades": data.CIUDADES,
        "origen": origen,
        "destino": destino,
        "fecha": fecha,
        "fecha_legible": _fecha_legible(fecha),
        "pasajeros": pasajeros,
        "viajes": resultados,
        "destinos": data.DESTINOS,
    }
    return render(request, "core/buscar.html", contexto)


def comprar(request, viaje_id):
    """Resumen del viaje elegido.

    La compra online todavía no está habilitada: la página lo dice con
    claridad y deja los datos de contacto para cerrar la reserva.
    """
    viaje = data.obtener_viaje(viaje_id)
    if viaje is None:
        raise Http404("No existe ese viaje")

    pasajeros = _pasajeros(request.GET.get("pasajeros"))
    contexto = {
        "viaje": viaje,
        "pasajeros": pasajeros,
        "total_txt": data.formato_miles(viaje["precio"] * pasajeros),
        "origen": viaje["origen"],
        "destino": viaje["destino"],
        "fecha": viaje["fecha_iso"],
    }
    return render(request, "core/comprar.html", contexto)
