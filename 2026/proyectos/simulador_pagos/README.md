# Simulador de Pago y Cobro

Aplicación web educativa para registrar usuarios, administrar productos, crear pedidos y **simular** operaciones de pago y cobro. No procesa dinero real ni se conecta a ninguna pasarela de pago.

## Objetivos

- Practicar Python y Flask con un caso práctico completo.
- Implementar autenticación de usuarios, CRUD de productos, pedidos y simulación de pagos.
- Trabajar con base de datos SQLite, formularios validados y protección de rutas.

## Tecnologías utilizadas

| Tecnología | Para qué sirve |
|---|---|
| Python | Lenguaje principal |
| Flask | Framework web |
| Flask-SQLAlchemy | Modelos y base de datos |
| Flask-Login | Sesiones de usuario (login/logout) |
| Flask-WTF y WTForms | Formularios y validaciones (con CSRF) |
| Flask-Migrate | Migraciones opcionales de la base de datos |
| SQLite | Base de datos inicial (archivo local) |
| HTML5, CSS3, Jinja2 | Plantillas y diseño |
| email-validator | Validación de direcciones de email |

## Estructura del proyecto

```
simulador_pagos/
├── app.py              # Aplicación: configuración, modelos, formularios y rutas
├── config.py           # Configuración adicional (opcional)
├── requirements.txt    # Dependencias
├── probar_app.py       # Pruebas automáticas (usa instance/test.db)
├── ver_db.py           # Ver contenido de la base de datos
├── limpiar_db.py       # Vaciar datos de prueba (conserva cuentas reales)
├── .env.example        # Ejemplo de variables de entorno
├── .gitignore
├── README.md
├── instance/
│   ├── app.db          # Base de datos de desarrollo (se crea sola)
│   └── test.db         # Base de datos de pruebas (la crea probar_app.py)
├── templates/
│   ├── base.html       # Layout común (barra de navegación)
│   ├── main/index.html # Panel principal (dashboard)
│   ├── auth/           # login.html, registro.html
│   ├── productos/      # lista, catalogo, nuevo, ver, editar
│   ├── pedidos/        # lista, crear, detalle
│   ├── pagos/          # lista, form (simulación)
│   └── errores/        # 403, 404, 500
└── static/
    └── css/style.css   # Estilos (negro, blanco y rojo)
```

## Requisitos previos

- Python 3.10 o superior ([python.org](https://www.python.org/downloads/))
- Terminal o consola de comandos

## Instalación

### 1. Crear y activar el entorno virtual

Windows:

```bash
cd simulador_pagos
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:

```bash
cd simulador_pagos
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Variables de entorno (opcional)

Copia el archivo de ejemplo y definí tu clave secreta:

```bash
copy .env.example .env
```

En `.env` podés cambiar `SECRET_KEY` por un valor propio. Si no se define, la aplicación usa una clave de desarrollo.

### 4. Inicializar la base de datos

```bash
python -c "import app; app.crear_base_datos()"
```

Esto crea las tablas y el usuario de prueba. También se ejecuta automáticamente la primera vez que se levanta la aplicación.

## Ejecutar la aplicación

```bash
python app.py
```

Abrí en el navegador: **http://127.0.0.1:5000**

## Usuario de prueba

| Email | Contraseña |
|---|---|
| `test@test.com` | `password123` |

Se crea automáticamente al inicializar la base de datos.

## Funcionalidades

- **Registro e inicio de sesión** con contraseñas protegidas con hash (werkzeug).
- **Productos**: crear, listar, buscar por nombre, ver, editar y eliminar (solo el propietario puede modificarlos).
- **Catálogo**: productos activos de otros usuarios, con opción de comprar.
- **Desactivación inteligente**: si un producto tiene pedidos asociados no se borra: se marca `activo = False`, se conserva el historial y desaparece del catálogo.
- **Pedidos**: elegir producto y cantidad, con validación de stock, de productos activos y cálculo del total en el servidor.
- **Simulación de pagos**: tres resultados posibles (aprobado, rechazado, pendiente) con métodos ficticios (saldo, tarjeta de prueba, transferencia simulada).
- **Panel principal** con productos, pedidos, pagos aprobados, importe cobrado (simulado), últimas transacciones, productos recientes y accesos rápidos.
- **Historial de pagos** con identificador de transacción, y pagos visibles en el detalle de cada pedido.
- **Páginas de error** 403, 404 y 500.
- **Diseño responsive** en negro, blanco y rojo (las tablas se desplazan en pantallas chicas).

## Flujo de demostración

1. Iniciar sesión con el usuario de prueba (o registrar uno nuevo).
2. Crear un producto propio: *Productos → + Agregar nuevo producto*.
3. Ir al **Catálogo** (barra de navegación) y abrir un producto de otro usuario.
4. Pulsar **Comprar**, indicar la cantidad y crear el pedido (queda *pendiente*).
5. Abrir el pedido y pulsar **Simular pago**.
6. Elegir método y resultado de la prueba:
   - **Aprobado**: el pedido pasa a *pagado* y se descuenta el stock (una sola vez).
   - **Rechazado**: el pedido sigue *pendiente* y no se descuenta stock.
   - **Pendiente**: el pedido no se marca como pagado.
7. Revisar el panel, el detalle del pedido y el historial de pagos.
8. Probar la desactivación: *Productos → Eliminar* un producto con pedidos (queda *Inactivo* y sale del catálogo).

## Pruebas automáticas

```bash
python probar_app.py
```

**No hace falta tener el servidor de desarrollo corriendo.** El script levanta su
propio servidor en el puerto 5001 usando una base de datos de pruebas separada
(`instance/test.db`), así los datos de desarrollo nunca se tocan. Si la prueba
termina con código de salida 0, todo pasó.

Ejecuta **31 pruebas**: registro, login, rutas protegidas, productos, validaciones
de precio, búsqueda, catálogo, protección CSRF (400 sin token), pedidos, cálculo
de importes en el servidor, los tres resultados de pago, pago duplicado, historial
de pagos, desactivación de productos con pedidos, productos inactivos no comprables,
permisos entre usuarios (editar/eliminar/ver) y stock.

Utilidades adicionales:

```bash
python ver_db.py       # ver el contenido de la base de datos de desarrollo
python limpiar_db.py   # vaciar datos de prueba (conserva las cuentas reales)
```

## Limitaciones del simulador

- **No procesa dinero real**: no hay conexión con bancos, tarjetas ni pasarelas de pago.
- No solicita ni almacena números de tarjeta, CVV ni credenciales bancarias.
- El selector de resultado (aprobado/rechazado/pendiente) es solo para demostración en clase; una transacción real nunca se validaría así.
- Los importes del panel son **ficticios** y no representan dinero disponible.
- SQLite y el servidor de desarrollo de Flask son adecuados solo para fines de aprendizaje.

## Modelos y relaciones

| Modelo | Campos principales | Relaciones |
|---|---|---|
| **Usuario** | nombre, email único, contraseña (hash), fecha de creación | tiene muchos `productos`, `pedidos` y `pagos` |
| **Producto** | nombre, descripción, precio, stock, activo, propietario | pertenece a un `usuario`; tiene muchos `detalles` |
| **Pedido** | comprador, estado (`pendiente`/`pagado`), fecha | pertenece a un `usuario`; tiene muchos `detalles` y `pagos` |
| **DetallePedido** | cantidad, precio_unitario | une un `pedido` con un `producto` |
| **Pago** | importe, método, estado, identificador de transacción | pertenece a un `pedido` y a un `usuario` |

**Reglas clave:**

- El total del pedido se calcula siempre en el servidor con `Pedido.calcular_total()`.
- El stock solo se descuenta cuando un pago se aprueba, y una única vez.
- Un pedido ya pagado no puede pagarse dos veces.
- Un producto con pedidos asociados nunca se borra: se desactiva (`activo = False`).
- Cada usuario solo puede ver y modificar sus propios recursos.
