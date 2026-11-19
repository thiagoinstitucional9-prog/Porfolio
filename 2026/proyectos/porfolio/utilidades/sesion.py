# utilidades/sesion.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Guardar en un solo lugar las funciones que trabajan con la sesion de Flask.
#
# La sesion es una cookie firmada. Flask guarda dentro un identificador
# del usuario, pero NO guarda la contraseña.

from flask import redirect, session, url_for


def hay_sesion_iniciada():
    """
    Devuelve True si el usuario ya inicio sesion.
    """

    return "usuario_id" in session


def obtener_nombre_usuario():
    """
    Devuelve el nombre del usuario guardado en la sesion.
    """

    return session.get("usuario_nombre", "")


def iniciar_sesion(usuario):
    """
    Guarda los datos basicos del usuario en la sesion.

    Primero limpiamos la sesion anterior para evitar que queden datos
    viejos de otra persona.
    """

    session.clear()
    session["usuario_id"] = usuario["id"]
    session["usuario_nombre"] = usuario["nombre_usuario"]


def cerrar_sesion():
    """
    Borra todos los datos de la sesion actual.
    """

    session.clear()


def revisar_sesion_iniciada():
    """
    Revisa si hay una sesion iniciada.

    Si no hay sesion, devuelve una redireccion a la pagina principal
    con el modal de login abierto. Si hay sesion, devuelve None.
    """

    if hay_sesion_iniciada():
        return None

    return redirect(
        url_for(
            "portfolio.mostrar_portfolio",
            login="requerido",
            _anchor="login",
        )
    )
