# Modelo relacional del portfolio

Este documento explica la base de datos antes de escribir el codigo de Flask.
La idea es poder defender que guarda cada tabla, cual es su clave primaria y
como se conectan las tablas entre si.

## 1. Diagrama general

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

Se lee asi:

- Un usuario tiene un solo perfil.
- Un perfil tiene muchas experiencias, estudios, skills, idiomas,
  proyectos y redes sociales.
- Cada elemento pertenece a un unico perfil mediante la columna `perfil_id`.

## 2. Claves

### Claves primarias (PK)

| Tabla | Clave primaria | Para que sirve |
|---|---|---|
| `usuarios` | `id` | Identificar cada usuario. |
| `perfil` | `id` | Identificar el perfil. |
| `experiencias` | `id` | Identificar cada trabajo. |
| `educacion` | `id` | Identificar cada estudio. |
| `skills` | `id` | Identificar cada habilidad. |
| `idiomas` | `id` | Identificar cada idioma. |
| `proyectos` | `id` | Identificar cada proyecto. |
| `redes_sociales` | `id` | Identificar cada red social. |

Todas las claves primarias son numeros enteros autoincrementales. MySQL genera
el numero solo cuando se inserta una fila nueva.

### Claves foraneas (FK)

| Tabla hija | Columna | Tabla padre | Relacion |
|---|---|---|---|
| `perfil` | `usuario_id` | `usuarios(id)` | Uno a uno |
| `experiencias` | `perfil_id` | `perfil(id)` | Uno a muchos |
| `educacion` | `perfil_id` | `perfil(id)` | Uno a muchos |
| `skills` | `perfil_id` | `perfil(id)` | Uno a muchos |
| `idiomas` | `perfil_id` | `perfil(id)` | Uno a muchos |
| `proyectos` | `perfil_id` | `perfil(id)` | Uno a muchos |
| `redes_sociales` | `perfil_id` | `perfil(id)` | Uno a muchos |

`perfil.usuario_id` tiene una restriccion `UNIQUE`. Gracias a eso no se pueden
crear dos perfiles para el mismo usuario: la relacion es uno a uno.

Las demas tablas usan `ON DELETE CASCADE`. Si se borrara un perfil, MySQL
borraria automaticamente sus experiencias, estudios, skills, idiomas,
proyectos y redes sociales. De esta forma no quedan filas huerfanas.

## 3. Descripcion de cada tabla

### `usuarios`

Guarda las personas que pueden iniciar sesion.

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | INT UNSIGNED | PK, autoincremental. |
| `nombre_usuario` | VARCHAR(50) | Nombre para el login. Es unico. |
| `clave_hash` | VARCHAR(255) | Hash de la contrasena, nunca la contrasena real. |
| `creado_en` | TIMESTAMP | Fecha de creacion. |

El hash se genera con `werkzeug.security.generate_password_hash()` y se
comprueba con `check_password_hash()`.

### `perfil`

Guarda los datos personales que aparecen en el encabezado y en "Acerca de".

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | INT UNSIGNED | PK. |
| `usuario_id` | INT UNSIGNED | FK a `usuarios.id`, unico. |
| `nombre_completo` | VARCHAR(100) | Nombre visible. |
| `titulo_profesional` | VARCHAR(150) | Ejemplo: Desarrollador Full Stack Jr. |
| `resumen` | TEXT | Texto de presentacion. |
| `texto_banner` | VARCHAR(255) | Frase corta del banner. |
| `foto_perfil` | VARCHAR(255) | Ruta de la foto dentro de `static/`. |
| `imagen_banner` | VARCHAR(255) | Ruta de la imagen del banner. |
| `archivo_cv` | VARCHAR(255) | Ruta del PDF del CV. |
| `correo` | VARCHAR(120) | Correo de contacto. |
| `ubicacion` | VARCHAR(120) | Ciudad o pais. |
| `mapa_url` | VARCHAR(500) | URL que se carga dentro del iframe del mapa. |
| `actualizado_en` | TIMESTAMP | Se actualiza solo al modificar la fila. |

Las rutas de imagenes son relativas a la carpeta `static/`. Por ejemplo,
`img/perfil-ejemplo.svg` se convierte en `/static/img/perfil-ejemplo.svg` con
`url_for("static", filename=...)` dentro de Jinja2.

### `experiencias`

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | INT UNSIGNED | PK. |
| `perfil_id` | INT UNSIGNED | FK a `perfil.id`. |
| `puesto` | VARCHAR(120) | Cargo ocupado. |
| `empresa` | VARCHAR(120) | Nombre de la empresa. |
| `periodo` | VARCHAR(80) | Ejemplo: 2025 - Actualidad. |
| `descripcion` | TEXT | Tareas realizadas. |
| `logo` | VARCHAR(255) | Ruta del logo de la empresa. |
| `orden` | INT | Posicion dentro de la seccion. |

Se usa un texto para el periodo porque es mas simple que manejar dos fechas y
permite escribir "Actualidad" sin agregar una columna extra.

### `educacion`

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | INT UNSIGNED | PK. |
| `perfil_id` | INT UNSIGNED | FK a `perfil.id`. |
| `titulo` | VARCHAR(150) | Carrera, curso o titulo. |
| `institucion` | VARCHAR(150) | Lugar donde se estudio. |
| `periodo` | VARCHAR(80) | Anios o periodo. |
| `descripcion` | TEXT | Detalle del estudio. |
| `logo` | VARCHAR(255) | Ruta del logo del instituto. |
| `orden` | INT | Posicion dentro de la seccion. |

### `skills`

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | INT UNSIGNED | PK. |
| `perfil_id` | INT UNSIGNED | FK a `perfil.id`. |
| `nombre` | VARCHAR(80) | Nombre de la habilidad. |
| `porcentaje` | TINYINT UNSIGNED | Valor del 0 al 100. |
| `categoria` | ENUM('Hard', 'Soft') | Permite separar los dos grupos. |
| `orden` | INT | Posicion dentro del grupo. |

El circulo de porcentaje se va a dibujar con CSS simple a partir del valor de
`porcentaje`. No se necesita ninguna libreria de graficos.

### `idiomas`

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | INT UNSIGNED | PK. |
| `perfil_id` | INT UNSIGNED | FK a `perfil.id`. |
| `nombre` | VARCHAR(80) | Ejemplo: Ingles. |
| `nivel` | VARCHAR(60) | Ejemplo: Intermedio. |
| `porcentaje` | TINYINT UNSIGNED | Valor del 0 al 100. |
| `orden` | INT | Posicion dentro de la seccion. |

Se decidio crear una tabla aparte porque la consigna pide un bloque de idiomas
adicional al de skills.

### `proyectos`

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | INT UNSIGNED | PK. |
| `perfil_id` | INT UNSIGNED | FK a `perfil.id`. |
| `nombre` | VARCHAR(150) | Nombre del proyecto. |
| `fecha` | DATE | Fecha de realizacion. |
| `descripcion` | TEXT | Que hace el proyecto. |
| `enlace` | VARCHAR(500) | Link a GitHub o a una demo. |
| `imagen` | VARCHAR(255) | Ruta de la captura del proyecto. |
| `orden` | INT | Posicion dentro de la seccion. |

### `redes_sociales`

| Columna | Tipo | Detalle |
|---|---|---|
| `id` | INT UNSIGNED | PK. |
| `perfil_id` | INT UNSIGNED | FK a `perfil.id`. |
| `nombre` | VARCHAR(80) | Ejemplo: GitHub. |
| `enlace` | VARCHAR(500) | URL del perfil. |
| `icono` | VARCHAR(100) | Clase de FontAwesome, por ejemplo `fa-brands fa-github`. |
| `orden` | INT | Orden de aparicion en el encabezado. |

## 4. Decisiones simples para poder explicar el modelo

- Los nombres de tablas y columnas estan en espanol.
- Cada tabla tiene una clave primaria llamada `id`.
- Las relaciones se resuelven con `perfil_id` y `usuario_id`.
- Los datos que se repiten en una lista (trabajos, estudios, proyectos) van en
  tablas separadas. Asi se pueden agregar, editar y borrar sin tocar el resto.
- Las imagenes no se guardan como archivos binarios en MySQL. Se guarda
  solamente la ruta del archivo y el archivo vive en `static/`.
- La contrasena se guarda como hash, no como texto plano.
- El campo `orden` queda preparado para el Drag and Drop opcional de la ultima
  etapa.

## 5. Usuario de ejemplo

El script `base_datos.sql` crea este usuario:

- Usuario: `admin`
- Contrasena: `admin123`
- Hash almacenado: el valor de la columna `clave_hash` del primer registro de
  `usuarios`.

Es importante cambiar la contrasena antes de publicar el proyecto.
