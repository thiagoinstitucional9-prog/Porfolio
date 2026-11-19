# formularios/formulario_login.py
# RESPONSABILIDAD DE ESTE ARCHIVO:
# Definir el formulario de inicio de sesion.
#
# Flask-WTF nos da dos cosas importantes:
# 1. Validacion de los campos.
# 2. Proteccion CSRF mediante el token oculto del formulario.

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class FormularioLogin(FlaskForm):
    """
    Formulario que se muestra dentro del modal de login.
    """

    nombre_usuario = StringField(
        "Usuario",
        validators=[
            DataRequired(message="Escribí tu nombre de usuario."),
            Length(max=50, message="El usuario no puede tener más de 50 caracteres."),
        ],
        render_kw={
            "placeholder": "admin",
            "autocomplete": "username",
            "autofocus": True,
        },
    )

    clave = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="Escribí tu contraseña."),
            Length(max=128, message="La contraseña es demasiado larga."),
        ],
        render_kw={
            "placeholder": "Tu contraseña",
            "autocomplete": "current-password",
        },
    )

    enviar = SubmitField("Entrar")
