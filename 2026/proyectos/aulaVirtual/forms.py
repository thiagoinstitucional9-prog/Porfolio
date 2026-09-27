from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, FileField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


class RegistroForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    confirmar_password = PasswordField(
        "Confirmar contraseña",
        validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Crear cuenta")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar")


class CursoForm(FlaskForm):
    nombre = StringField("Nombre del curso", validators=[DataRequired(), Length(max=150)])
    descripcion = TextAreaField("Descripción")
    submit = SubmitField("Guardar")


class ContenidoForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=150)])
    tipo = StringField("Tipo (PDF, video o enlace)", validators=[DataRequired(), Length(max=20)])
    enlace = StringField("Enlace externo", validators=[Optional(), Length(max=255)])
    archivo = FileField("Archivo")
    submit = SubmitField("Publicar contenido")


class EvaluacionForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=150)])
    descripcion = TextAreaField("Indicaciones")
    preguntas = TextAreaField("Preguntas", validators=[DataRequired()], description="Una pregunta por línea")
    submit = SubmitField("Crear evaluación")


class EntregaForm(FlaskForm):
    respuestas = TextAreaField("Respuestas", validators=[DataRequired()])
    submit = SubmitField("Entregar evaluación")


class CalificacionForm(FlaskForm):
    calificacion = FloatField("Calificación", validators=[DataRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField("Guardar calificación")
