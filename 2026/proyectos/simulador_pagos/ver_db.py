"""Ver el contenido actual de la base de datos (solo lectura)."""
import sqlite3
import os

basedir = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(basedir, 'instance', 'app.db')

if not os.path.exists(ruta):
    print('La base de datos no existe todavía.')
else:
    conexion = sqlite3.connect(ruta)
    cursor = conexion.cursor()
    for tabla in ['usuarios', 'productos', 'pedidos', 'detalle_pedido', 'pagos']:
        try:
            cursor.execute(f'SELECT * FROM {tabla}')
            filas = cursor.fetchall()
            print(f'{tabla}: {len(filas)} filas')
            for f in filas:
                print('   ', f)
        except Exception as e:
            print(f'{tabla}: {e}')
    conexion.close()
