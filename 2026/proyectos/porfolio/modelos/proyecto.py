# modelos/proyecto.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Representar un proyecto realizado por la persona duena del portfolio.

from modelos.elemento_portfolio import ElementoPortfolio


class Proyecto(ElementoPortfolio):
    """
    Un proyecto del portfolio.

    Hereda id, titulo y descripcion de ElementoPortfolio.
    El "titulo" es el nombre del proyecto.
    """

    # POO - HERENCIA:
    # Proyecto hereda de ElementoPortfolio.
    # Aprovecha los getters y setters del id, el titulo y la descripcion.

    def __init__(
        self,
        id=0,
        perfil_id=1,
        nombre="",
        fecha="",
        descripcion="",
        enlace="",
        imagen="",
        orden=0,
    ):
        # Guardamos el nombre como titulo en la clase base.
        super().__init__(id, nombre, descripcion)

        # POO - ENCAPSULAMIENTO:
        # Los datos propios del proyecto son privados.
        self._perfil_id = perfil_id
        self._fecha = fecha
        self._enlace = enlace
        self._imagen = imagen
        self._orden = orden

    # -------------------- GETTERS --------------------

    def obtener_perfil_id(self):
        return self._perfil_id

    def obtener_fecha(self):
        return self._fecha

    def obtener_enlace(self):
        return self._enlace

    def obtener_imagen(self):
        return self._imagen

    def obtener_orden(self):
        return self._orden

    # -------------------- SETTERS --------------------

    def establecer_perfil_id(self, nuevo_perfil_id):
        self._perfil_id = nuevo_perfil_id

    def establecer_fecha(self, nueva_fecha):
        self._fecha = nueva_fecha

    def establecer_enlace(self, nuevo_enlace):
        self._enlace = nuevo_enlace

    def establecer_imagen(self, nueva_imagen):
        self._imagen = nueva_imagen

    def establecer_orden(self, nuevo_orden):
        self._orden = nuevo_orden

    # -------------------- MOSTRAR --------------------

    def mostrar(self):
        """
        Devuelve un resumen corto del proyecto.
        """

        # POO - POLIMORFISMO:
        # Proyecto redefine mostrar() a su manera.
        return self._titulo + " (" + str(self._fecha) + ")"

    # -------------------- GUARDAR --------------------

    def guardar(self, base_de_datos):
        """
        Inserta un proyecto nuevo en MySQL y devuelve su id.
        """

        consulta = """
            INSERT INTO proyectos
                (perfil_id, nombre, fecha, descripcion, enlace, imagen, orden)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._fecha,
            self._descripcion,
            self._enlace,
            self._imagen,
            self._orden,
        )

        nuevo_id = base_de_datos.ejecutar_insercion(consulta, parametros)
        self.establecer_id(nuevo_id)

        return nuevo_id

    # -------------------- ACTUALIZAR --------------------

    def actualizar(self, base_de_datos):
        """
        Actualiza un proyecto existente.
        Devuelve True si se modifico alguna fila.
        """

        if self._id == 0:
            return False

        consulta = """
            UPDATE proyectos
            SET perfil_id = %s,
                nombre = %s,
                fecha = %s,
                descripcion = %s,
                enlace = %s,
                imagen = %s,
                orden = %s
            WHERE id = %s
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._fecha,
            self._descripcion,
            self._enlace,
            self._imagen,
            self._orden,
            self._id,
        )

        filas_modificadas = base_de_datos.ejecutar_actualizacion(
            consulta, parametros
        )

        return filas_modificadas > 0

    # -------------------- ELIMINAR --------------------

    def eliminar(self, base_de_datos):
        """
        Elimina el proyecto actual usando su id.
        Devuelve True si se borro alguna fila.
        """

        if self._id == 0:
            return False

        consulta = "DELETE FROM proyectos WHERE id = %s"
        parametros = (self._id,)

        filas_borradas = base_de_datos.ejecutar_eliminacion(consulta, parametros)

        return filas_borradas > 0
