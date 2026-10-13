"""Vaciar los datos de prueba y dejar la base lista para una demostración.

Elimina TODO lo que creó el sistema de pruebas (productos, pedidos y pagos
de la cuenta demo y de los usuarios de prueba), pero conserva siempre
cualquier cuenta creada por el usuario real (por ejemplo la del alumno).

No borra la base de datos: solo vacía tablas.
"""
import sqlite3
import os

basedir = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(basedir, 'instance', 'app.db')

# Cuentas que usa el sistema de pruebas
usuarios_de_prueba = ('test@test.com', 'vendedor@ejemplo.com', 'otro@ejemplo.com')

if not os.path.exists(ruta):
    print('La base de datos no existe todavía.')
else:
    conexion = sqlite3.connect(ruta)
    cursor = conexion.cursor()

    # Se borra en orden: primero las tablas que dependen de otras
    # (subconsulta para encontrar los ids de las cuentas de prueba)
    cuenta_prueba = f"SELECT id FROM usuarios WHERE email IN {usuarios_de_prueba}"

    cursor.execute(f"DELETE FROM pagos WHERE usuario_id IN ({cuenta_prueba})")
    cursor.execute(
        f"DELETE FROM detalle_pedido WHERE pedido_id IN "
        f"(SELECT id FROM pedidos WHERE usuario_id IN ({cuenta_prueba}))"
    )
    cursor.execute(f"DELETE FROM pedidos WHERE usuario_id IN ({cuenta_prueba})")
    cursor.execute(f"DELETE FROM productos WHERE usuario_id IN ({cuenta_prueba})")
    # Se conserva test@test.com (es la cuenta de demostración)
    cursor.execute(
        "DELETE FROM usuarios WHERE email IN "
        "('vendedor@ejemplo.com', 'otro@ejemplo.com')"
    )
    conexion.commit()

    print('Datos de prueba eliminados.')
    cursor.execute('SELECT email FROM usuarios')
    restantes = cursor.fetchall()
    print('Cuentas conservadas:')
    for (email,) in restantes:
        print('  -', email)
    conexion.close()
