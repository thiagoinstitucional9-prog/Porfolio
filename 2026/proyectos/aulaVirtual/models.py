from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db, login_manager


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="estudiante")

    cursos_dictados = db.relationship("Curso", backref="profesor", lazy=True)
    inscripciones = db.relationship("Inscripcion", backref="estudiante", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def es_admin(self):
        return self.rol == "admin"

    def es_profesor(self):
        return self.rol == "profesor"

    def es_estudiante(self):
        return self.rol == "estudiante"


@login_manager.user_loader
def cargar_usuario(usuario_id):
    return Usuario.query.get(int(usuario_id))


class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    id_profesor = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    contenidos = db.relationship("Contenido", backref="curso", lazy=True, cascade="all, delete-orphan")
    evaluaciones = db.relationship("Evaluacion", backref="curso", lazy=True, cascade="all, delete-orphan")
    inscripciones = db.relationship("Inscripcion", backref="curso", lazy=True, cascade="all, delete-orphan")


class Inscripcion(db.Model):
    __table_args__ = (db.UniqueConstraint("id_curso", "id_estudiante", name="uq_inscripcion"),)
    id = db.Column(db.Integer, primary_key=True)
    id_curso = db.Column(db.Integer, db.ForeignKey("curso.id"), nullable=False)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)



class Contenido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_curso = db.Column(db.Integer, db.ForeignKey("curso.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    url_o_archivo = db.Column(db.String(255), nullable=False)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)


class Pregunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_evaluacion = db.Column(db.Integer, db.ForeignKey("evaluacion.id"), nullable=False)
    enunciado = db.Column(db.Text, nullable=False)
    respuesta_correcta = db.Column(db.Text)

    evaluacion = db.relationship("Evaluacion", backref=db.backref("preguntas", lazy=True, cascade="all, delete-orphan"))


class EntregaEvaluacion(db.Model):
    __table_args__ = (db.UniqueConstraint("id_evaluacion", "id_estudiante", name="uq_entrega"),)

    id = db.Column(db.Integer, primary_key=True)
    id_evaluacion = db.Column(db.Integer, db.ForeignKey("evaluacion.id"), nullable=False)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    respuestas = db.Column(db.Text, nullable=False)
    calificacion = db.Column(db.Float)
    fecha_entrega = db.Column(db.DateTime, default=datetime.utcnow)

    evaluacion = db.relationship("Evaluacion", backref=db.backref("entregas", lazy=True, cascade="all, delete-orphan"))
    estudiante = db.relationship("Usuario", backref="entregas")


class Evaluacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_curso = db.Column(db.Integer, db.ForeignKey("curso.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
