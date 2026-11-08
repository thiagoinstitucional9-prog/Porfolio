"""Funciones y constantes de formato compartidas."""

from datetime import date

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes",
               "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def formato_miles(numero):
    """32000 -> '32.000' (separador de miles como se usa en Argentina)."""
    return f"{numero:,}".replace(",", ".")


def duracion_texto(minutos):
    """520 -> '8 h 40 min'."""
    return f"{minutos // 60} h {minutos % 60:02d} min"


def fecha_legible(valor):
    """'2026-10-20' -> 'martes 20 de octubre de 2026'. Devuelve '' si no es válida."""
    try:
        fecha = date.fromisoformat(valor)
    except (TypeError, ValueError):
        return ""
    return (f"{DIAS_SEMANA[fecha.weekday()]} {fecha.day} de "
            f"{MESES[fecha.month - 1]} de {fecha.year}")
