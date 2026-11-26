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

# Permite leer variables de entorno como PORT o FLASK_DEBUG.
import os

# Traemos las herramientas de Flask para crear la app y responder al navegador.
from flask import Flask, flash, redirect, url_for

# Traemos la proteccion CSRF y el tipo de error que lanza cuando falla.
from flask_wtf.csrf import CSRFError, CSRFProtect

# Esta funcion lee la clave secreta desde el archivo .env.
from configuracion import obtener_clave_secreta

# Traemos el grupo de rutas del login y del logout.
from rutas.autenticacion import autenticacion

# Traemos el grupo de rutas para agregar, editar y eliminar contenido.
from rutas.edicion import paginas_edicion

# Traemos el grupo de rutas de la pagina principal.
from rutas.portfolio import paginas_portfolio


# Definimos una funcion que arma la aplicacion y la devuelve lista.
def crear_aplicacion():
    """
    Crea la aplicacion Flask y la deja lista para funcionar.
    """

    # Creamos el objeto Flask. __name__ le dice donde estan las carpetas.
    aplicacion = Flask(__name__)

    # La clave se lee del .env y sirve para firmar la sesion y el token CSRF.
    clave_secreta = obtener_clave_secreta()

    # Revisamos que la clave no este vacia: sin ella no se puede iniciar sesion.
    if clave_secreta == "":
        # Si falta la clave, detenemos el programa con un mensaje claro.
        raise RuntimeError(
            "Falta SECRET_KEY en el archivo .env. "
            # Este pedazo se pega al anterior dentro del mismo mensaje.
            "Sin esa clave no se puede iniciar la sesion."
        )

    # Guardamos la clave dentro de la configuracion de Flask.
    aplicacion.config["SECRET_KEY"] = clave_secreta

    # La cookie de sesion no puede ser leida por JavaScript (mas seguridad).
    aplicacion.config["SESSION_COOKIE_HTTPONLY"] = True

    # La cookie solo viaja dentro de este sitio, no desde otras paginas.
    aplicacion.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Activamos el token secreto en todos los formularios POST.
    # Si el token falta o no coincide, Flask rechaza la peticion.
    CSRFProtect(aplicacion)

    # Enchufamos el grupo de rutas de la pagina principal.
    aplicacion.register_blueprint(paginas_portfolio)

    # Enchufamos el grupo de rutas del login y del logout.
    aplicacion.register_blueprint(autenticacion)

    # Enchufamos el grupo de rutas protegidas de edicion.
    aplicacion.register_blueprint(paginas_edicion)

    # Decimos que la funcion de abajo atendera los errores de token CSRF.
    @aplicacion.errorhandler(CSRFError)
    # Definimos la funcion que recibe el error y devuelve una respuesta amable.
    def manejar_error_csrf(error):
        """
        Evita que el usuario vea una pagina de error fea cuando un
        formulario vence. Le avisa y lo devuelve al portfolio.
        """

        # Mostramos un aviso arriba de la pagina con categoria "warning".
        flash(
            "El formulario venció o no es válido. Volvé a intentarlo.",
            # La categoria "warning" hace que el aviso sea amarillo.
            "warning",
        )

        # Devolvemos al usuario a la pagina principal con un redirect.
        return redirect(url_for("portfolio.mostrar_portfolio"))

    return aplicacion


# Creamos la aplicacion una sola vez, apenas se importa este archivo.
aplicacion = crear_aplicacion()

# Muchos servicios de publicacion buscan una variable llamada exactamente "app".
# Por eso dejamos este alias; la logica sigue estando en "aplicacion".
app = aplicacion


# Este bloque solo se ejecuta cuando corremos "python app.py".
if __name__ == "__main__":
    # En la computadora queremos ver errores si FLASK_DEBUG=1 en el .env.
    # En el hosting queremos ocultarlos si FLASK_DEBUG=0.
    modo_depuracion = os.getenv("FLASK_DEBUG", "0") == "1"

    # El hosting dice en que puerto escuchar; si no lo dice, usamos el 5000.
    puerto = int(os.getenv("PORT", "5000"))

    # host="0.0.0.0" permite que el servidor del hosting pueda conectarse.
    aplicacion.run(
        host="0.0.0.0",
        port=puerto,
        debug=modo_depuracion,
    )
