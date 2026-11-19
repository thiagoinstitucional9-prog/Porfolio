# rutas/autenticacion.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Atender el inicio y el cierre de sesion.
#
# La contrasena nunca se guarda en la sesion ni se compara en texto plano.
# Se compara el hash guardado en MySQL con la clave escrita por el usuario.

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.security import check_password_hash

from formularios.formulario_login import FormularioLogin
from modelos.base_de_datos import BaseDeDatos
from modelos.consultas_usuario import obtener_usuario_por_nombre
from utilidades.sesion import (
    cerrar_sesion as borrar_sesion,
    hay_sesion_iniciada,
    iniciar_sesion as guardar_sesion,
)


# Blueprint que agrupa las rutas de login y logout.
autenticacion = Blueprint("autenticacion", __name__)


@autenticacion.route("/login", methods=["GET", "POST"])
def iniciar_sesion():
    """
    Revisa el usuario y la contrasena.

    Si los datos son correctos, guarda el id del usuario en la sesion.
    Si son incorrectos, vuelve a la pagina principal con un mensaje.
    """

    # Si ya hay una sesion, no hace falta volver a entrar.
    if hay_sesion_iniciada():
        flash("Ya tenés una sesión iniciada.", "info")
        return redirect(
            url_for("portfolio.mostrar_portfolio", _anchor="sobre-mi")
        )

    # Si alguien abre /login directamente, lo mandamos al modal.
    if request.method == "GET":
        return redirect(
            url_for(
                "portfolio.mostrar_portfolio",
                login="abrir",
                _anchor="login",
            )
        )

    formulario = FormularioLogin()

    # validate_on_submit revisa los campos y el token CSRF.
    if not formulario.validate_on_submit():
        return redirect(
            url_for(
                "portfolio.mostrar_portfolio",
                login="error",
                _anchor="login",
            )
        )

    nombre_usuario = formulario.nombre_usuario.data.strip()
    clave = formulario.clave.data

    base_de_datos = BaseDeDatos()

    if not base_de_datos.conectar():
        mensaje = (
            "No se pudo conectar con la base de datos para revisar el login. "
            "Comprobá que MySQL esté encendido."
        )
        return render_template("error_conexion.html", mensaje=mensaje), 500

    try:
        usuario = obtener_usuario_por_nombre(base_de_datos, nombre_usuario)

        # Si el usuario no existe o la clave no coincide, mostramos
        # el mismo mensaje. Asi no revelamos cual de los dos datos fallo.
        if usuario is None or not check_password_hash(
            usuario["clave_hash"], clave
        ):
            return redirect(
                url_for(
                    "portfolio.mostrar_portfolio",
                    login="error",
                    _anchor="login",
                )
            )

        guardar_sesion(usuario)

    finally:
        base_de_datos.cerrar()

    flash("Sesión iniciada. Ya podés editar el portfolio.", "success")
    return redirect(
        url_for("portfolio.mostrar_portfolio", _anchor="sobre-mi")
    )


@autenticacion.route("/logout", methods=["POST"])
def cerrar_sesion():
    """
    Borra la sesion actual.

    Solamente acepta POST porque el boton de salir es un formulario
    con token CSRF. Asi otra pagina no puede cerrar la sesion sin permiso.
    """

    if not hay_sesion_iniciada():
        flash("No hay una sesión iniciada.", "info")
        return redirect(url_for("portfolio.mostrar_portfolio"))

    borrar_sesion()
    flash("Sesión cerrada correctamente.", "info")

    return redirect(url_for("portfolio.mostrar_portfolio"))
