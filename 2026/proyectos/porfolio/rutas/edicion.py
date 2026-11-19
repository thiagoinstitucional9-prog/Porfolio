# rutas/edicion.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Atender las rutas que agregan, editan y eliminan contenido.
#
# Todas las rutas de este archivo estan protegidas: si no hay una sesion
# iniciada, la persona vuelve a la pagina principal con el login abierto.

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from modelos.base_de_datos import BaseDeDatos
from modelos.consultas_edicion import actualizar_orden, actualizar_perfil
from modelos.consultas_portfolio import obtener_perfil
from modelos.educacion import Educacion
from modelos.experiencia import Experiencia
from modelos.idioma import Idioma
from modelos.proyecto import Proyecto
from modelos.red_social import RedSocial
from modelos.skill import Skill
from utilidades.sesion import revisar_sesion_iniciada


# Blueprint que agrupa todas las rutas de edicion.
paginas_edicion = Blueprint("edicion", __name__)


MENSAJE_SIN_BASE = (
    "No se pudo conectar con la base de datos para guardar los cambios. "
    "Comprobá que MySQL esté encendido."
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_texto(nombre_campo):
    """
    Lee un campo de texto del formulario y le quita los espacios sobrantes.
    """

    return request.form.get(nombre_campo, "").strip()


def obtener_entero(nombre_campo, valor_inicial=0):
    """
    Lee un campo numerico. Si viene vacio o con un error, usa un valor inicial.
    """

    texto = request.form.get(nombre_campo, "").strip()

    if texto == "":
        return valor_inicial

    try:
        return int(texto)
    except ValueError:
        return valor_inicial


def obtener_fecha(nombre_campo):
    """
    Revisa que la fecha tenga el formato que espera MySQL: AAAA-MM-DD.
    """

    texto = obtener_texto(nombre_campo)

    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return texto
    except ValueError:
        return ""


def conectar_base_de_datos():
    """
    Crea y abre una conexion. Si falla, devuelve None.
    """

    base_de_datos = BaseDeDatos()

    if base_de_datos.conectar():
        return base_de_datos

    return None


def respuesta_error_base_de_datos():
    """
    Devuelve la pagina de error cuando MySQL no responde.
    """

    return render_template("error_conexion.html", mensaje=MENSAJE_SIN_BASE), 500


def redirigir_a(ancla):
    """
    Vuelve a la pagina principal y baja hasta la seccion indicada.
    """

    return redirect(url_for("portfolio.mostrar_portfolio", _anchor=ancla))


def faltan_datos(datos, campos_obligatorios):
    """
    Devuelve True si alguno de los campos obligatorios esta vacio.
    """

    for nombre_campo in campos_obligatorios:
        if datos[nombre_campo] == "":
            return True

    return False


# ============================================================
# PERFIL
# ============================================================

@paginas_edicion.route("/perfil/editar", methods=["POST"])
def editar_perfil():
    """
    Actualiza los datos personales del perfil.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para editar.", "danger")
            return redirigir_a("sobre-mi")

        datos = {
            "nombre_completo": obtener_texto("nombre_completo"),
            "titulo_profesional": obtener_texto("titulo_profesional"),
            "resumen": obtener_texto("resumen"),
            "texto_banner": obtener_texto("texto_banner"),
            "foto_perfil": obtener_texto("foto_perfil"),
            "imagen_banner": obtener_texto("imagen_banner"),
            "archivo_cv": obtener_texto("archivo_cv"),
            "correo": obtener_texto("correo"),
            "ubicacion": obtener_texto("ubicacion"),
            "mapa_url": obtener_texto("mapa_url"),
        }

        campos_obligatorios = [
            "nombre_completo",
            "titulo_profesional",
            "resumen",
            "texto_banner",
            "foto_perfil",
            "imagen_banner",
            "archivo_cv",
            "correo",
            "ubicacion",
            "mapa_url",
        ]

        if faltan_datos(datos, campos_obligatorios):
            flash("Completá todos los datos del perfil.", "danger")
            return redirigir_a("sobre-mi")

        if actualizar_perfil(base_de_datos, perfil["id"], datos):
            flash("Perfil actualizado correctamente.", "success")
        else:
            flash("No se pudo actualizar el perfil.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("sobre-mi")


# ============================================================
# EXPERIENCIAS
# ============================================================

@paginas_edicion.route("/experiencias/agregar", methods=["POST"])
def agregar_experiencia():
    """
    Agrega una experiencia laboral nueva.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para guardar la experiencia.", "danger")
            return redirigir_a("experiencia")

        datos = {
            "puesto": obtener_texto("puesto"),
            "empresa": obtener_texto("empresa"),
            "periodo": obtener_texto("periodo"),
            "descripcion": obtener_texto("descripcion"),
            "logo": obtener_texto("logo"),
        }

        if faltan_datos(
            datos,
            ["puesto", "empresa", "periodo", "descripcion", "logo"],
        ):
            flash("Completá todos los datos de la experiencia.", "danger")
            return redirigir_a("experiencia")

        experiencia = Experiencia(
            perfil_id=perfil["id"],
            puesto=datos["puesto"],
            empresa=datos["empresa"],
            periodo=datos["periodo"],
            descripcion=datos["descripcion"],
            logo=datos["logo"],
            orden=obtener_entero("orden", 0),
        )

        experiencia.guardar(base_de_datos)
        flash("Experiencia agregada correctamente.", "success")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("experiencia")


@paginas_edicion.route(
    "/experiencias/<int:experiencia_id>/editar",
    methods=["POST"],
)
def editar_experiencia(experiencia_id):
    """
    Actualiza una experiencia laboral existente.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para editar la experiencia.", "danger")
            return redirigir_a("experiencia")

        datos = {
            "puesto": obtener_texto("puesto"),
            "empresa": obtener_texto("empresa"),
            "periodo": obtener_texto("periodo"),
            "descripcion": obtener_texto("descripcion"),
            "logo": obtener_texto("logo"),
        }

        if faltan_datos(
            datos,
            ["puesto", "empresa", "periodo", "descripcion", "logo"],
        ):
            flash("Completá todos los datos de la experiencia.", "danger")
            return redirigir_a("experiencia")

        experiencia = Experiencia(
            id=experiencia_id,
            perfil_id=perfil["id"],
            puesto=datos["puesto"],
            empresa=datos["empresa"],
            periodo=datos["periodo"],
            descripcion=datos["descripcion"],
            logo=datos["logo"],
            orden=obtener_entero("orden", 0),
        )

        if experiencia.actualizar(base_de_datos):
            flash("Experiencia actualizada correctamente.", "success")
        else:
            flash("No se encontró la experiencia para actualizar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("experiencia")


@paginas_edicion.route(
    "/experiencias/<int:experiencia_id>/eliminar",
    methods=["POST"],
)
def eliminar_experiencia(experiencia_id):
    """
    Elimina una experiencia laboral.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        experiencia = Experiencia(id=experiencia_id)

        if experiencia.eliminar(base_de_datos):
            flash("Experiencia eliminada correctamente.", "info")
        else:
            flash("No se encontró la experiencia para eliminar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("experiencia")


# ============================================================
# EDUCACION
# ============================================================

@paginas_edicion.route("/educacion/agregar", methods=["POST"])
def agregar_educacion():
    """
    Agrega un estudio nuevo.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para guardar el estudio.", "danger")
            return redirigir_a("educacion")

        datos = {
            "titulo": obtener_texto("titulo"),
            "institucion": obtener_texto("institucion"),
            "periodo": obtener_texto("periodo"),
            "descripcion": obtener_texto("descripcion"),
            "logo": obtener_texto("logo"),
        }

        if faltan_datos(
            datos,
            ["titulo", "institucion", "periodo", "descripcion", "logo"],
        ):
            flash("Completá todos los datos del estudio.", "danger")
            return redirigir_a("educacion")

        estudio = Educacion(
            perfil_id=perfil["id"],
            titulo=datos["titulo"],
            institucion=datos["institucion"],
            periodo=datos["periodo"],
            descripcion=datos["descripcion"],
            logo=datos["logo"],
            orden=obtener_entero("orden", 0),
        )

        estudio.guardar(base_de_datos)
        flash("Estudio agregado correctamente.", "success")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("educacion")


@paginas_edicion.route(
    "/educacion/<int:educacion_id>/editar",
    methods=["POST"],
)
def editar_educacion(educacion_id):
    """
    Actualiza un estudio existente.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para editar el estudio.", "danger")
            return redirigir_a("educacion")

        datos = {
            "titulo": obtener_texto("titulo"),
            "institucion": obtener_texto("institucion"),
            "periodo": obtener_texto("periodo"),
            "descripcion": obtener_texto("descripcion"),
            "logo": obtener_texto("logo"),
        }

        if faltan_datos(
            datos,
            ["titulo", "institucion", "periodo", "descripcion", "logo"],
        ):
            flash("Completá todos los datos del estudio.", "danger")
            return redirigir_a("educacion")

        estudio = Educacion(
            id=educacion_id,
            perfil_id=perfil["id"],
            titulo=datos["titulo"],
            institucion=datos["institucion"],
            periodo=datos["periodo"],
            descripcion=datos["descripcion"],
            logo=datos["logo"],
            orden=obtener_entero("orden", 0),
        )

        if estudio.actualizar(base_de_datos):
            flash("Estudio actualizado correctamente.", "success")
        else:
            flash("No se encontró el estudio para actualizar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("educacion")


@paginas_edicion.route(
    "/educacion/<int:educacion_id>/eliminar",
    methods=["POST"],
)
def eliminar_educacion(educacion_id):
    """
    Elimina un estudio.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        estudio = Educacion(id=educacion_id)

        if estudio.eliminar(base_de_datos):
            flash("Estudio eliminado correctamente.", "info")
        else:
            flash("No se encontró el estudio para eliminar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("educacion")


# ============================================================
# SKILLS
# ============================================================

@paginas_edicion.route("/skills/agregar", methods=["POST"])
def agregar_skill():
    """
    Agrega una habilidad nueva.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para guardar la habilidad.", "danger")
            return redirigir_a("skills")

        nombre = obtener_texto("nombre")
        categoria = obtener_texto("categoria")

        if nombre == "" or categoria not in ("Hard", "Soft"):
            flash("Completá el nombre y la categoría de la habilidad.", "danger")
            return redirigir_a("skills")

        skill = Skill(
            perfil_id=perfil["id"],
            nombre=nombre,
            porcentaje=obtener_entero("porcentaje", 0),
            categoria=categoria,
            orden=obtener_entero("orden", 0),
        )

        skill.guardar(base_de_datos)
        flash("Habilidad agregada correctamente.", "success")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("skills")


@paginas_edicion.route("/skills/<int:skill_id>/editar", methods=["POST"])
def editar_skill(skill_id):
    """
    Actualiza una habilidad existente.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para editar la habilidad.", "danger")
            return redirigir_a("skills")

        nombre = obtener_texto("nombre")
        categoria = obtener_texto("categoria")

        if nombre == "" or categoria not in ("Hard", "Soft"):
            flash("Completá el nombre y la categoría de la habilidad.", "danger")
            return redirigir_a("skills")

        skill = Skill(
            id=skill_id,
            perfil_id=perfil["id"],
            nombre=nombre,
            porcentaje=obtener_entero("porcentaje", 0),
            categoria=categoria,
            orden=obtener_entero("orden", 0),
        )

        if skill.actualizar(base_de_datos):
            flash("Habilidad actualizada correctamente.", "success")
        else:
            flash("No se encontró la habilidad para actualizar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("skills")


@paginas_edicion.route("/skills/<int:skill_id>/eliminar", methods=["POST"])
def eliminar_skill(skill_id):
    """
    Elimina una habilidad.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        skill = Skill(id=skill_id)

        if skill.eliminar(base_de_datos):
            flash("Habilidad eliminada correctamente.", "info")
        else:
            flash("No se encontró la habilidad para eliminar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("skills")


# ============================================================
# IDIOMAS
# ============================================================

@paginas_edicion.route("/idiomas/agregar", methods=["POST"])
def agregar_idioma():
    """
    Agrega un idioma nuevo.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para guardar el idioma.", "danger")
            return redirigir_a("skills")

        nombre = obtener_texto("nombre")
        nivel = obtener_texto("nivel")

        if nombre == "" or nivel == "":
            flash("Completá el nombre y el nivel del idioma.", "danger")
            return redirigir_a("skills")

        idioma = Idioma(
            perfil_id=perfil["id"],
            nombre=nombre,
            nivel=nivel,
            porcentaje=obtener_entero("porcentaje", 0),
            orden=obtener_entero("orden", 0),
        )

        idioma.guardar(base_de_datos)
        flash("Idioma agregado correctamente.", "success")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("skills")


@paginas_edicion.route("/idiomas/<int:idioma_id>/editar", methods=["POST"])
def editar_idioma(idioma_id):
    """
    Actualiza un idioma existente.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para editar el idioma.", "danger")
            return redirigir_a("skills")

        nombre = obtener_texto("nombre")
        nivel = obtener_texto("nivel")

        if nombre == "" or nivel == "":
            flash("Completá el nombre y el nivel del idioma.", "danger")
            return redirigir_a("skills")

        idioma = Idioma(
            id=idioma_id,
            perfil_id=perfil["id"],
            nombre=nombre,
            nivel=nivel,
            porcentaje=obtener_entero("porcentaje", 0),
            orden=obtener_entero("orden", 0),
        )

        if idioma.actualizar(base_de_datos):
            flash("Idioma actualizado correctamente.", "success")
        else:
            flash("No se encontró el idioma para actualizar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("skills")


@paginas_edicion.route("/idiomas/<int:idioma_id>/eliminar", methods=["POST"])
def eliminar_idioma(idioma_id):
    """
    Elimina un idioma.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        idioma = Idioma(id=idioma_id)

        if idioma.eliminar(base_de_datos):
            flash("Idioma eliminado correctamente.", "info")
        else:
            flash("No se encontró el idioma para eliminar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("skills")


# ============================================================
# PROYECTOS
# ============================================================

@paginas_edicion.route("/proyectos/agregar", methods=["POST"])
def agregar_proyecto():
    """
    Agrega un proyecto nuevo.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para guardar el proyecto.", "danger")
            return redirigir_a("proyectos")

        datos = {
            "nombre": obtener_texto("nombre"),
            "fecha": obtener_fecha("fecha"),
            "descripcion": obtener_texto("descripcion"),
            "enlace": obtener_texto("enlace"),
            "imagen": obtener_texto("imagen"),
        }

        if faltan_datos(
            datos,
            ["nombre", "fecha", "descripcion", "enlace", "imagen"],
        ):
            flash("Completá todos los datos del proyecto.", "danger")
            return redirigir_a("proyectos")

        proyecto = Proyecto(
            perfil_id=perfil["id"],
            nombre=datos["nombre"],
            fecha=datos["fecha"],
            descripcion=datos["descripcion"],
            enlace=datos["enlace"],
            imagen=datos["imagen"],
            orden=obtener_entero("orden", 0),
        )

        proyecto.guardar(base_de_datos)
        flash("Proyecto agregado correctamente.", "success")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("proyectos")


@paginas_edicion.route(
    "/proyectos/<int:proyecto_id>/editar",
    methods=["POST"],
)
def editar_proyecto(proyecto_id):
    """
    Actualiza un proyecto existente.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para editar el proyecto.", "danger")
            return redirigir_a("proyectos")

        datos = {
            "nombre": obtener_texto("nombre"),
            "fecha": obtener_fecha("fecha"),
            "descripcion": obtener_texto("descripcion"),
            "enlace": obtener_texto("enlace"),
            "imagen": obtener_texto("imagen"),
        }

        if faltan_datos(
            datos,
            ["nombre", "fecha", "descripcion", "enlace", "imagen"],
        ):
            flash("Completá todos los datos del proyecto.", "danger")
            return redirigir_a("proyectos")

        proyecto = Proyecto(
            id=proyecto_id,
            perfil_id=perfil["id"],
            nombre=datos["nombre"],
            fecha=datos["fecha"],
            descripcion=datos["descripcion"],
            enlace=datos["enlace"],
            imagen=datos["imagen"],
            orden=obtener_entero("orden", 0),
        )

        if proyecto.actualizar(base_de_datos):
            flash("Proyecto actualizado correctamente.", "success")
        else:
            flash("No se encontró el proyecto para actualizar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("proyectos")


@paginas_edicion.route(
    "/proyectos/<int:proyecto_id>/eliminar",
    methods=["POST"],
)
def eliminar_proyecto(proyecto_id):
    """
    Elimina un proyecto.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        proyecto = Proyecto(id=proyecto_id)

        if proyecto.eliminar(base_de_datos):
            flash("Proyecto eliminado correctamente.", "info")
        else:
            flash("No se encontró el proyecto para eliminar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("proyectos")


# ============================================================
# REDES SOCIALES
# ============================================================

@paginas_edicion.route("/redes/agregar", methods=["POST"])
def agregar_red_social():
    """
    Agrega una red social nueva.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para guardar la red social.", "danger")
            return redirigir_a("redes-sociales-admin")

        datos = {
            "nombre": obtener_texto("nombre"),
            "enlace": obtener_texto("enlace"),
            "icono": obtener_texto("icono"),
        }

        if faltan_datos(datos, ["nombre", "enlace", "icono"]):
            flash("Completá todos los datos de la red social.", "danger")
            return redirigir_a("redes-sociales-admin")

        red_social = RedSocial(
            perfil_id=perfil["id"],
            nombre=datos["nombre"],
            enlace=datos["enlace"],
            icono=datos["icono"],
            orden=obtener_entero("orden", 0),
        )

        red_social.guardar(base_de_datos)
        flash("Red social agregada correctamente.", "success")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("redes-sociales-admin")


@paginas_edicion.route(
    "/redes/<int:red_social_id>/editar",
    methods=["POST"],
)
def editar_red_social(red_social_id):
    """
    Actualiza una red social existente.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        perfil = obtener_perfil(base_de_datos)

        if perfil is None:
            flash("No se encontró el perfil para editar la red social.", "danger")
            return redirigir_a("redes-sociales-admin")

        datos = {
            "nombre": obtener_texto("nombre"),
            "enlace": obtener_texto("enlace"),
            "icono": obtener_texto("icono"),
        }

        if faltan_datos(datos, ["nombre", "enlace", "icono"]):
            flash("Completá todos los datos de la red social.", "danger")
            return redirigir_a("redes-sociales-admin")

        red_social = RedSocial(
            id=red_social_id,
            perfil_id=perfil["id"],
            nombre=datos["nombre"],
            enlace=datos["enlace"],
            icono=datos["icono"],
            orden=obtener_entero("orden", 0),
        )

        if red_social.actualizar(base_de_datos):
            flash("Red social actualizada correctamente.", "success")
        else:
            flash("No se encontró la red social para actualizar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("redes-sociales-admin")


@paginas_edicion.route(
    "/redes/<int:red_social_id>/eliminar",
    methods=["POST"],
)
def eliminar_red_social(red_social_id):
    """
    Elimina una red social.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        red_social = RedSocial(id=red_social_id)

        if red_social.eliminar(base_de_datos):
            flash("Red social eliminada correctamente.", "info")
        else:
            flash("No se encontró la red social para eliminar.", "warning")

    finally:
        base_de_datos.cerrar()

    return redirigir_a("redes-sociales-admin")


# ============================================================
# ORDEN CON DRAG AND DROP
# ============================================================

def obtener_ancla_por_tipo(tipo):
    """
    Devuelve el id de la sección adonde hay que volver después de guardar.

    Si el tipo no es conocido, devuelve un texto vacío para avisar del error.
    """

    if tipo == "experiencias":
        return "experiencia"
    if tipo == "educacion":
        return "educacion"
    if tipo == "skills_hard" or tipo == "skills_soft":
        return "skills"
    if tipo == "idiomas":
        return "skills"
    if tipo == "proyectos":
        return "proyectos"
    if tipo == "redes_sociales":
        return "redes-sociales-admin"

    return ""


def convertir_lista_de_ids(texto_ids):
    """
    Convierte un texto como "3,1,8" en la lista [3, 1, 8].

    Los valores que no sean números se ignoran. Así un dato raro no rompe
    la página.
    """

    lista_ids = []

    for parte in texto_ids.split(","):
        texto = parte.strip()

        if texto == "":
            continue

        try:
            lista_ids.append(int(texto))
        except ValueError:
            continue

    return lista_ids


@paginas_edicion.route("/orden/guardar", methods=["POST"])
def guardar_orden():
    """
    Guarda el orden nuevo que dejó el usuario al arrastrar las tarjetas.

    JavaScript manda los ids en el orden en que quedaron en la pantalla.
    Acá les damos los números 1, 2, 3... y los guardamos en MySQL.
    """

    respuesta = revisar_sesion_iniciada()
    if respuesta is not None:
        return respuesta

    tipo = obtener_texto("tipo")
    texto_ids = obtener_texto("ids")
    ancla = obtener_ancla_por_tipo(tipo)

    if ancla == "":
        flash("No se reconoció la sección que se quiso ordenar.", "danger")
        return redirigir_a("sobre-mi")

    lista_ids = convertir_lista_de_ids(texto_ids)

    if len(lista_ids) == 0:
        flash("No se recibió ningún elemento para ordenar.", "warning")
        return redirigir_a(ancla)

    base_de_datos = conectar_base_de_datos()
    if base_de_datos is None:
        return respuesta_error_base_de_datos()

    try:
        numero_de_orden = 1

        for id_elemento in lista_ids:
            actualizar_orden(
                base_de_datos,
                tipo,
                id_elemento,
                numero_de_orden,
            )
            numero_de_orden = numero_de_orden + 1

        flash("Orden guardado correctamente.", "success")

    finally:
        base_de_datos.cerrar()

    return redirigir_a(ancla)
