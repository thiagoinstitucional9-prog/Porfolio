# cambiar_clave.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Cambiar la contraseña de un usuario desde la consola.
#
# Uso:
#   python cambiar_clave.py
#
# El script no muestra la contraseña mientras se escribe.
# Tampoco la guarda en texto plano: genera un hash con werkzeug.

from getpass import getpass

from werkzeug.security import generate_password_hash

from modelos.base_de_datos import BaseDeDatos


def pedir_usuario():
    """
    Pide el nombre de usuario. Si se deja vacio, usa "admin".
    """

    usuario = input("Usuario (Enter para admin): ").strip()

    if usuario == "":
        return "admin"

    return usuario


def pedir_clave():
    """
    Pide la nueva contraseña dos veces y revisa que coincidan.
    """

    clave = getpass("Nueva contraseña: ")
    repeticion = getpass("Repetir contraseña: ")

    if len(clave) < 8:
        print("La contraseña debe tener al menos 8 caracteres.")
        return ""

    if clave != repeticion:
        print("Las contraseñas no coinciden.")
        return ""

    return clave


def main():
    """
    Pide los datos, actualiza el hash en MySQL y muestra el resultado.
    """

    print("Cambio de contraseña del portfolio")
    usuario = pedir_usuario()
    clave = pedir_clave()

    if clave == "":
        return

    base_de_datos = BaseDeDatos()

    if not base_de_datos.conectar():
        print("No se pudo conectar con MySQL. Revisá el archivo .env.")
        return

    try:
        consulta = """
            UPDATE usuarios
            SET clave_hash = %s
            WHERE nombre_usuario = %s
        """

        parametros = (generate_password_hash(clave), usuario)
        filas = base_de_datos.ejecutar_actualizacion(consulta, parametros)

        if filas == 0:
            print("No existe el usuario:", usuario)
        else:
            print("Contraseña actualizada correctamente para:", usuario)

    finally:
        base_de_datos.cerrar()


if __name__ == "__main__":
    main()
