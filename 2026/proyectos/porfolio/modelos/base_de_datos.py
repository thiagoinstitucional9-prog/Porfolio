# modelos/base_de_datos.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Abrir la conexion con MySQL, ejecutar consultas SQL y cerrar la conexion.
#
# Esta clase NO sabe que es una experiencia o un proyecto.
# Solo sabe hablar con MySQL. Esa separacion hace que el codigo sea mas facil
# de entender y de explicar.

import mysql.connector

from configuracion import obtener_datos_base_de_datos


class BaseDeDatos:
    """
    Representa la conexion con la base de datos MySQL.

    Guarda dos objetos importantes:
    - _conexion: la conexion completa con el servidor MySQL.
    - _cursor: el objeto que permite ejecutar consultas y leer resultados.
    """

    # POO - ENCAPSULAMIENTO:
    # Los atributos _conexion y _cursor son privados por convencion.
    # El guion bajo indica que no se deben usar directamente desde afuera.
    # Para trabajar con ellos existen los metodos de esta clase.

    def __init__(self):
        # Al principio todavia no hay conexion.
        self._conexion = None
        self._cursor = None

    def conectar(self):
        """
        Abre la conexion con MySQL.

        Devuelve True si pudo conectar y False si hubo un error.
        """

        # Si ya habia una conexion abierta, la cerramos antes de abrir otra.
        if self._conexion is not None:
            self.cerrar()

        datos = obtener_datos_base_de_datos()

        try:
            self._conexion = mysql.connector.connect(
                host=datos["host"],
                port=datos["puerto"],
                user=datos["usuario"],
                password=datos["clave"],
                database=datos["nombre_base"],
                charset="utf8mb4",
                # FOUND_ROWS hace que un UPDATE cuente las filas que
                # coinciden con el WHERE, aunque los datos no hayan cambiado.
                # Asi guardar un formulario sin modificaciones no se
                # confunde con un error.
                client_flags=[mysql.connector.ClientFlag.FOUND_ROWS],
            )

            # dictionary=True hace que cada fila llegue como un diccionario.
            # Ejemplo: {"id": 1, "nombre": "Thiago"}
            # Es mas facil de leer en los templates de Jinja2.
            self._cursor = self._conexion.cursor(dictionary=True)

            return True

        except mysql.connector.Error as error:
            # Mostramos el error en la consola para poder revisarlo.
            # No mostramos la contrasena ni datos sensibles.
            print("No se pudo conectar con MySQL.")
            print("Detalle del error:", error)

            self._conexion = None
            self._cursor = None
            return False

    def cerrar(self):
        """
        Cierra el cursor y la conexion si estan abiertos.
        """

        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None

        if self._conexion is not None:
            if self._conexion.is_connected():
                self._conexion.close()

        self._conexion = None

    def esta_conectada(self):
        """
        Devuelve True si la conexion sigue activa.
        """

        if self._conexion is None:
            return False

        return self._conexion.is_connected()

    def _preparar_consulta(self, consulta_sql, parametros):
        """
        Metodo privado que ejecuta una consulta sin devolver resultados.

        Se usa desde los otros metodos para no repetir siempre
        la misma comprobacion y la misma llamada a execute().
        """

        # POO - ENCAPSULAMIENTO:
        # Este metodo es privado (empieza con _) porque es un detalle interno.
        # Quien use BaseDeDatos no necesita llamarlo directamente.

        if self._conexion is None or self._cursor is None:
            raise RuntimeError(
                "No hay conexion con la base de datos. "
                "Primero hay que llamar al metodo conectar()."
            )

        if parametros is None:
            self._cursor.execute(consulta_sql)
        else:
            # Usamos %s como marcador de posicion.
            # MySQL Connector coloca los valores de forma segura.
            # Esto ayuda a evitar inyecciones SQL.
            self._cursor.execute(consulta_sql, parametros)

    def obtener_todos(self, consulta_sql, parametros=None):
        """
        Ejecuta un SELECT y devuelve todas las filas encontradas.

        Cada fila es un diccionario. Si no hay resultados, devuelve [].
        """

        self._preparar_consulta(consulta_sql, parametros)
        return self._cursor.fetchall()

    def obtener_uno(self, consulta_sql, parametros=None):
        """
        Ejecuta un SELECT y devuelve la primera fila encontrada.

        Si no encuentra nada, devuelve None.
        """

        self._preparar_consulta(consulta_sql, parametros)
        return self._cursor.fetchone()

    def ejecutar_insercion(self, consulta_sql, parametros=None):
        """
        Ejecuta un INSERT y devuelve el id generado por MySQL.
        """

        self._preparar_consulta(consulta_sql, parametros)

        # Confirmamos el cambio para que quede guardado de verdad.
        self._conexion.commit()

        return self._cursor.lastrowid

    def ejecutar_actualizacion(self, consulta_sql, parametros=None):
        """
        Ejecuta un UPDATE y devuelve cuantas filas se modificaron.
        """

        self._preparar_consulta(consulta_sql, parametros)
        self._conexion.commit()

        return self._cursor.rowcount

    def ejecutar_eliminacion(self, consulta_sql, parametros=None):
        """
        Ejecuta un DELETE y devuelve cuantas filas se borraron.
        """

        self._preparar_consulta(consulta_sql, parametros)
        self._conexion.commit()

        return self._cursor.rowcount
