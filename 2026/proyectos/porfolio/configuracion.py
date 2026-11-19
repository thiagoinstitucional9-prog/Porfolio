# configuracion.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Leer el archivo .env y entregar los datos de configuracion.
#
# No usamos ninguna libreria extra: Python ya trae "os", que permite
# leer variables de entorno.
#
# Los datos sensibles NO se escriben aca. Solo se leen desde .env.

import os


# Calculamos la ruta del archivo .env.
# __file__ es la ruta de este archivo (configuracion.py).
# os.path.dirname(...) obtiene la carpeta donde esta.
# os.path.join(...) arma la ruta final: carpeta + ".env".
CARPETA_DEL_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_ARCHIVO_ENV = os.path.join(CARPETA_DEL_PROYECTO, ".env")


def cargar_variables_de_entorno():
    """
    Lee el archivo .env linea por linea y carga cada variable en os.environ.

    Formato esperado dentro de .env:
        NOMBRE_VARIABLE=valor

    Las lineas vacias y las que empiezan con # se ignoran.
    """

    # Si el archivo no existe, no hacemos nada.
    # Mas adelante se pueden usar los valores por defecto de las funciones.
    if not os.path.exists(RUTA_ARCHIVO_ENV):
        return

    # Abrimos el archivo con UTF-8 para que funcionen los acentos y la ñ.
    with open(RUTA_ARCHIVO_ENV, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()

            # Ignoramos lineas vacias.
            if linea == "":
                continue

            # Ignoramos los comentarios.
            if linea.startswith("#"):
                continue

            # Si la linea no tiene un signo igual, no es una variable.
            if "=" not in linea:
                continue

            # split("=", 1) corta la linea en dos partes como maximo.
            # Asi un valor que tenga "=" adentro no se rompe.
            partes = linea.split("=", 1)
            nombre = partes[0].strip()
            valor = partes[1].strip()

            # Si el valor esta entre comillas, las sacamos.
            # Usamos elif para no volver a revisar un valor que ya quedo vacio.
            if len(valor) >= 2:
                if valor[0] == '"' and valor[-1] == '"':
                    valor = valor[1:-1]
                elif valor[0] == "'" and valor[-1] == "'":
                    valor = valor[1:-1]

            # Guardamos la variable solamente si todavia no existe.
            # Esto permite que una variable del sistema tenga prioridad.
            if nombre != "" and os.getenv(nombre) is None:
                os.environ[nombre] = valor


def obtener_datos_base_de_datos():
    """
    Devuelve un diccionario con los datos necesarios para conectar a MySQL.

    Los valores se leen de las variables cargadas desde .env.
    Si alguna variable falta, se usa un valor por defecto para poder
    trabajar en un entorno local simple.
    """

    puerto_como_texto = os.getenv("DB_PORT", "3306")

    datos = {
        "host": os.getenv("DB_HOST", "localhost"),
        "puerto": int(puerto_como_texto),
        "usuario": os.getenv("DB_USER", "root"),
        "clave": os.getenv("DB_PASSWORD", ""),
        "nombre_base": os.getenv("DB_NAME", "portfolio_db"),
    }

    return datos


def obtener_clave_secreta():
    """
    Devuelve la SECRET_KEY de Flask.

    Se usa para firmar la sesion del usuario.
    El valor real vive en .env y nunca se escribe en el codigo.
    """

    return os.getenv("SECRET_KEY", "")


# Al importar este archivo se ejecuta una sola vez la lectura del .env.
# Despues, las funciones de arriba pueden pedir los valores cuando los necesiten.
cargar_variables_de_entorno()
