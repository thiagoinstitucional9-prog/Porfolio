# modelos/educacion.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Representar un estudio, curso o carrera del portfolio.

from modelos.elemento_portfolio import ElementoPortfolio


class Educacion(ElementoPortfolio):
    """
    Un estudio realizado.

    Hereda id, titulo y descripcion de ElementoPortfolio.
    """

    # POO - HERENCIA:
    # Educacion hereda de ElementoPortfolio.
    # Comparte los datos comunes con Experiencia, Proyecto y Skill,
    # pero cada una tiene sus propios campos.

    def __init__(
        self,
        id=0,
        perfil_id=1,
        titulo="",
        institucion="",
        periodo="",
        descripcion="",
        logo="",
        orden=0,
    ):
        # La clase base recibe el id, el titulo y la descripcion.
        super().__init__(id, titulo, descripcion)

        # POO - ENCAPSULAMIENTO:
        # Los datos propios de Educacion quedan en atributos privados.
        self._perfil_id = perfil_id
        self._institucion = institucion
        self._periodo = periodo
        self._logo = logo
        self._orden = orden

    # -------------------- GETTERS --------------------

    def obtener_perfil_id(self):
        return self._perfil_id

    def obtener_institucion(self):
        return self._institucion

    def obtener_periodo(self):
        return self._periodo

    def obtener_logo(self):
        return self._logo

    def obtener_orden(self):
        return self._orden

    # -------------------- SETTERS --------------------

    def establecer_perfil_id(self, nuevo_perfil_id):
        self._perfil_id = nuevo_perfil_id

    def establecer_institucion(self, nueva_institucion):
        self._institucion = nueva_institucion

    def establecer_periodo(self, nuevo_periodo):
        self._periodo = nuevo_periodo

    def establecer_logo(self, nuevo_logo):
        self._logo = nuevo_logo

    def establecer_orden(self, nuevo_orden):
        self._orden = nuevo_orden

    # -------------------- MOSTRAR --------------------

    def mostrar(self):
        """
        Devuelve un resumen corto del estudio.
        """

        # POO - POLIMORFISMO:
        # Es el mismo nombre de metodo que usa Experiencia, pero aca
        # el resultado se arma con la institucion y el periodo.
        return self._titulo + " - " + self._institucion + " (" + self._periodo + ")"

    # -------------------- GUARDAR --------------------

    def guardar(self, base_de_datos):
        """
        Inserta un estudio nuevo en MySQL y devuelve su id.
        """

        consulta = """
            INSERT INTO educacion
                (perfil_id, titulo, institucion, periodo, descripcion, logo, orden)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._institucion,
            self._periodo,
            self._descripcion,
            self._logo,
            self._orden,
        )

        nuevo_id = base_de_datos.ejecutar_insercion(consulta, parametros)
        self.establecer_id(nuevo_id)

        return nuevo_id

    # -------------------- ACTUALIZAR --------------------

    def actualizar(self, base_de_datos):
        """
        Actualiza un estudio existente.
        Devuelve True si se modifico alguna fila.
        """

        if self._id == 0:
            return False

        consulta = """
            UPDATE educacion
            SET perfil_id = %s,
                titulo = %s,
                institucion = %s,
                periodo = %s,
                descripcion = %s,
                logo = %s,
                orden = %s
            WHERE id = %s
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._institucion,
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
        Elimina el estudio actual usando su id.
        Devuelve True si se borro alguna fila.
        """

        if self._id == 0:
            return False

        consulta = "DELETE FROM educacion WHERE id = %s"
        parametros = (self._id,)

        filas_borradas = base_de_datos.ejecutar_eliminacion(consulta, parametros)

        return filas_borradas > 0
