# modelos/idioma.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Representar un idioma del portfolio.

from modelos.elemento_portfolio import ElementoPortfolio


class Idioma(ElementoPortfolio):
    """
    Un idioma que habla la persona duena del portfolio.

    Hereda id, titulo y descripcion de ElementoPortfolio.
    En esta clase, el "titulo" es el nombre del idioma.
    """

    # POO - HERENCIA:
    # Idioma tambien hereda de ElementoPortfolio, igual que Experiencia,
    # Educacion, Proyecto y Skill. Reutiliza el id y el titulo.

    def __init__(
        self,
        id=0,
        perfil_id=1,
        nombre="",
        nivel="",
        porcentaje=0,
        orden=0,
    ):
        # El nombre se guarda como titulo en la clase base.
        super().__init__(id, nombre, "")

        # POO - ENCAPSULAMIENTO:
        # El nivel, el porcentaje y el orden son datos propios de Idioma.
        self._perfil_id = perfil_id
        self._nivel = nivel
        self._porcentaje = 0
        self._orden = orden

        # Usamos el setter para aprovechar la validacion del porcentaje.
        self.establecer_porcentaje(porcentaje)

    # -------------------- GETTERS --------------------

    def obtener_perfil_id(self):
        return self._perfil_id

    def obtener_nivel(self):
        return self._nivel

    def obtener_porcentaje(self):
        return self._porcentaje

    def obtener_orden(self):
        return self._orden

    # -------------------- SETTERS --------------------

    def establecer_perfil_id(self, nuevo_perfil_id):
        self._perfil_id = nuevo_perfil_id

    def establecer_nivel(self, nuevo_nivel):
        self._nivel = nuevo_nivel

    def establecer_porcentaje(self, nuevo_porcentaje):
        """
        Guarda el porcentaje solamente si esta entre 0 y 100.
        """

        if nuevo_porcentaje < 0:
            self._porcentaje = 0
        elif nuevo_porcentaje > 100:
            self._porcentaje = 100
        else:
            self._porcentaje = nuevo_porcentaje

    def establecer_orden(self, nuevo_orden):
        self._orden = nuevo_orden

    # -------------------- MOSTRAR --------------------

    def mostrar(self):
        """
        Devuelve un resumen corto del idioma.
        """

        # POO - POLIMORFISMO:
        # Idioma redefine mostrar() para incluir el nivel y el porcentaje.
        return (
            self._titulo
            + " - "
            + self._nivel
            + " ("
            + str(self._porcentaje)
            + "%)"
        )

    # -------------------- GUARDAR --------------------

    def guardar(self, base_de_datos):
        """
        Inserta un idioma nuevo en MySQL y devuelve su id.
        """

        consulta = """
            INSERT INTO idiomas
                (perfil_id, nombre, nivel, porcentaje, orden)
            VALUES
                (%s, %s, %s, %s, %s)
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._nivel,
            self._porcentaje,
            self._orden,
        )

        nuevo_id = base_de_datos.ejecutar_insercion(consulta, parametros)
        self.establecer_id(nuevo_id)

        return nuevo_id

    # -------------------- ACTUALIZAR --------------------

    def actualizar(self, base_de_datos):
        """
        Actualiza un idioma existente.
        Devuelve True si se modifico alguna fila.
        """

        if self._id == 0:
            return False

        consulta = """
            UPDATE idiomas
            SET perfil_id = %s,
                nombre = %s,
                nivel = %s,
                porcentaje = %s,
                orden = %s
            WHERE id = %s
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._nivel,
            self._porcentaje,
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
        Elimina el idioma actual usando su id.
        Devuelve True si se borro alguna fila.
        """

        if self._id == 0:
            return False

        consulta = "DELETE FROM idiomas WHERE id = %s"
        parametros = (self._id,)

        filas_borradas = base_de_datos.ejecutar_eliminacion(consulta, parametros)

        return filas_borradas > 0
