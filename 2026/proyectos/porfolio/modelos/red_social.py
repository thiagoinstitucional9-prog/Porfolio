# modelos/red_social.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Representar una red social del portfolio.

from modelos.elemento_portfolio import ElementoPortfolio


class RedSocial(ElementoPortfolio):
    """
    Una red social que se muestra en el encabezado y en el pie.

    Hereda id, titulo y descripcion de ElementoPortfolio.
    En esta clase, el "titulo" es el nombre de la red.
    """

    # POO - HERENCIA:
    # RedSocial hereda de ElementoPortfolio y reutiliza el id y el titulo.

    def __init__(
        self,
        id=0,
        perfil_id=1,
        nombre="",
        enlace="",
        icono="",
        orden=0,
    ):
        # El nombre se guarda como titulo en la clase base.
        super().__init__(id, nombre, "")

        # POO - ENCAPSULAMIENTO:
        # El enlace, el icono y el orden son datos propios de RedSocial.
        self._perfil_id = perfil_id
        self._enlace = enlace
        self._icono = icono
        self._orden = orden

    # -------------------- GETTERS --------------------

    def obtener_perfil_id(self):
        return self._perfil_id

    def obtener_enlace(self):
        return self._enlace

    def obtener_icono(self):
        return self._icono

    def obtener_orden(self):
        return self._orden

    # -------------------- SETTERS --------------------

    def establecer_perfil_id(self, nuevo_perfil_id):
        self._perfil_id = nuevo_perfil_id

    def establecer_enlace(self, nuevo_enlace):
        self._enlace = nuevo_enlace

    def establecer_icono(self, nuevo_icono):
        self._icono = nuevo_icono

    def establecer_orden(self, nuevo_orden):
        self._orden = nuevo_orden

    # -------------------- MOSTRAR --------------------

    def mostrar(self):
        """
        Devuelve un resumen corto de la red social.
        """

        # POO - POLIMORFISMO:
        # RedSocial redefine mostrar() para mostrar el nombre y el enlace.
        return self._titulo + ": " + self._enlace

    # -------------------- GUARDAR --------------------

    def guardar(self, base_de_datos):
        """
        Inserta una red social nueva en MySQL y devuelve su id.
        """

        consulta = """
            INSERT INTO redes_sociales
                (perfil_id, nombre, enlace, icono, orden)
            VALUES
                (%s, %s, %s, %s, %s)
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._enlace,
            self._icono,
            self._orden,
        )

        nuevo_id = base_de_datos.ejecutar_insercion(consulta, parametros)
        self.establecer_id(nuevo_id)

        return nuevo_id

    # -------------------- ACTUALIZAR --------------------

    def actualizar(self, base_de_datos):
        """
        Actualiza una red social existente.
        Devuelve True si se modifico alguna fila.
        """

        if self._id == 0:
            return False

        consulta = """
            UPDATE redes_sociales
            SET perfil_id = %s,
                nombre = %s,
                enlace = %s,
                icono = %s,
                orden = %s
            WHERE id = %s
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._enlace,
            self._icono,
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
        Elimina la red social actual usando su id.
        Devuelve True si se borro alguna fila.
        """

        if self._id == 0:
            return False

        consulta = "DELETE FROM redes_sociales WHERE id = %s"
        parametros = (self._id,)

        filas_borradas = base_de_datos.ejecutar_eliminacion(consulta, parametros)

        return filas_borradas > 0
