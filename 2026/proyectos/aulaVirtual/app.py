from flask import Flask

from config import Config
from extensions import db, login_manager
from routes import registrar_rutas


# El proyecto ya usa la carpeta "statics"; se la declaramos a Flask para que
# url_for('static', ...) genere una URL que realmente exista.
aplicacion = Flask(__name__, static_folder="statics")
aplicacion.config.from_object(Config)

db.init_app(aplicacion)
login_manager.init_app(aplicacion)

with aplicacion.app_context():
    db.create_all()

registrar_rutas(aplicacion)


if __name__ == "__main__":
    aplicacion.run(debug=True)
