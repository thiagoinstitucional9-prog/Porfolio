"""Datos de ejemplo del sitio.

Todo el contenido vive acá: destinos, promociones, beneficios y viajes.
No hay base de datos: son listas y funciones simples en Python, fáciles
de modificar.
"""

from datetime import date, timedelta

# Fecha de hoy, para que el buscador no acepte fechas pasadas y para
# generar las salidas de ejemplo.
HOY = date.today()

CIUDADES = [
    "Buenos Aires (Retiro)",
    "Rosario",
    "Santa Fe",
    "Córdoba",
    "Mendoza",
    "Mar del Plata",
    "Bahía Blanca",
    "Neuquén",
    "San Carlos de Bariloche",
    "Salta",
    "Tucumán",
]

# Nombres en español para mostrar fechas sin depender del sistema.
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


def _hora_llegada(hora, minutos):
    """Suma la duración a la hora de salida y avisa si llega al día siguiente."""
    hora_salida, minuto_salida = (int(parte) for parte in hora.split(":"))
    total = hora_salida * 60 + minuto_salida + minutos
    dia_siguiente = total >= 24 * 60
    total %= 24 * 60
    return f"{total // 60:02d}:{total % 60:02d}", dia_siguiente


# Cada ruta sale todos los días a los horarios de HORARIOS.
# Las rutas funcionan en los dos sentidos (origen <-> destino).
RUTAS = [
    {"origen": "Buenos Aires (Retiro)", "destino": "Rosario",
     "minutos": 300,
     "precios": {"Semipullman": 22000, "Pullman": 27000, "Cama": 34000}},
    {"origen": "Buenos Aires (Retiro)", "destino": "Córdoba",
     "minutos": 520,
     "precios": {"Semipullman": 32000, "Pullman": 39000, "Cama": 48000}},
    {"origen": "Buenos Aires (Retiro)", "destino": "Mar del Plata",
     "minutos": 390,
     "precios": {"Semipullman": 26000, "Pullman": 32000, "Cama": 40000}},
    {"origen": "Buenos Aires (Retiro)", "destino": "Mendoza",
     "minutos": 840,
     "precios": {"Semipullman": 46000, "Pullman": 56000, "Cama": 68000}},
    {"origen": "Buenos Aires (Retiro)", "destino": "San Carlos de Bariloche",
     "minutos": 1200,
     "precios": {"Semipullman": 62000, "Pullman": 74000, "Cama": 89000}},
    {"origen": "Buenos Aires (Retiro)", "destino": "Salta",
     "minutos": 1320,
     "precios": {"Semipullman": 68000, "Pullman": 82000, "Cama": 98000}},
    {"origen": "Buenos Aires (Retiro)", "destino": "Bahía Blanca",
     "minutos": 660,
     "precios": {"Semipullman": 30000, "Pullman": 36000, "Cama": 44000}},
    {"origen": "Rosario", "destino": "Córdoba",
     "minutos": 300,
     "precios": {"Semipullman": 21000, "Pullman": 26000, "Cama": 32000}},
    {"origen": "Córdoba", "destino": "Mendoza",
     "minutos": 540,
     "precios": {"Semipullman": 30000, "Pullman": 36000, "Cama": 44000}},
    {"origen": "Mendoza", "destino": "San Carlos de Bariloche",
     "minutos": 660,
     "precios": {"Semipullman": 34000, "Pullman": 41000, "Cama": 50000}},
]

HORARIOS = [("06:30", "Semipullman"), ("13:00", "Pullman"),
            ("21:30", "Cama")]


def _generar_viajes():
    """Crea las salidas de ejemplo para los próximos 15 días."""
    viajes = []
    numero = 1
    for dia in range(15):
        fecha = HOY + timedelta(days=dia)
        for ruta in RUTAS:
            for hora, clase in HORARIOS:
                llegada, dia_siguiente = _hora_llegada(hora, ruta["minutos"])
                precio = ruta["precios"][clase]
                viajes.append({
                    "id": numero,
                    "origen": ruta["origen"],
                    "destino": ruta["destino"],
                    "fecha": fecha,
                    "fecha_iso": fecha.isoformat(),
                    "dia_largo": (f"{DIAS_SEMANA[fecha.weekday()]} "
                                  f"{fecha.day} de {MESES[fecha.month - 1]}"),
                    "hora": hora,
                    "hora_llegada": llegada,
                    "llegada_dia_siguiente": dia_siguiente,
                    "duracion": duracion_texto(ruta["minutos"]),
                    "clase": clase,
                    "precio": precio,
                    "precio_txt": formato_miles(precio),
                    "asientos": 2 + (numero * 13) % 34,
                })
                numero += 1
    return viajes


VIAJES = _generar_viajes()


def buscar_viajes(origen, destino, fecha):
    """Filtra los viajes de ejemplo. Un campo vacío no filtra."""
    return [
        viaje for viaje in VIAJES
        if (not origen or viaje["origen"] == origen)
        and (not destino or viaje["destino"] == destino)
        and (not fecha or viaje["fecha_iso"] == fecha)
    ]


def obtener_viaje(viaje_id):
    """Busca un viaje por su id; devuelve None si no existe."""
    for viaje in VIAJES:
        if viaje["id"] == viaje_id:
            return viaje
    return None


# ------------------------------------------------------------------
# Contenido de la página principal
# ------------------------------------------------------------------

DESTINOS = [
    {"nombre": "Rosario", "provincia": "Santa Fe", "desde": 22000,
     "duracion": "5 h", "icono": "ic-ciudad", "estilo": "grad-1",
     "bajada": "Costera, río Paraná y la frutería de siempre.",
     "origen": "Buenos Aires (Retiro)"},
    {"nombre": "Córdoba", "provincia": "Córdoba", "desde": 32000,
     "duracion": "8 h 40 min", "icono": "ic-ciudad", "estilo": "grad-2",
     "bajada": "Sierras, universidad y callejerismo en el centro.",
     "origen": "Buenos Aires (Retiro)"},
    {"nombre": "Mar del Plata", "provincia": "Buenos Aires", "desde": 26000,
     "duracion": "6 h 30 min", "icono": "ic-mar", "estilo": "grad-3",
     "bajada": "Playas, muelles y el sabor del verano atlántico.",
     "origen": "Buenos Aires (Retiro)"},
    {"nombre": "Mendoza", "provincia": "Mendoza", "desde": 46000,
     "duracion": "14 h", "icono": "ic-montana", "estilo": "grad-4",
     "bajada": "Viñedos, ruta de vinos y los Andes de fondo.",
     "origen": "Buenos Aires (Retiro)"},
    {"nombre": "San Carlos de Bariloche", "provincia": "Río Negro",
     "desde": 62000, "duracion": "20 h", "icono": "ic-montana",
     "estilo": "grad-5",
     "bajada": "Lagos, montaña y chocolate en la Patagonia.",
     "origen": "Buenos Aires (Retiro)"},
    {"nombre": "Salta", "provincia": "Salta", "desde": 68000,
     "duracion": "22 h", "icono": "ic-sol", "estilo": "grad-6",
     "bajada": "Quebrada, cordillera y gastronomía del norte.",
     "origen": "Buenos Aires (Retiro)"},
]

for _destino in DESTINOS:
    _destino["desde_txt"] = formato_miles(_destino["desde"])

PROMOCIONES = [
    {"titulo": "Ida y vuelta con 20% off",
     "descuento": "-20%",
     "bajada": "Comprando la ida y el regreso en la misma operación, "
               "el viaje de vuelta sale 20% menos.",
     "condiciones": "Válido para todos los servicios de larga distancia. "
                    "El descuento se aplica sobre la butaca de regreso. "
                    "No acumulable con otras promociones."},
    {"titulo": "Hasta 6 cuotas sin interés",
     "descuento": "CUOTAS",
     "bajada": "Pagá con las tarjetas bancarias adheridas en 3 y 6 cuotas "
               "sin interés desde $90.000.",
     "condiciones": "3 cuotas desde $45.000 y 6 cuotas desde $90.000. "
                    "Sujeto a aprobación del emisor. No aplica a cambios "
                    "ni anulaciones."},
    {"titulo": "Club METRO",
     "descuento": "PUNTOS",
     "bajada": "Sumás 1 punto por cada $100 y los canjeás por pasajes o "
               "upgrades de butaca.",
     "condiciones": "Registro gratuito. Los puntos se acreditan 48 horas "
                    "después del viaje y vencen a los 12 meses."},
    {"titulo": "Chicos viajan con descuento",
     "descuento": "-30%",
     "bajada": "Menores de 12 años con 30% off de lunes a jueves, "
               "acompañados de un adulto.",
     "condiciones": "Un menor por pasajero adulto. Presentar DNI o "
                    "partida de nacimiento al momento del viaje."},
]

BENEFICIOS = [
    {"titulo": "Comodidad",
     "texto": "Butacas reclinables cama con apoyabrazos, aire acondicionado "
              "y wifi a bordo en los servicios premium.",
     "icono": "ic-asiento"},
    {"titulo": "Seguridad",
     "texto": "Flota con GPS y mantenimiento programado, choferes con "
              "capacitación anual y seguro de pasajeros incluido.",
     "icono": "ic-escudo"},
    {"titulo": "Puntualidad",
     "texto": "Salidas en horario y seguimiento del servicio en tiempo "
              "real desde tu celular.",
     "icono": "ic-reloj"},
    {"titulo": "Facilidad para comprar",
     "texto": "Elegís destino, horario y butaca en tres pasos, y el "
              "boleto llega a tu mail y a tu celular.",
     "icono": "ic-click"},
]
