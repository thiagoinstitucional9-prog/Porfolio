# rutas/portfolio.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Atender la pagina principal del portfolio.
#
# Esta ruta LEE los datos que se muestran en el sitio.
# Tambien prepara el estado del login para mostrar el encabezado correcto
# y para abrir el modal cuando hace falta.

from datetime import date

from flask import Blueprint, render_template, request

from formularios.formulario_login import FormularioLogin
from modelos.base_de_datos import BaseDeDatos
from modelos.consultas_portfolio import (
    obtener_educacion,
    obtener_experiencias,
    obtener_idiomas,
    obtener_perfil,
    obtener_proyectos,
    obtener_redes_sociales,
    obtener_skills,
)
from utilidades.sesion import hay_sesion_iniciada, obtener_nombre_usuario


# Un Blueprint agrupa rutas relacionadas.
# En este caso, todas las rutas publicas del portfolio.
paginas_portfolio = Blueprint("portfolio", __name__)


@paginas_portfolio.route("/")
def mostrar_portfolio():
    """
    Muestra la pagina principal con todas las secciones.
    """

    # Creamos el objeto que sabe hablar con MySQL.
    base_de_datos = BaseDeDatos()

    # Intentamos abrir la conexion.
    if not base_de_datos.conectar():
        mensaje = (
            "No se pudo conectar con la base de datos. "
            "Revisá los datos del archivo .env y comprobá que MySQL esté encendido."
        )
        return render_template("error_conexion.html", mensaje=mensaje), 500

    try:
        # -------------------- CONSULTAS --------------------

        perfil = obtener_perfil(base_de_datos)

        # Si no hay perfil, no tiene sentido mostrar el portfolio.
        if perfil is None:
            mensaje = (
                "La base de datos está conectada, pero no tiene un perfil. "
                "Ejecutá el archivo base_datos.sql para cargar los datos de ejemplo."
            )
            return render_template("error_conexion.html", mensaje=mensaje), 500

        redes_sociales = obtener_redes_sociales(base_de_datos)
        experiencias = obtener_experiencias(base_de_datos)
        educacion = obtener_educacion(base_de_datos)
        skills_duras = obtener_skills(base_de_datos, "Hard")
        skills_blandas = obtener_skills(base_de_datos, "Soft")
        idiomas = obtener_idiomas(base_de_datos)
        proyectos = obtener_proyectos(base_de_datos)

    finally:
        # Pase lo que pase, cerramos la conexion.
        # Asi no quedan conexiones abiertas ocupando recursos.
        base_de_datos.cerrar()

    # -------------------- ESTADO DEL LOGIN --------------------
    # La ruta puede recibir ?login=error, ?login=requerido o ?login=abrir.
    # Ese valor se usa para abrir el modal de login cuando hace falta.
    estado_login = request.args.get("login", "")
    mensaje_login = ""
    abrir_modal_login = False
    sesion_iniciada = hay_sesion_iniciada()

    if estado_login == "error":
        mensaje_login = (
            "Usuario o contraseña incorrectos. "
            "Revisá los datos e intentá de nuevo."
        )
        abrir_modal_login = True
    elif estado_login == "formulario":
        mensaje_login = (
            "Faltan datos en el formulario. "
            "Escribí el usuario y la contraseña."
        )
        abrir_modal_login = True
    elif estado_login == "requerido":
        mensaje_login = "Iniciá sesión para poder editar el portfolio."
        abrir_modal_login = True
    elif estado_login == "abrir":
        abrir_modal_login = True

    # -------------------- RENDERIZADO --------------------
    # render_template busca el archivo index.html dentro de la carpeta templates.
    # Las variables que pasamos aca quedan disponibles dentro del HTML con Jinja2.
    return render_template(
        "index.html",
        perfil=perfil,
        redes_sociales=redes_sociales,
        experiencias=experiencias,
        educacion=educacion,
        skills_duras=skills_duras,
        skills_blandas=skills_blandas,
        idiomas=idiomas,
        proyectos=proyectos,
        anio_actual=date.today().year,
        formulario_login=FormularioLogin(),
        sesion_iniciada=sesion_iniciada,
        nombre_usuario=obtener_nombre_usuario(),
        mensaje_login=mensaje_login,
        abrir_modal_login=abrir_modal_login,
    )
