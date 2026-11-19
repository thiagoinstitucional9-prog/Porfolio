# modelos/elemento_portfolio.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Definir la clase base que comparten todos los elementos del portfolio.
#
# Un "elemento" es algo que se muestra en el sitio y que tiene un id,
# un titulo y una descripcion. Por ejemplo: una experiencia, un estudio,
# un proyecto o una skill.

class ElementoPortfolio:
    """
    Clase base para los elementos del portfolio.

    No se usa directamente para crear objetos. Sirve para que las clases
    hijas hereden los datos y el comportamiento comun.
    """

    # POO - ABSTRACCIÓN:
    # Esta clase define QUE debe tener un elemento del portfolio
    # (id, titulo, descripcion, mostrar, guardar, etc.) sin decir COMO
    # lo hace cada tipo de elemento.
    #
    # Las clases hijas se encargan de completar los metodos.
    # Por eso los metodos de abajo lanzan NotImplementedError.

    # POO - ENCAPSULAMIENTO:
    # Los atributos empiezan con un guion bajo (_).
    # Eso indica que son privados: no se cambian directamente desde afuera.
    # Se leen y se modifican con getters y setters.

    def __init__(self, id=0, titulo="", descripcion=""):
        self._id = id
        self._titulo = titulo
        self._descripcion = descripcion

    # -------------------- GETTERS --------------------

    def obtener_id(self):
        return self._id

    def obtener_titulo(self):
        return self._titulo

    def obtener_descripcion(self):
        return self._descripcion

    # -------------------- SETTERS --------------------

    def establecer_id(self, nuevo_id):
        self._id = nuevo_id

    def establecer_titulo(self, nuevo_titulo):
        self._titulo = nuevo_titulo

    def establecer_descripcion(self, nueva_descripcion):
        self._descripcion = nueva_descripcion

    # -------------------- METODOS QUE COMPLETAN LAS HIJAS --------------------

    def mostrar(self):
        """
        Devuelve un texto corto que representa al elemento.

        Cada clase hija va a escribir su propia version.
        """

        # POO - ABSTRACCIÓN:
        # La clase base solo dice que existe mostrar().
        # No puede saber si una experiencia se muestra distinto de una skill.

        # POO - POLIMORFISMO:
        # El mismo nombre de metodo se va a comportar distinto en cada hija.
        raise NotImplementedError("La clase hija debe implementar mostrar().")

    def guardar(self, base_de_datos):
        """
        Guarda el elemento en la tabla que le corresponde.

        Cada clase hija conoce su propia tabla y sus propios campos.
        """

        # POO - ABSTRACCIÓN:
        # Guardar es una accion comun, pero los datos concretos cambian.
        raise NotImplementedError("La clase hija debe implementar guardar().")

    def actualizar(self, base_de_datos):
        """
        Actualiza en MySQL los datos de un elemento que ya existe.
        """

        raise NotImplementedError("La clase hija debe implementar actualizar().")

    def eliminar(self, base_de_datos):
        """
        Elimina de MySQL el elemento usando su id.
        """

        raise NotImplementedError("La clase hija debe implementar eliminar().")
