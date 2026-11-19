# Portfolio personal con Flask y MySQL

Proyecto de portfolio personal de una sola página. Muestra los datos personales,
experiencias, educación, habilidades, idiomas, proyectos y ubicación. Además
incluye un modo de edición protegido con login para que la persona dueña del
portfolio pueda agregar, editar y eliminar contenido sin tocar el código.

## Tecnologías

- Python 3
- Flask
- Jinja2
- MySQL / MariaDB
- `mysql-connector-python` con SQL escrito a mano
- Flask-WTF para el formulario de login y la protección CSRF
- `werkzeug.security` para guardar contraseñas como hash
- Bootstrap
- CSS propio con variables y diseño responsive
- JavaScript básico para los modales y las confirmaciones
- FontAwesome y Google Fonts por CDN

## Funcionalidades

- Página principal responsive para celular, tablet y escritorio.
- Encabezado con logo, redes sociales y botón de login.
- Banner, presentación, datos de contacto y descarga de CV.
- Experiencias, educación, hard skills, soft skills, idiomas y proyectos.
- Skills dibujadas como círculos con CSS.
- Barras animadas para los idiomas.
- Mapa embebido con Google Maps.
- Login con sesión, contraseña con hash y token CSRF.
- Modo edición con formularios modales.
- Agregar, editar y eliminar experiencias, educación, skills, idiomas,
  proyectos y redes sociales.
- Edición del perfil y de las rutas de imágenes y CV.
- Arrastrar las tarjetas para cambiar el orden (drag and drop básico).
- Mensajes de éxito, aviso y error.
- Página de error cuando no se puede conectar con la base de datos.

## Estructura del proyecto

```text
portfolio/
├── app.py                         Crea Flask y registra las rutas
├── configuracion.py               Lee el archivo .env
├── cambiar_clave.py               Cambia la contraseña desde la consola
├── base_datos.sql                 Crea la base y carga datos de ejemplo
├── requirements.txt               Dependencias del proyecto
├── .env.example                   Ejemplo de variables de entorno
│
├── modelos/
│   ├── base_de_datos.py           Conexión y consultas SQL
│   ├── elemento_portfolio.py      Clase base de los elementos
│   ├── experiencia.py             Clase Experiencia
│   ├── educacion.py               Clase Educacion
│   ├── proyecto.py                Clase Proyecto
│   ├── skill.py                   Clase Skill
│   ├── idioma.py                  Clase Idioma
│   ├── red_social.py              Clase RedSocial
│   ├── consultas_portfolio.py     SELECT de la página principal
│   ├── consultas_usuario.py       SELECT del usuario que inicia sesión
│   └── consultas_edicion.py       UPDATE del perfil
│
├── rutas/
│   ├── portfolio.py               Página principal
│   ├── autenticacion.py           Login y logout
│   └── edicion.py                 Rutas protegidas de agregar/editar/eliminar
│
├── formularios/
│   └── formulario_login.py        Formulario de login con Flask-WTF
│
├── utilidades/
│   └── sesion.py                  Funciones de sesión y protección de rutas
│
├── templates/
│   ├── base.html                  Estructura HTML compartida
│   ├── index.html                 Página principal
│   ├── modal_login.html           Modal de login
│   ├── modal_edicion.html         Modales del modo edición
│   └── error_conexion.html        Página de error de MySQL
│
├── static/
│   ├── css/estilos.css            Todos los estilos
│   ├── js/portfolio.js            Modales y confirmaciones
│   ├── img/                       Logo, favicon e imágenes de ejemplo
│   └── cv/cv-ejemplo.pdf          CV descargable
│
└── docs/
    ├── modelo-relacional.md       Explicación de la base de datos
    ├── guia-defensa.md            Guía para explicar el proyecto oralmente
    └── cv-ejemplo.html            Fuente HTML usada para generar el PDF
```

## Cómo ejecutar el proyecto

### 1. Tener MySQL encendido

Si se usa XAMPP, abrir el panel de control y encender **MySQL**.
También se puede usar cualquier servidor MySQL o MariaDB local.

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar el archivo `.env`

Copiar `.env.example` como `.env` y completar los datos:

```text
FLASK_APP=app.py
FLASK_DEBUG=1
SECRET_KEY=una-clave-larga-y-dificil-de-adivinar

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=portfolio_db
```

`SECRET_KEY` se usa para firmar la sesión y los tokens CSRF. No se debe subir
el archivo `.env` al repositorio.

### 4. Crear y cargar la base de datos

Desde la carpeta del proyecto:

```bash
mysql -u root -p --default-character-set=utf8mb4 < base_datos.sql
```

Si el usuario `root` no tiene contraseña, se puede omitir `-p`.

> Importante: el script elimina y vuelve a crear las tablas del portfolio.
> No ejecutarlo si ya hay datos que se quieren conservar.

### 5. Iniciar el sitio

```bash
python app.py
```

Luego abrir:

```text
http://127.0.0.1:5000
```

## Usuario de ejemplo

```text
Usuario: admin
Contraseña: admin123
```

La contraseña se guarda como hash en la tabla `usuarios`, nunca en texto plano.

Para cambiarla antes de publicar el sitio:

```bash
python cambiar_clave.py
```

## Cómo usar el modo edición

1. Entrar con el botón **Login**.
2. Al iniciar sesión aparece la etiqueta **Modo edición**.
3. Usar el botón **Editar perfil** para cambiar los datos personales.
4. En cada sección aparece el botón **Agregar**.
5. En cada tarjeta aparecen los botones **Editar** y **Eliminar**.
6. Arrastrá una tarjeta con el mouse para moverla de lugar. El cambio se guarda
   solo cuando soltás la tarjeta.
7. El botón **Salir** cierra la sesión.

El campo **Orden** de cada formulario permite lo mismo con un número, por si no
querés arrastrar. Las dos formas escriben en la columna `orden` de MySQL.

## Seguridad aplicada

- Contraseñas con `generate_password_hash()` y `check_password_hash()`.
- Sesión de Flask con cookie `HttpOnly` y `SameSite=Lax`.
- Todos los formularios POST tienen token CSRF.
- Las rutas de edición revisan que exista una sesión iniciada.
- Las consultas SQL usan parámetros `%s`, no concatenación de texto.
- El login muestra un mensaje genérico si el usuario o la contraseña fallan.
- Los datos sensibles viven en `.env`.
- Las conexiones a MySQL se cierran en un bloque `finally`.

## Programación orientada a objetos

- `ElementoPortfolio` es la clase base.
- `Experiencia`, `Educacion`, `Proyecto`, `Skill`, `Idioma` y `RedSocial`
  heredan de ella.
- Los atributos privados usan guion bajo y se leen o modifican con getters y
  setters.
- Cada clase hija redefine `mostrar()`, lo que demuestra polimorfismo.
- La clase base define el comportamiento común y deja métodos para que las
  clases hijas los completen, lo que representa la abstracción.

La explicación ampliada está en `docs/guia-defensa.md`.

## CV descargable

El botón **Descargar CV** apunta a:

```text
static/cv/cv-ejemplo.pdf
```

La ruta se puede cambiar desde el modal **Editar perfil**.

El archivo fuente del CV de ejemplo es `docs/cv-ejemplo.html`. Si se modifica,
se puede generar de nuevo el PDF con Chrome:

```bash
chrome --headless=new --disable-gpu --no-pdf-header-footer ^
  --print-to-pdf=static/cv/cv-ejemplo.pdf ^
  file:///ruta/al/proyecto/docs/cv-ejemplo.html
```

## Problemas frecuentes

### No se pudo conectar con MySQL

- Revisar que MySQL esté encendido.
- Revisar `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` y `DB_NAME` en `.env`.
- Comprobar que la base `portfolio_db` exista.

### La página dice que no hay perfil

Ejecutar `base_datos.sql` para cargar el usuario, el perfil y los datos de
ejemplo.

### El login no funciona

- Comprobar que el usuario `admin` exista en la tabla `usuarios`.
- Si se cambió la contraseña, usar la nueva.
- Revisar que `SECRET_KEY` esté definida en `.env`.

### El formulario dice que venció o no es válido

El token CSRF puede haber vencido. Recargar la página y volver a intentar.

## Publicación (deploy)

La idea es dejar la base en **Clever Cloud** y la aplicación en un hosting
gratuito como **Render**. No hace falta agregar librerías nuevas: la app usa
Flask y `mysql-connector-python`, que ya están en `requirements.txt`.

> Los planes gratuitos pueden cambiar. Antes de publicar, conviene revisar los
> precios y límites actuales de cada servicio.

### 1. Subir el código a GitHub

El repositorio NO debe incluir `.env` (ya está en `.gitignore`). Si por error se
subió una clave, hay que cambiarla antes de seguir.

```bash
git add .
git commit -m "Portfolio listo para publicar"
git push
```

### 2. Crear la base MySQL en Clever Cloud

1. Entrar a Clever Cloud y crear un **add-on de MySQL**.
2. Copiar del panel estos datos: **host**, **puerto**, **usuario**,
   **contraseña** y **nombre de la base**.
3. Cargar las tablas. El archivo `base_datos.sql` dice `CREATE DATABASE` y
   `USE portfolio_db`, pero Clever Cloud ya creó la base con otro nombre.
   Por eso:
   - Hacer una copia llamada `base_datos_clever.sql`.
   - Comentar las líneas del `CREATE DATABASE` y del `USE` (aprox. 32 a 36).
   - Ejecutar desde la computadora:

```bash
mysql -h HOST_DE_CLEVER -P PUERTO -u USUARIO -p NOMBRE_DE_LA_BASE < base_datos_clever.sql
```

También se puede pegar el SQL en MySQL Workbench conectado a Clever Cloud.
Ojo: el script borra las tablas si ya existen.

### 3. Crear el servicio web en Render

1. Crear cuenta en Render y elegir **New > Web Service**.
2. Conectar el repositorio de GitHub.
3. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
4. En la pestaña **Environment** agregar estas variables:

```text
SECRET_KEY=una-clave-larga-y-dificil-de-adivinar
FLASK_DEBUG=0
DB_HOST=host_de_clever_cloud
DB_PORT=puerto_de_clever_cloud
DB_USER=usuario_de_clever_cloud
DB_PASSWORD=clave_de_clever_cloud
DB_NAME=nombre_de_la_base_en_clever
```

No hace falta subir `.env`: `configuracion.py` también lee las variables que
el hosting pone en el entorno. Así los datos sensibles siguen fuera del código.

### 4. Revisar que ande

1. Abrir la URL que da Render (por ejemplo `https://tu-app.onrender.com`).
2. Probar el botón **Login** con `admin` / `admin123`.
3. Cambiar la contraseña con:

```bash
python cambiar_clave.py
```

(para eso hay que conectarse a la base de Clever Cloud, por ejemplo desde
MySQL Workbench o desde una consola con `mysql`).

4. Probar agregar, editar, eliminar y arrastrar una tarjeta.

**Dato importante:** el plan gratuito de Render duerme el sitio después de un
rato sin visitas. La primera visita puede tardar unos segundos en levantar.

## Próximas mejoras posibles

- Subida de imágenes y CV desde el navegador.
- Recuperación de contraseña.
- Tests automáticos.
- Pasar a un servidor WSGI de producción cuando se contrate un plan pago.
