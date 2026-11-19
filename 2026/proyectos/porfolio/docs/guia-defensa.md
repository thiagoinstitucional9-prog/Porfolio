# Guía para defender el portfolio

Esta guía está pensada para explicar el proyecto con palabras simples durante
una defensa oral. La idea no es memorizar todo, sino entender qué hace cada
parte y por qué está separada de las demás.

## 1. Qué hace el proyecto

Es un portfolio personal de una sola página. La persona que visita el sitio
puede ver:

- Presentación y datos de contacto.
- Experiencias laborales.
- Educación.
- Hard skills y soft skills.
- Idiomas.
- Proyectos.
- Ubicación en un mapa.
- Un botón para descargar el CV.

La persona dueña del portfolio puede iniciar sesión y entrar en un modo de
edición. Desde ahí puede agregar, editar y eliminar contenido sin tocar la base
de datos a mano.

## 2. Tecnologías y por qué se usaron

- **Flask**: es un framework pequeño de Python. Permite crear rutas y renderizar
  plantillas sin esconder lo que pasa.
- **Jinja2**: permite escribir HTML con variables y bloques. Por ejemplo,
  recorre la lista de experiencias y crea una tarjeta por cada una.
- **MySQL**: guarda los datos en tablas relacionadas.
- **mysql-connector-python**: conecta Python con MySQL. Se usa SQL escrito a
  mano para entender qué consulta se ejecuta.
- **Flask-WTF**: aporta el formulario de login y la protección CSRF.
- **werkzeug.security**: genera y compara hashes de contraseñas.
- **Bootstrap**: ayuda con la estructura, los botones y los modales.
- **CSS propio**: define la identidad visual, la paleta, las animaciones y el
  diseño responsive.
- **JavaScript básico**: completa los modales de edición y pide confirmación
  antes de eliminar.

## 3. Recorrido de una petición

### Cuando alguien entra a la página principal

1. El navegador pide `GET /`.
2. Flask busca la función `mostrar_portfolio()` en `rutas/portfolio.py`.
3. Esa función crea un objeto `BaseDeDatos` y abre la conexión con MySQL.
4. Llama a las funciones de `modelos/consultas_portfolio.py` para traer el
   perfil, las experiencias, la educación, las skills, los idiomas, los
   proyectos y las redes sociales.
5. Cierra la conexión en el bloque `finally`.
6. Renderiza `templates/index.html` con todos esos datos.
7. Jinja2 recorre las listas y arma las tarjetas.

### Cuando alguien inicia sesión

1. El formulario del modal hace `POST /login`.
2. `CSRFProtect` revisa que el token sea válido.
3. `rutas/autenticacion.py` valida el formulario con Flask-WTF.
4. Busca el usuario en MySQL con una consulta parametrizada.
5. Compara la contraseña escrita con el hash guardado usando
   `check_password_hash()`.
6. Si coincide, guarda `usuario_id` y `usuario_nombre` en la sesión.
7. Redirige a la página principal. El encabezado ahora muestra el nombre y el
   botón de salir.

### Cuando se agrega una experiencia

1. El botón **Agregar** abre el modal y el JavaScript le indica al formulario a
   qué ruta debe enviarse.
2. El formulario hace `POST /experiencias/agregar`.
3. La ruta revisa que haya una sesión iniciada.
4. Lee los datos del formulario.
5. Crea un objeto `Experiencia` con esos datos.
6. Llama a `guardar()` y la clase ejecuta el `INSERT` en MySQL.
7. Muestra un mensaje de éxito y vuelve a la sección de experiencia.

Las demás secciones siguen el mismo camino: agregar, editar y eliminar.

## 4. Programación orientada a objetos

### Encapsulamiento

Los atributos privados empiezan con un guion bajo. Por ejemplo:

```python
self._titulo
self._porcentaje
self._categoria
```

Eso indica que no se deben modificar directamente desde afuera. Para leerlos o
cambiarlos se usan getters y setters:

```python
def obtener_titulo(self):
    return self._titulo

def establecer_porcentaje(self, nuevo_porcentaje):
    if nuevo_porcentaje < 0:
        self._porcentaje = 0
    elif nuevo_porcentaje > 100:
        self._porcentaje = 100
    else:
        self._porcentaje = nuevo_porcentaje
```

El setter de porcentaje es un buen ejemplo: no acepta cualquier valor, lo
mantiene entre 0 y 100.

También se aplica encapsulamiento en `BaseDeDatos`: la conexión y el cursor son
privados (`_conexion`, `_cursor`) y se usan mediante métodos como
`obtener_uno()`, `ejecutar_insercion()` o `cerrar()`.

### Herencia

`ElementoPortfolio` es la clase base. Guarda lo que comparten todos los
elementos:

- `id`
- `titulo`
- `descripcion`

Las clases hijas son:

- `Experiencia`
- `Educacion`
- `Proyecto`
- `Skill`
- `Idioma`
- `RedSocial`

Todas heredan de `ElementoPortfolio`. Por eso no repiten el id ni el título.
Por ejemplo:

```python
class Experiencia(ElementoPortfolio):
    def __init__(self, id=0, perfil_id=1, puesto="", ...):
        super().__init__(id, puesto, descripcion)
```

`super()` llama al constructor de la clase base. Ahí se guardan el id, el
título (en este caso, el puesto) y la descripción.

### Polimorfismo

Polimorfismo significa que distintas clases pueden tener un método con el mismo
nombre, pero cada una lo resuelve a su manera.

Todas las clases hijas tienen `mostrar()`, pero no devuelven lo mismo:

- `Experiencia` muestra puesto y empresa.
- `Educacion` muestra título e institución.
- `Proyecto` muestra nombre y enlace.
- `Skill` muestra nombre, porcentaje y categoría.
- `Idioma` muestra nombre, nivel y porcentaje.
- `RedSocial` muestra nombre y enlace.

El código que llama a `mostrar()` no necesita saber de qué clase es el objeto.

### Abstracción

`ElementoPortfolio` define qué debe tener un elemento del portfolio, pero no
resuelve todos los detalles. Sus métodos `mostrar()`, `guardar()`, `actualizar()`
y `eliminar()` lanzan `NotImplementedError` para indicar que las clases hijas
deben completarlos.

No se usó `ABC` ni `@abstractmethod` para que el código sea más simple de leer,
pero la idea es la misma: la clase base marca el contrato común.

## 5. Base de datos

El modelo está explicado en `docs/modelo-relacional.md`. Resumen:

```text
usuarios (1) ---- (1) perfil
                       |
                       |---- (N) experiencias
                       |---- (N) educacion
                       |---- (N) skills
                       |---- (N) idiomas
                       |---- (N) proyectos
                       |---- (N) redes_sociales
```

- `usuarios` guarda el nombre de usuario y el hash de la contraseña.
- `perfil` guarda los datos personales. Tiene `usuario_id` con `UNIQUE`, por eso
  la relación es uno a uno.
- Las demás tablas tienen `perfil_id`, que es una clave foránea.
- `ON DELETE CASCADE` borra los elementos hijos si se borra el perfil, para no
  dejar datos huérfanos.

Las claves primarias son `id`, enteros autoincrementales. Las claves foráneas
son `usuario_id` y `perfil_id`.

## 6. Seguridad

### Contraseñas

No se guarda la contraseña. Se guarda un hash generado con
`generate_password_hash()`. Para comprobarla se usa `check_password_hash()`.

El hash de ejemplo corresponde a la contraseña `admin123`, pero antes de
publicar el sitio se debe cambiar con:

```bash
python cambiar_clave.py
```

### Sesión

Cuando el login es correcto, Flask guarda en una cookie firmada:

- `usuario_id`
- `usuario_nombre`

La cookie no se puede leer desde JavaScript porque está configurada como
`HttpOnly`. La contraseña nunca se guarda en la sesión.

### CSRF

CSRF significa "Cross-Site Request Forgery". Es un ataque donde otra página
intenta enviar un formulario en nombre del usuario.

`CSRFProtect` agrega un token secreto a cada formulario POST. Si el token falta o
no coincide, Flask rechaza la petición. Por eso todos los formularios incluyen:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

El formulario de login usa `formulario_login.hidden_tag()`, que agrega el mismo
token automáticamente.

### Rutas protegidas

Todas las rutas de `rutas/edicion.py` empiezan con:

```python
respuesta = revisar_sesion_iniciada()
if respuesta is not None:
    return respuesta
```

Si no hay sesión, la función devuelve una redirección a la página principal con
el modal de login abierto.

### SQL parametrizado

Las consultas usan `%s` y una tupla de parámetros:

```python
consulta = "SELECT * FROM experiencias WHERE perfil_id = %s"
parametros = (perfil_id,)
```

Así los datos no se pegan directamente dentro del SQL y se reduce el riesgo de
inyección SQL.

### Variables sensibles

Los datos de conexión y la `SECRET_KEY` viven en `.env`. El archivo `.env` está
ignorado por Git. El repositorio incluye solamente `.env.example`.

## 7. Diseño responsive y animaciones

El CSS usa variables para la paleta:

```css
:root {
    --color-primario: #0f766e;
    --color-primario-claro: #14b8a6;
    --color-acento: #f97316;
}
```

Los breakpoints principales son:

- Mobile: menos de 768 px.
- Tablet: entre 768 px y 991 px.
- Escritorio: 992 px o más.

Las skills se dibujan con `conic-gradient` y la variable `--porcentaje`. Las
barras de idiomas usan `transform: scaleX()` y una animación de CSS.

La animación está marcada en el CSS con el comentario `ANIMACIÓN:`. Además, si
el sistema operativo pide reducir el movimiento, las animaciones se apagan con
`prefers-reduced-motion`.

## 8. Archivos y responsabilidades

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Crear Flask, configurar CSRF, sesión y registrar rutas. |
| `configuracion.py` | Leer `.env` y entregar los datos de conexión. |
| `modelos/base_de_datos.py` | Abrir, usar y cerrar la conexión con MySQL. |
| `modelos/elemento_portfolio.py` | Clase base de los elementos. |
| `modelos/experiencia.py` | Datos y SQL de una experiencia. |
| `modelos/educacion.py` | Datos y SQL de un estudio. |
| `modelos/proyecto.py` | Datos y SQL de un proyecto. |
| `modelos/skill.py` | Datos y SQL de una habilidad. |
| `modelos/idioma.py` | Datos y SQL de un idioma. |
| `modelos/red_social.py` | Datos y SQL de una red social. |
| `modelos/consultas_portfolio.py` | SELECT de la página principal. |
| `modelos/consultas_usuario.py` | SELECT del usuario del login. |
| `modelos/consultas_edicion.py` | UPDATE del perfil. |
| `rutas/portfolio.py` | Atender `GET /`. |
| `rutas/autenticacion.py` | Atender login y logout. |
| `rutas/edicion.py` | Agregar, editar y eliminar contenido. |
| `formularios/formulario_login.py` | Formulario de login y validaciones. |
| `utilidades/sesion.py` | Guardar, borrar y revisar la sesión. |
| `templates/base.html` | Estructura HTML y recursos compartidos. |
| `templates/index.html` | Página principal y secciones. |
| `templates/modal_login.html` | Modal de login. |
| `templates/modal_edicion.html` | Modales de edición. |
| `static/css/estilos.css` | Diseño, responsive y animaciones. |
| `static/js/portfolio.js` | Modales y confirmaciones. |
| `base_datos.sql` | Crear tablas y cargar datos de ejemplo. |

## 9. Preguntas posibles durante la defensa

### ¿Por qué separaste los modelos de las rutas?

Para que cada archivo tenga una responsabilidad. Las rutas deciden qué hacer y
los modelos saben cómo hablar con MySQL. Si cambia una consulta, no hay que
tocar la ruta.

### ¿Por qué usaste SQL a mano y no SQLAlchemy?

Porque el objetivo era aprender y poder mostrar las consultas. SQLAlchemy
esconde parte del SQL y agrega conceptos que no eran necesarios para este
proyecto.

### ¿Dónde se guarda la contraseña?

En la tabla `usuarios`, en la columna `clave_hash`. Nunca se guarda la
contraseña real.

### ¿Qué pasa si alguien intenta entrar a una ruta de edición sin sesión?

La función `revisar_sesion_iniciada()` devuelve una redirección a la página
principal con el modal de login abierto.

### ¿Qué pasa si alguien borra un perfil?

Las tablas hijas tienen `ON DELETE CASCADE`, así que MySQL borra también sus
experiencias, estudios, skills, idiomas, proyectos y redes sociales.

### ¿Cómo se ordenan las tarjetas?

Cada tabla tiene una columna `orden`. Las consultas usan `ORDER BY orden, id`.
El modo edición permite cambiar ese número desde el formulario.

### ¿Por qué el botón de eliminar es un formulario y no un enlace?

Porque eliminar cambia datos. Un enlace haría un GET y no llevaría token CSRF.
Un formulario POST con token es más seguro y respeta la semántica HTTP.

### ¿Qué demuestra que hay polimorfismo?

Que `Experiencia`, `Educacion`, `Proyecto`, `Skill`, `Idioma` y `RedSocial`
tengan `mostrar()` con implementaciones distintas.

### ¿Qué demuestra que hay abstracción?

Que `ElementoPortfolio` defina métodos comunes que las clases hijas deben
completar. En este proyecto se simula con `NotImplementedError` para no usar
`ABC`.

### ¿Cómo funciona el drag and drop?

Cuando hay sesión iniciada, las tarjetas tienen `draggable="true"`. JavaScript
guarda en qué posición quedó cada una y manda los ids por un formulario POST a
la ruta `/orden/guardar`. Esa ruta revisa la sesión y el token CSRF, y después
escribe los números 1, 2, 3... en la columna `orden` de la tabla correspondiente.
El campo "Orden" de los formularios sigue sirviendo para quien no quiere
arrastrar.

### ¿Qué se podría mejorar?

- Subir imágenes y CV desde el navegador.
- Agregar tests automáticos.
- Pasar a un servidor WSGI de producción en un plan pago.
