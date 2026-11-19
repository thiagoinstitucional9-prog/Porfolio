# AGENTS.md — Reglas del proyecto Portfolio Full Stack

Este archivo existe para que, si se cierra la terminal y se abre una sesión nueva,
no se pierdan las reglas ni el estado del proyecto.

Leelo siempre antes de tocar código.

---

## 1. Quién es la persona dueña del proyecto

- Es **principiante**.
- Tiene que **defender el código oralmente**, explicando cada parte.
- Por eso el código debe parecerse al que escribiría un estudiante que recién
  empieza: claro, directo y fácil de leer en voz alta.

---

## 2. Reglas de código (OBLIGATORIAS)

- Usar **lógica básica y simple**.
- NO usar trucos avanzados, decoradores raros, comprehensions complicadas,
  lambdas, async ni patrones de diseño.
  - Excepción permitida: los `@app.route` / `@blueprint.route` de Flask y los
    `@keyframes` de CSS, que son parte normal del stack.
- Nombres de variables y funciones **en español, claros y largos**.
  - Mejor `obtener_experiencias` que `get_exp`.
- **Un archivo = una responsabilidad**.
- Funciones cortas, que hagan una sola cosa.
- Comentar **TODO en español**, como si se le explicara a alguien que recién
  empieza.
- No usar librerías fuera de la lista del stack.
- Usar comentarios especiales:
  - `# POO - ENCAPSULAMIENTO:`
  - `# POO - HERENCIA:`
  - `# POO - POLIMORFISMO:`
  - `# POO - ABSTRACCIÓN:`
  - `ANIMACIÓN:` donde haya animaciones en CSS u otros archivos.

---

## 3. Stack obligatorio

**Back end**
- Python + Flask.
- Jinja2 con herencia: todas las plantillas extienden `templates/base.html`.
- MySQL con `mysql-connector-python`.
- SQL escrito a mano. **NO usar SQLAlchemy**.
- Flask-WTF para formularios y CSRF del login.
- Hash de contraseñas con `werkzeug.security`.

**Front end**
- HTML + CSS propio (`static/css/estilos.css`).
- Bootstrap.
- JavaScript básico (`static/js/portfolio.js`).
- Íconos FontAwesome.
- Fuente de Google Fonts.

**Datos y archivos**
- Datos sensibles solo en `.env` (nunca escribir claves en el código).
- `.env.example` es la plantilla; `.env` está en `.gitignore`.

**POO**
- Los 4 pilares deben estar comentados donde se usan:
  encapsulamiento, herencia, polimorfismo y abstracción.

---

## 4. Cómo trabajar por etapas

- Trabajar **de a una etapa por vez**.
- Al terminar una etapa: **parar**, explicar con palabras simples qué se hizo
  y qué archivos se crearon o cambiaron.
- Después **esperar la confirmación del usuario con la palabra "seguí"**.
- No avanzar a la siguiente etapa sin ese "seguí".

---

## 5. Estructura actual del proyecto

```text
porfolio/
├── AGENTS.md                    Este archivo de reglas
├── app.py                       Crea Flask, CSRF y registra blueprints
├── configuracion.py             Lee .env sin librerías extra
├── cambiar_clave.py             Cambia la clave del usuario por consola
├── base_datos.sql               Crea base, tablas y datos de ejemplo
├── requirements.txt             Flask, Flask-WTF, mysql-connector-python
├── .env / .env.example          Datos sensibles / plantilla
├── .gitignore                   Ignora .env, __pycache__, etc.
│
├── modelos/
│   ├── base_de_datos.py         Conexión y consultas a MySQL
│   ├── elemento_portfolio.py    Clase base (abstracción)
│   ├── experiencia.py
│   ├── educacion.py
│   ├── proyecto.py
│   ├── skill.py
│   ├── idioma.py
│   ├── red_social.py
│   ├── consultas_portfolio.py   SELECT de la página principal
│   ├── consultas_usuario.py     SELECT del login
│   └── consultas_edicion.py     UPDATE del perfil
│
├── rutas/
│   ├── portfolio.py             Página principal (solo lectura)
│   ├── autenticacion.py         Login y logout
│   └── edicion.py               Rutas protegidas de agregar/editar/eliminar
│
├── formularios/
│   └── formulario_login.py      Flask-WTF + CSRF
│
├── utilidades/
│   └── sesion.py                Funciones de sesión
│
├── templates/
│   ├── base.html                Plantilla madre con bloques
│   ├── index.html               Página principal completa
│   ├── modal_login.html         Modal de login
│   ├── modal_edicion.html       Todos los modales de edición
│   ├── error_conexion.html      Página cuando falla MySQL
│   └── modales/                 Carpeta vacía (solo .gitkeep)
│
├── static/
│   ├── css/estilos.css          Estilos, responsive y animaciones
│   ├── js/portfolio.js          Modales y confirmaciones
│   ├── js/arrastrar_orden.js    Drag and drop de tarjetas
│   ├── img/                     Logo, favicon e imágenes de ejemplo
│   └── cv/cv-ejemplo.pdf        CV descargable
│
└── docs/
    ├── modelo-relacional.md     Explicación de la base de datos
    ├── guia-defensa.md          Guía para explicar el proyecto oralmente
    └── cv-ejemplo.html          Fuente usada para generar el PDF
```

---

## 6. Estado real de las etapas (revisado el 17/11/2026)

| Etapa | Estado | Evidencia |
|---|---|---|
| 1. Estructura + requirements + modelo relacional + `base_datos.sql` | **Completa** | 8 tablas con PK/FK, datos de ejemplo y `docs/modelo-relacional.md`. |
| 2. Conexión a la base y clases POO | **Completa** | `BaseDeDatos`, `ElementoPortfolio` y 6 clases hijas con los 4 pilares comentados. |
| 3. Página principal leyendo desde la base | **Completa** | `index.html` + `rutas/portfolio.py`: banner, Acerca de, Experiencia, Educación, Skills en círculos y Proyectos. |
| 4. Diseño y responsive | **Completa** | CSS propio con 3 cortes `(max-width: 767.98px)`, tablet y `(min-width: 992px)`, FontAwesome, Google Fonts, animaciones y favicon. |
| 5. Login con hash y sesión | **Completa** | Flask-WTF, `hidden_tag()`, `check_password_hash`, sesión y botones Login/Salir. |
| 6. Modo edición protegido | **Completa** | 19 rutas en `edicion.py` con `revisar_sesion_iniciada()` y CSRF; edición con modales de Bootstrap. |
| 7. Descarga del CV en PDF | **Completa** | `static/cv/cv-ejemplo.pdf` es un PDF real y el botón usa `perfil.archivo_cv`. |
| 8. README con deploy | **Completa** | `README.md` tiene la sección "Publicación (deploy)": base MySQL en Clever Cloud y app en Render (plan gratuito). `app.py` lee `PORT` y `FLASK_DEBUG`. |
| 9. Drag and drop | **Completa (era opcional)** | `static/js/arrastrar_orden.js`, ruta `/orden/guardar` y `actualizar_orden()` en `consultas_edicion.py`. El campo "Orden" de los formularios sigue funcionando. |

**Estado final: las 9 etapas están completas.**
El usuario autorizó seguir con todas las etapas sin pedir confirmación en cada
una. Si pide cambios nuevos, volver a trabajar por etapas y frenar al terminar
cada una, salvo que vuelva a autorizar lo contrario.

---

## 7. Notas para no olvidar

- Usuario de ejemplo del SQL: `admin` / `admin123` (cambiar antes de publicar
  con `python cambiar_clave.py`).
- El PDF es un archivo estático de ejemplo; no se genera desde Flask.
- `templates/modales/` está vacía: los modales reales están en
  `templates/modal_edicion.html`.
- La carpeta del portfolio todavía no tiene commit en Git (aparece como `?? ./`).
- Ante cualquier duda: elegir la opción más simple y explicarla con palabras
  de principiante.
