# modelos/experiencia.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Representar una experiencia laboral del portfolio.

from modelos.elemento_portfolio import ElementoPortfolio


class Experiencia(ElementoPortfolio):
    """
    Una experiencia laboral.

    Hereda id, titulo y descripcion de ElementoPortfolio.
    En esta clase, el "titulo" es el puesto de trabajo.
    """

    # POO - HERENCIA:
    # Experiencia hereda de ElementoPortfolio.
    # Por eso ya tiene obtener_id(), obtener_titulo(), etc. sin volver
    # a escribir esos metodos.

    def __init__(
        self,
        id=0,
        perfil_id=1,
        puesto="",
        empresa="",
        periodo="",
        descripcion="",
        logo="",
        orden=0,
    ):
        # Enviamos los datos comunes a la clase base.
        super().__init__(id, puesto, descripcion)

        # POO - ENCAPSULAMIENTO:
        # Estos atributos son propios de Experiencia y tambien son privados.
        self._perfil_id = perfil_id
        self._empresa = empresa
        self._periodo = periodo
        self._logo = logo
        self._orden = orden

    # -------------------- GETTERS --------------------

    def obtener_perfil_id(self):
        return self._perfil_id

    def obtener_empresa(self):
        return self._empresa

    def obtener_periodo(self):
        return self._periodo

    def obtener_logo(self):
        return self._logo

    def obtener_orden(self):
        return self._orden

    # -------------------- SETTERS --------------------

    def establecer_perfil_id(self, nuevo_perfil_id):
        self._perfil_id = nuevo_perfil_id

    def establecer_empresa(self, nueva_empresa):
        self._empresa = nueva_empresa

    def establecer_periodo(self, nuevo_periodo):
        self._periodo = nuevo_periodo

    def establecer_logo(self, nuevo_logo):
        self._logo = nuevo_logo

    def establecer_orden(self, nuevo_orden):
        self._orden = nuevo_orden

    # -------------------- MOSTRAR --------------------

    def mostrar(self):
        """
        Devuelve un resumen corto de la experiencia.
        """

        # POO - POLIMORFISMO:
        # Experiencia tiene su propia version de mostrar().
        # Educacion, Proyecto y Skill tambien tienen la suya.
        return self._titulo + " en " + self._empresa + " (" + self._periodo + ")"

    # -------------------- GUARDAR --------------------

    def guardar(self, base_de_datos):
        """
        Inserta una experiencia nueva en MySQL.
        Devuelve el id generado.
        """

        consulta = """
            INSERT INTO experiencias
                (perfil_id, puesto, empresa, periodo, descripcion, logo, orden)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._empresa,
            self._periodo,
            self._descripcion,
            self._logo,
            self._orden,
        )

        nuevo_id = base_de_datos.ejecutar_insercion(consulta, parametros)

        # Guardamos el id que genero MySQL para poder editar o borrar despues.
        self.establecer_id(nuevo_id)
        return nuevo_id

    # -------------------- ACTUALIZAR --------------------

    def actualizar(self, base_de_datos):
        """
        Actualiza los datos de una experiencia que ya existe.
        Devuelve True si se modifico alguna fila.
        """

        # Si el id es 0, el objeto todavia no esta guardado en MySQL.
        if self._id == 0:
            return False

        consulta = """
            UPDATE experiencias
            SET perfil_id = %s,
                puesto = %s,
                empresa = %s,
                periodo = %s,
                descripcion = %s,
                logo = %s,
                orden = %s
            WHERE id = %s
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._empresa,
            self._periodo,
            self._descripcion,
            self._logo,
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
        Elimina la experiencia actual usando su id.
        Devuelve True si se borro alguna fila.
        """

        if self._id == 0:
            return False

        consulta = "DELETE FROM experiencias WHERE id = %s"
        parametros = (self._id,)

        filas_borradas = base_de_datos.ejecutar_eliminacion(consulta, parametros)

        return filas_borradas > 0
