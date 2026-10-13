"""Pruebas del Simulador de Pago y Cobro.

Se ejecutan con:   python probar_app.py

No hace falta tener el servidor de desarrollo corriendo:
el script crea su propio servidor en el puerto 5001 usando
una base de datos de PRUEBAS separada (instance/test.db),
así nunca se tocan los datos de desarrollo.
"""
import os
import re
import sys
import threading
import time
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar

# ===== Base de datos de pruebas SEPARADA de la de desarrollo =====
basedir = os.path.abspath(os.path.dirname(__file__))
ruta_test_db = os.path.join(basedir, 'instance', 'test.db')

# Siempre arrancamos con una base de pruebas limpia
if os.path.exists(ruta_test_db):
    os.remove(ruta_test_db)

# Debe definirse ANTES de importar app (app.py lee DATABASE_URL al importar)
os.environ['DATABASE_URL'] = 'sqlite:///' + ruta_test_db.replace('\\', '/')

from app import app, crear_base_datos  # noqa: E402

BASE = 'http://127.0.0.1:5001'
resultados = []

# Sesión compartida: todas las peticiones usan las mismas cookies
galletas = http.cookiejar.CookieJar()
operador = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(galletas))


# ===== Utilidades de prueba =====

def obtener_token(html):
    """Extrae el token CSRF de un formulario."""
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    return match.group(1) if match else None


def hacer(peticion):
    """Ejecuta una petición y devuelve (código, url_final, html)."""
    try:
        respuesta = operador.open(peticion, timeout=10)
        return respuesta.status, respuesta.geturl(), respuesta.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.geturl(), e.read().decode('utf-8')


def verificar(nombre, condicion):
    """Registra el resultado de una prueba."""
    resultados.append((nombre, bool(condicion)))
    estado = 'OK  ' if condicion else 'FALLA'
    print(f'[{estado}] {nombre}')


def obtener_token_de(ruta):
    _, _, html = hacer(urllib.request.Request(BASE + ruta))
    return obtener_token(html)


def login(email, password):
    token = obtener_token_de('/auth/login')
    datos = urllib.parse.urlencode({
        'csrf_token': token,
        'email': email,
        'password': password,
        'submit': 'Iniciar sesión'
    }).encode()
    return hacer(urllib.request.Request(BASE + '/auth/login', data=datos))


def cerrar_sesion():
    token = obtener_token_de('/')
    if token:
        datos = urllib.parse.urlencode({'csrf_token': token}).encode()
        hacer(urllib.request.Request(BASE + '/auth/logout', data=datos))


def registrar(nombre, email, password):
    token = obtener_token_de('/auth/registro')
    datos = urllib.parse.urlencode({
        'csrf_token': token,
        'nombre': nombre,
        'email': email,
        'password': password,
        'submit': 'Registrarse'
    }).encode()
    return hacer(urllib.request.Request(BASE + '/auth/registro', data=datos))


def crear_producto(nombre, precio, stock):
    """Crea un producto con la sesión actual y devuelve su id."""
    token = obtener_token_de('/productos/nuevo')
    datos = urllib.parse.urlencode({
        'csrf_token': token,
        'nombre': nombre,
        'descripcion': 'Producto de prueba',
        'precio': precio,
        'stock': stock,
        'activo': 'y',
        'submit': 'Guardar producto'
    }).encode()
    codigo, url_final, _ = hacer(urllib.request.Request(BASE + '/productos/nuevo', data=datos))
    if codigo != 200 or '/productos' not in url_final:
        return None
    # Buscar el id en la lista de productos propios
    _, _, html = hacer(urllib.request.Request(BASE + '/productos'))
    match = re.search(re.escape(nombre) + r'</td>.*?/productos/(\d+)', html, re.S)
    return match.group(1) if match else None


def crear_pedido(id_producto, cantidad):
    """Crea un pedido del producto indicado y devuelve su id (o None)."""
    token = obtener_token_de(f'/pedidos/crear/{id_producto}')
    datos = urllib.parse.urlencode({
        'csrf_token': token,
        'cantidad': str(cantidad),
        'submit': 'Crear pedido'
    }).encode()
    codigo, url_final, _ = hacer(urllib.request.Request(
        BASE + f'/pedidos/crear/{id_producto}', data=datos))
    if codigo != 200 or '/pedidos/' not in url_final:
        return None
    return url_final.rstrip('/').split('/')[-1]


def simular_pago(pedido_id, metodo, resultado):
    token = obtener_token_de(f'/pagos/pagar/{pedido_id}')
    datos = urllib.parse.urlencode({
        'csrf_token': token,
        'metodo_pago': metodo,
        'resultado_demo': resultado,
        'submit': 'Simular pago'
    }).encode()
    return hacer(urllib.request.Request(BASE + f'/pagos/pagar/{pedido_id}', data=datos))


# ===== Pruebas =====

def main():
    # ===== FASE 1: usuario de prueba crea su producto =====
    login('test@test.com', 'password123')
    id_propio = crear_producto('Teclado Mecanico', '150.50', '5')
    verificar('Producto propio creado', id_propio is not None)
    cerrar_sesion()

    # ===== FASE 2: otro usuario crea el producto a comprar =====
    registrar('Vendedor', 'vendedor@ejemplo.com', 'secreto123')
    login('vendedor@ejemplo.com', 'secreto123')
    id_ajeno = crear_producto('Auriculares', '80', '5')
    verificar('Producto de otro usuario creado', id_ajeno is not None)
    cerrar_sesion()

    # ===== FASE 3: autenticación =====
    # 1. Ruta protegida sin sesión
    codigo, url_final, _ = hacer(urllib.request.Request(BASE + '/'))
    verificar('Ruta protegida redirige al login', codigo == 200 and '/auth/login' in url_final)

    # 2. Login (redirige al panel, que puede ser / o /index)
    codigo, url_final, _ = login('test@test.com', 'password123')
    verificar('Login correcto',
              codigo == 200 and url_final.rstrip('/').endswith(('5001', '5001/index')))

    # 3. Panel
    codigo, _, html = hacer(urllib.request.Request(BASE + '/'))
    verificar('Panel carga con sesión', codigo == 200 and 'Dashboard' in html)

    # 4. Validación de precio negativo
    token = obtener_token_de('/productos/nuevo')
    datos = urllib.parse.urlencode({
        'csrf_token': token,
        'nombre': 'Inválido',
        'precio': '-5',
        'stock': '1',
        'submit': 'Guardar producto'
    }).encode()
    codigo, _, html = hacer(urllib.request.Request(BASE + '/productos/nuevo', data=datos))
    verificar('Precio negativo rechazado',
              codigo == 200 and 'no puede ser negativo' in html)

    # 5. Búsqueda por nombre
    codigo, _, html = hacer(urllib.request.Request(BASE + '/productos?buscar=Teclado'))
    verificar('Búsqueda por nombre', codigo == 200 and 'Teclado Mecanico' in html)

    # 6. Catálogo de productos de otros usuarios
    codigo, _, html = hacer(urllib.request.Request(BASE + '/catalogo'))
    verificar('Catálogo muestra productos de otros',
              codigo == 200 and 'Auriculares' in html and 'Teclado Mecanico' not in html)

    # 7. Protección CSRF: un POST sin token debe rechazarse (400)
    codigo, _, _ = hacer(urllib.request.Request(
        BASE + '/productos/nuevo', data=b'nombre=Hack&precio=1&stock=1'))
    verificar('POST sin token CSRF rechazado (400)', codigo == 400)

    # ===== FASE 4: pedidos =====
    # 8. No comprar producto propio
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/pedidos/crear/{id_propio}'))
    verificar('No se puede comprar producto propio', 'propios productos' in html)

    # 9. Crear pedido del producto ajeno
    pedido_1 = crear_pedido(id_ajeno, 2)
    verificar('Pedido creado', pedido_1 is not None)

    # 10. Stock insuficiente rechazado
    token = obtener_token_de(f'/pedidos/crear/{id_ajeno}')
    datos = urllib.parse.urlencode({
        'csrf_token': token,
        'cantidad': '999',
        'submit': 'Crear pedido'
    }).encode()
    codigo, _, html = hacer(urllib.request.Request(
        BASE + f'/pedidos/crear/{id_ajeno}', data=datos))
    verificar('Stock insuficiente rechazado',
              codigo == 200 and 'Stock insuficiente' in html)

    # 11. El total del pedido se calcula en el servidor (2 x 80 = 160)
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/pedidos/{pedido_1}'))
    verificar('Importe calculado en el servidor ($160)',
              codigo == 200 and '$160' in html)

    # ===== FASE 5: simulación de pagos =====
    # 12. Pago APROBADO
    simular_pago(pedido_1, 'tarjeta_credito', 'aprobado')
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/pedidos/{pedido_1}'))
    verificar('Pago aprobado marca pedido como pagado', 'Pagado' in html)

    # 13. Pago duplicado bloqueado
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/pagos/pagar/{pedido_1}'))
    verificar('No se permite pagar dos veces', 'ya fue pagado' in html)

    # 14. Pago RECHAZADO
    pedido_2 = crear_pedido(id_ajeno, 1)
    simular_pago(pedido_2, 'saldo', 'rechazado')
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/pedidos/{pedido_2}'))
    verificar('Pago rechazado deja pedido pendiente', 'Pendiente' in html)

    # 15. Pago PENDIENTE
    pedido_3 = crear_pedido(id_ajeno, 1)
    simular_pago(pedido_3, 'transferencia', 'pendiente')
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/pedidos/{pedido_3}'))
    partes = html.split('Estado:</strong>')
    seccion_estado = partes[1][:300] if len(partes) > 1 else ''
    verificar('Pago pendiente no marca como pagado',
              bool(seccion_estado) and 'Pagado' not in seccion_estado)

    # 16. Historial de pagos
    codigo, _, html = hacer(urllib.request.Request(BASE + '/pagos'))
    verificar('Historial muestra los 3 pagos', codigo == 200 and html.count('TX-') >= 3)

    # 17. Detalle del pedido muestra sus pagos
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/pedidos/{pedido_1}'))
    verificar('Detalle del pedido muestra sus pagos', codigo == 200 and 'TX-' in html)

    # 18. Página 404
    codigo, _, _ = hacer(urllib.request.Request(BASE + '/no-existe'))
    verificar('Página 404 personalizada', codigo == 404)

    # ===== FASE 6: desactivación de producto con pedidos =====
    # 19. El vendedor intenta eliminar un producto CON pedidos:
    #     debe desactivarlo (no error 500) y conservar los pedidos
    cerrar_sesion()
    login('vendedor@ejemplo.com', 'secreto123')
    token = obtener_token_de(f'/productos/{id_ajeno}')
    datos = urllib.parse.urlencode({'csrf_token': token}).encode()
    codigo, url_final, html = hacer(urllib.request.Request(
        BASE + f'/productos/eliminar/{id_ajeno}', data=datos))
    verificar('Producto con pedidos se DESACTIVA sin error 500',
              codigo == 200 and 'desactivó' in html and '/productos' in url_final)

    # 20. El producto sigue existiendo (conserva el historial)
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/productos/{id_ajeno}'))
    verificar('Producto desactivado sigue existiendo (historial conservado)',
              codigo == 200 and 'Inactivo' in html)

    # 21. Ya no aparece en el catálogo
    cerrar_sesion()
    login('test@test.com', 'password123')
    codigo, _, html = hacer(urllib.request.Request(BASE + '/catalogo'))
    verificar('Producto desactivado sale del catálogo', 'Auriculares' not in html)

    # 22. Un producto inactivos no se puede comprar
    codigo, url_final, html = hacer(urllib.request.Request(
        BASE + f'/pedidos/crear/{id_ajeno}'))
    verificar('Producto inactivos no se puede comprar',
              'no está disponible' in html and '/pedidos/crear' not in url_final)

    # ===== FASE 7: registro y permisos =====
    # 23. Registro (primero cerrar sesión: la ruta solo funciona sin sesión)
    cerrar_sesion()
    codigo, url_final, _ = registrar('Comprador', 'otro@ejemplo.com', 'secreto123')
    verificar('Registro exitoso', codigo == 200 and '/auth/login' in url_final)

    # 24. Email duplicado
    codigo, _, html = registrar('Repetido', 'otro@ejemplo.com', 'secreto123')
    verificar('Email duplicado rechazado', 'ya está registrado' in html)

    # 25. Un usuario no puede EDITAR productos de otro
    login('otro@ejemplo.com', 'secreto123')
    codigo, url_final, _ = hacer(urllib.request.Request(
        BASE + f'/productos/editar/{id_propio}'))
    verificar('Usuario ajeno no puede editar producto ajeno',
              codigo == 200 and url_final.rstrip('/').endswith('/productos'))

    # 26. Un usuario no puede ELIMINAR productos de otro
    token = obtener_token_de(f'/productos/{id_propio}')
    datos = urllib.parse.urlencode({'csrf_token': token}).encode()
    codigo, _, html = hacer(urllib.request.Request(
        BASE + f'/productos/eliminar/{id_propio}', data=datos))
    verificar('Usuario ajeno no puede eliminar producto ajeno',
              'No tienes permiso' in html)

    # 27. Un usuario no accede al detalle de pedidos ajenos
    #     (la ruta redirige al panel propio)
    codigo, url_final, _ = hacer(urllib.request.Request(BASE + f'/pedidos/{pedido_1}'))
    verificar('Usuario ajeno no accede a pedido ajeno',
              codigo == 200 and '/pedidos/' not in url_final)

    # 28. Logout
    cerrar_sesion()
    codigo, url_final, _ = hacer(urllib.request.Request(BASE + '/'))
    verificar('Logout cierra la sesión', '/auth/login' in url_final)

    # ===== FASE 8: stock (con la sesión del vendedor) =====
    # 29. Stock descontado UNA sola vez con el pago aprobado (5 - 2 = 3)
    login('vendedor@ejemplo.com', 'secreto123')
    codigo, _, html = hacer(urllib.request.Request(BASE + f'/productos/{id_ajeno}'))
    verificar('Stock descontado una sola vez (queda 3)', 'Stock:</strong> 3' in html)
    cerrar_sesion()

    # ===== Resumen =====
    fallas = [n for n, ok in resultados if not ok]
    print('\n' + '=' * 50)
    print(f'Resultado: {len(resultados) - len(fallas)}/{len(resultados)} pruebas OK')
    if fallas:
        print('Fallaron:')
        for f in fallas:
            print('  -', f)
    return len(fallas)


def iniciar_servidor_pruebas():
    """Levanta Flask en un hilo, usando la base de datos de pruebas."""
    crear_base_datos()
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)


if __name__ == '__main__':
    # Servidor de pruebas en segundo plano (el hilo muere al terminar el script)
    hilo = threading.Thread(target=iniciar_servidor_pruebas, daemon=True)
    hilo.start()

    # Esperar a que el servidor esté listo
    listo = False
    for _ in range(30):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(BASE + '/auth/login', timeout=2)
            listo = True
            break
        except Exception:
            continue

    if not listo:
        print('No se pudo iniciar el servidor de pruebas.')
        sys.exit(1)

    print('Servidor de pruebas corriendo en el puerto 5001')
    print('Base de datos de pruebas:', ruta_test_db)
    print('-' * 50)
    fallos = main()
    sys.exit(1 if fallos else 0)
