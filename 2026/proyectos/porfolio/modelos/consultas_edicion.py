# modelos/consultas_edicion.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Guardar las consultas SQL que no tienen una clase propia.
#
# Por ejemplo, el perfil es un unico registro y no se maneja como una
# lista de elementos. Por eso actualizarlo con una funcion es suficiente.

def actualizar_perfil(base_de_datos, perfil_id, datos):
    """
    Actualiza los datos personales del perfil.

    Recibe un diccionario con las claves:
    nombre_completo, titulo_profesional, resumen, texto_banner,
    foto_perfil, imagen_banner, archivo_cv, correo y ubicacion.

    Devuelve True si se modifico alguna fila.
    """

    consulta = """
        UPDATE perfil
        SET nombre_completo = %s,
            titulo_profesional = %s,
            resumen = %s,
            texto_banner = %s,
            foto_perfil = %s,
            imagen_banner = %s,
            archivo_cv = %s,
            correo = %s,
            ubicacion = %s
        WHERE id = %s
    """

    parametros = (
        datos["nombre_completo"],
        datos["titulo_profesional"],
        datos["resumen"],
        datos["texto_banner"],
        datos["foto_perfil"],
        datos["imagen_banner"],
        datos["archivo_cv"],
        datos["correo"],
        datos["ubicacion"],
        perfil_id,
    )

    filas_modificadas = base_de_datos.ejecutar_actualizacion(
        consulta, parametros
    )

    return filas_modificadas > 0


def actualizar_orden(base_de_datos, tipo, id_elemento, nuevo_orden):
    """
    Cambia el numero de orden de un elemento.

    El "tipo" dice en que tabla está el elemento. Elegimos la consulta con un
    if/elif porque el nombre de la tabla NO se puede mandar como parámetro %s.
    Así solamente se pueden usar las tablas que escribimos acá.
    """

    if tipo == "experiencias":
        consulta = "UPDATE experiencias SET orden = %s WHERE id = %s"
    elif tipo == "educacion":
        consulta = "UPDATE educacion SET orden = %s WHERE id = %s"
    elif tipo == "skills_hard" or tipo == "skills_soft":
        consulta = "UPDATE skills SET orden = %s WHERE id = %s"
    elif tipo == "idiomas":
        consulta = "UPDATE idiomas SET orden = %s WHERE id = %s"
    elif tipo == "proyectos":
        consulta = "UPDATE proyectos SET orden = %s WHERE id = %s"
    elif tipo == "redes_sociales":
        consulta = "UPDATE redes_sociales SET orden = %s WHERE id = %s"
    else:
        # Si llegó un tipo desconocido, no hacemos nada.
        return False

    parametros = (nuevo_orden, id_elemento)
    filas_modificadas = base_de_datos.ejecutar_actualizacion(
        consulta, parametros
    )

    return filas_modificadas > 0
