# modelos/consultas_usuario.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Guardar la consulta SQL que busca al usuario que intenta iniciar sesion.

def obtener_usuario_por_nombre(base_de_datos, nombre_usuario):
    """
    Busca un usuario por su nombre.

    Devuelve un diccionario con id, nombre_usuario y clave_hash.
    Si no existe, devuelve None.
    """

    consulta = """
        SELECT id, nombre_usuario, clave_hash
        FROM usuarios
        WHERE nombre_usuario = %s
        LIMIT 1
    """

    parametros = (nombre_usuario,)
    return base_de_datos.obtener_uno(consulta, parametros)
