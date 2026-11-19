# app.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Crear la aplicacion Flask y registrar las rutas del proyecto.
#
# Para arrancar en modo local:
#   python app.py
#
# La pagina principal se atiende desde rutas/portfolio.py.
# El login se atiende desde rutas/autenticacion.py.
# Las acciones de edicion se atienden desde rutas/edicion.py.

import os

from flask import Flask, flash, redirect, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect

from configuracion import obtener_clave_secreta
from rutas.autenticacion import autenticacion
from rutas.edicion import paginas_edicion
from rutas.portfolio import paginas_portfolio


def crear_aplicacion():
    """
    Crea la aplicacion Flask y la deja lista para funcionar.
    """

    aplicacion = Flask(__name__)

    # La SECRET_KEY se lee desde .env.
    # Flask la usa para firmar la cookie de sesion y los tokens CSRF.
    clave_secreta = obtener_clave_secreta()

    if clave_secreta == "":
        raise RuntimeError(
            "Falta SECRET_KEY en el archivo .env. "
            "Sin esa clave no se puede iniciar la sesion."
        )

    aplicacion.config["SECRET_KEY"] = clave_secreta

    # La cookie de sesion no puede ser leida por JavaScript.
    aplicacion.config["SESSION_COOKIE_HTTPONLY"] = True
    aplicacion.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # CSRFProtect agrega un token secreto a todos los formularios POST.
    # Si el token falta o no coincide, Flask rechaza la peticion.
    CSRFProtect(aplicacion)

    # Registramos los grupos de rutas.
    aplicacion.register_blueprint(paginas_portfolio)
    aplicacion.register_blueprint(autenticacion)
    aplicacion.register_blueprint(paginas_edicion)

    @aplicacion.errorhandler(CSRFError)
    def manejar_error_csrf(error):
        """
        Evita que el usuario vea una pagina de error fea cuando un
        formulario vence. Le avisa y lo devuelve al portfolio.
        """

        flash(
            "El formulario venció o no es válido. Volvé a intentarlo.",
            "warning",
        )
        return redirect(url_for("portfolio.mostrar_portfolio"))

    return aplicacion


# Creamos la aplicacion una sola vez.
aplicacion = crear_aplicacion()

# Flask y los servicios de deploy suelen buscar una variable llamada "app".
# Por eso dejamos este alias. La logica sigue estando en "aplicacion".
app = aplicacion


if __name__ == "__main__":
    # En la computadora queremos ver los errores (FLASK_DEBUG=1 en .env).
    # En el hosting queremos que no se vean (FLASK_DEBUG=0).
    modo_depuracion = os.getenv("FLASK_DEBUG", "0") == "1"

    # El hosting gratuito dice en que puerto debe escuchar la aplicacion.
    # Si no lo dice, usamos el 5000 de siempre.
    puerto = int(os.getenv("PORT", "5000"))

    # host="0.0.0.0" permite que el servidor del hosting pueda conectarse.
    aplicacion.run(
        host="0.0.0.0",
        port=puerto,
        debug=modo_depuracion,
    )
