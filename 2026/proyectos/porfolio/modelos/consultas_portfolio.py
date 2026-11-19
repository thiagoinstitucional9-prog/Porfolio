# modelos/consultas_portfolio.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Guardar las consultas SELECT que usa la pagina principal.
#
# Asi la ruta de Flask no se llena de SQL y las consultas quedan
# todas juntas en un solo lugar.

def obtener_perfil(base_de_datos):
    """
    Devuelve los datos personales del portfolio.
    Solamente existe un perfil, por eso usamos LIMIT 1.
    """

    consulta = """
        SELECT *
        FROM perfil
        ORDER BY id
        LIMIT 1
    """

    return base_de_datos.obtener_uno(consulta)


def obtener_redes_sociales(base_de_datos):
    """
    Devuelve las redes sociales ordenadas para el encabezado.
    """

    consulta = """
        SELECT *
        FROM redes_sociales
        ORDER BY orden, id
    """

    return base_de_datos.obtener_todos(consulta)


def obtener_experiencias(base_de_datos):
    """
    Devuelve todas las experiencias laborales.
    """

    consulta = """
        SELECT *
        FROM experiencias
        ORDER BY orden, id
    """

    return base_de_datos.obtener_todos(consulta)


def obtener_educacion(base_de_datos):
    """
    Devuelve todos los estudios.
    """

    consulta = """
        SELECT *
        FROM educacion
        ORDER BY orden, id
    """

    return base_de_datos.obtener_todos(consulta)


def obtener_skills(base_de_datos, categoria):
    """
    Devuelve las skills de una categoria.

    categoria puede ser "Hard" o "Soft".
    El valor no se pega directamente en el SQL: se manda como parametro
    con %s para que MySQL lo trate como un dato seguro.
    """

    consulta = """
        SELECT *
        FROM skills
        WHERE categoria = %s
        ORDER BY orden, id
    """

    parametros = (categoria,)
    return base_de_datos.obtener_todos(consulta, parametros)


def obtener_idiomas(base_de_datos):
    """
    Devuelve todos los idiomas.
    """

    consulta = """
        SELECT *
        FROM idiomas
        ORDER BY orden, id
    """

    return base_de_datos.obtener_todos(consulta)


def obtener_proyectos(base_de_datos):
    """
    Devuelve todos los proyectos.
    """

    consulta = """
        SELECT *
        FROM proyectos
        ORDER BY orden, id
    """

    return base_de_datos.obtener_todos(consulta)
