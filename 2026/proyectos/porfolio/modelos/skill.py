# modelos/skill.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Representar una habilidad dura o blanda del portfolio.

from modelos.elemento_portfolio import ElementoPortfolio


class Skill(ElementoPortfolio):
    """
    Una habilidad.

    Hereda id, titulo y descripcion de ElementoPortfolio.
    El "titulo" es el nombre de la habilidad.
    """

    # POO - HERENCIA:
    # Skill hereda de ElementoPortfolio, igual que Experiencia,
    # Educacion y Proyecto.

    def __init__(
        self,
        id=0,
        perfil_id=1,
        nombre="",
        porcentaje=0,
        categoria="Hard",
        orden=0,
    ):
        # La descripcion no se usa en la tabla skills, por eso va vacia.
        super().__init__(id, nombre, "")

        # POO - ENCAPSULAMIENTO:
        # El porcentaje y la categoria son datos propios de Skill.
        self._perfil_id = perfil_id
        self._porcentaje = 0
        self._categoria = "Hard"
        self._orden = orden

        # Usamos los setters para aprovechar sus validaciones.
        self.establecer_porcentaje(porcentaje)
        self.establecer_categoria(categoria)

    # -------------------- GETTERS --------------------

    def obtener_perfil_id(self):
        return self._perfil_id

    def obtener_porcentaje(self):
        return self._porcentaje

    def obtener_categoria(self):
        return self._categoria

    def obtener_orden(self):
        return self._orden

    # -------------------- SETTERS --------------------

    def establecer_perfil_id(self, nuevo_perfil_id):
        self._perfil_id = nuevo_perfil_id

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

    def establecer_categoria(self, nueva_categoria):
        """
        Guarda la categoria solamente si es Hard o Soft.
        """

        if nueva_categoria == "Hard" or nueva_categoria == "Soft":
            self._categoria = nueva_categoria
        else:
            # Si llega un valor desconocido, usamos Hard por seguridad.
            self._categoria = "Hard"

    def establecer_orden(self, nuevo_orden):
        self._orden = nuevo_orden

    # -------------------- MOSTRAR --------------------

    def mostrar(self):
        """
        Devuelve un resumen corto de la skill.
        """

        # POO - POLIMORFISMO:
        # Skill redefine mostrar() y usa el porcentaje y la categoria,
        # que no existen en las otras clases hijas.
        return (
            self._titulo
            + ": "
            + str(self._porcentaje)
            + "% ("
            + self._categoria
            + ")"
        )

    # -------------------- GUARDAR --------------------

    def guardar(self, base_de_datos):
        """
        Inserta una skill nueva en MySQL y devuelve su id.
        """

        consulta = """
            INSERT INTO skills
                (perfil_id, nombre, porcentaje, categoria, orden)
            VALUES
                (%s, %s, %s, %s, %s)
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._porcentaje,
            self._categoria,
            self._orden,
        )

        nuevo_id = base_de_datos.ejecutar_insercion(consulta, parametros)
        self.establecer_id(nuevo_id)

        return nuevo_id

    # -------------------- ACTUALIZAR --------------------

    def actualizar(self, base_de_datos):
        """
        Actualiza una skill existente.
        Devuelve True si se modifico alguna fila.
        """

        if self._id == 0:
            return False

        consulta = """
            UPDATE skills
            SET perfil_id = %s,
                nombre = %s,
                porcentaje = %s,
                categoria = %s,
                orden = %s
            WHERE id = %s
        """

        parametros = (
            self._perfil_id,
            self._titulo,
            self._porcentaje,
            self._categoria,
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
        Elimina la skill actual usando su id.
        Devuelve True si se borro alguna fila.
        """

        if self._id == 0:
            return False

        consulta = "DELETE FROM skills WHERE id = %s"
        parametros = (self._id,)

        filas_borradas = base_de_datos.ejecutar_eliminacion(consulta, parametros)

        return filas_borradas > 0
