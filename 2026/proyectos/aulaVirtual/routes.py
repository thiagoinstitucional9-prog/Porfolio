import os
from uuid import uuid4

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from extensions import db
from forms import CalificacionForm, ContenidoForm, CursoForm, EntregaForm, EvaluacionForm, LoginForm, RegistroForm
from models import Contenido, Curso, EntregaEvaluacion, Evaluacion, Inscripcion, Pregunta, Usuario


def es_gestor(curso):
    return current_user.es_admin() or curso.id_profesor == current_user.id


def puede_ver_curso(curso):
    if es_gestor(curso):
        return True
    return Inscripcion.query.filter_by(id_curso=curso.id, id_estudiante=current_user.id).first() is not None


def obtener_curso_visible(curso_id):
    curso = db.get_or_404(Curso, curso_id)
    if not puede_ver_curso(curso):
        abort(403)
    return curso


def cursos_visibles_para_usuario():
    """Devuelve los cursos cuyos materiales y evaluaciones puede consultar el usuario."""
    if current_user.es_admin() or current_user.es_profesor():
        return Curso.query.order_by(Curso.nombre).all()
    return [inscripcion.curso for inscripcion in current_user.inscripciones]


def registrar_rutas(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/registro", methods=["GET", "POST"])
    def registro():
        form = RegistroForm()
        if form.validate_on_submit():
            if Usuario.query.filter_by(email=form.email.data.lower()).first():
                flash("Ese email ya está registrado.", "error")
                return redirect(url_for("registro"))
            usuario = Usuario(nombre=form.nombre.data.strip(), email=form.email.data.lower())
            usuario.set_password(form.password.data)
            db.session.add(usuario)
            db.session.commit()
            flash("Cuenta creada correctamente. Ya podés ingresar.", "exito")
            return redirect(url_for("login"))
        if form.is_submitted():
            flash("No se pudo completar el registro. Revisá los campos marcados.", "error")
        return render_template("registro.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            usuario = Usuario.query.filter_by(email=form.email.data.lower()).first()
            if usuario and usuario.check_password(form.password.data):
                login_user(usuario)
                flash("¡Bienvenido/a!", "exito")
                return redirect(url_for("cursos"))
            flash("Email o contraseña incorrectos.", "error")
        elif form.is_submitted():
            flash("No se pudo iniciar sesión. Revisá el email y la contraseña.", "error")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Sesión cerrada.", "info")
        return redirect(url_for("index"))

    @app.route("/cursos")
    @login_required
    def cursos():
        lista_cursos = cursos_visibles_para_usuario()
        disponibles = []
        if current_user.es_estudiante():
            ids = [inscripcion.id_curso for inscripcion in current_user.inscripciones]
            disponibles = Curso.query.filter(~Curso.id.in_(ids)).order_by(Curso.nombre).all()
        return render_template("cursos/listado.html", cursos=lista_cursos, cursos_disponibles=disponibles)

    @app.route("/materiales")
    @login_required
    def materiales():
        cursos_usuario = cursos_visibles_para_usuario()
        materiales_por_curso = [
            (curso, Contenido.query.filter_by(id_curso=curso.id).order_by(Contenido.fecha_publicacion.desc()).all())
            for curso in cursos_usuario
        ]
        return render_template("contenidos/listado.html", materiales_por_curso=materiales_por_curso)

    @app.route("/evaluaciones")
    @login_required
    def evaluaciones():
        cursos_usuario = cursos_visibles_para_usuario()
        ids_cursos = [curso.id for curso in cursos_usuario]
        lista_evaluaciones = []
        if ids_cursos:
            lista_evaluaciones = Evaluacion.query.filter(
                Evaluacion.id_curso.in_(ids_cursos)
            ).order_by(Evaluacion.fecha.desc()).all()
        entregas = {}
        if current_user.es_estudiante() and lista_evaluaciones:
            ids_evaluaciones = [evaluacion.id for evaluacion in lista_evaluaciones]
            entregas = {
                entrega.id_evaluacion: entrega
                for entrega in EntregaEvaluacion.query.filter_by(id_estudiante=current_user.id).filter(
                    EntregaEvaluacion.id_evaluacion.in_(ids_evaluaciones)
                ).all()
            }
        return render_template(
            "evaluaciones/listado.html",
            evaluaciones=lista_evaluaciones,
            entregas=entregas,
        )

    @app.route("/cursos/nuevo", methods=["GET", "POST"])
    @login_required
    def crear_curso():
        if not (current_user.es_admin() or current_user.es_profesor()):
            abort(403)
        form = CursoForm()
        if form.validate_on_submit():
            db.session.add(Curso(nombre=form.nombre.data.strip(), descripcion=form.descripcion.data.strip(), id_profesor=current_user.id))
            db.session.commit()
            flash("Curso creado.", "exito")
            return redirect(url_for("cursos"))
        return render_template("cursos/formulario.html", form=form, titulo="Crear curso")

    @app.route("/cursos/<int:curso_id>/editar", methods=["GET", "POST"])
    @login_required
    def editar_curso(curso_id):
        curso = db.get_or_404(Curso, curso_id)
        if not es_gestor(curso):
            abort(403)
        form = CursoForm(obj=curso)
        if form.validate_on_submit():
            curso.nombre, curso.descripcion = form.nombre.data.strip(), form.descripcion.data.strip()
            db.session.commit()
            flash("Curso actualizado.", "exito")
            return redirect(url_for("ver_curso", curso_id=curso.id))
        return render_template("cursos/formulario.html", form=form, titulo="Editar curso")

    @app.post("/cursos/<int:curso_id>/eliminar")
    @login_required
    def eliminar_curso(curso_id):
        curso = db.get_or_404(Curso, curso_id)
        if not es_gestor(curso):
            abort(403)
        db.session.delete(curso)
        db.session.commit()
        flash("Curso eliminado.", "info")
        return redirect(url_for("cursos"))

    @app.post("/cursos/<int:curso_id>/inscribirse")
    @login_required
    def inscribirse(curso_id):
        if not current_user.es_estudiante():
            abort(403)
        db.get_or_404(Curso, curso_id)
        if not Inscripcion.query.filter_by(id_curso=curso_id, id_estudiante=current_user.id).first():
            db.session.add(Inscripcion(id_curso=curso_id, id_estudiante=current_user.id))
            db.session.commit()
            flash("Te inscribiste al curso.", "exito")
        return redirect(url_for("cursos"))

    @app.route("/cursos/<int:curso_id>")
    @login_required
    def ver_curso(curso_id):
        curso = obtener_curso_visible(curso_id)
        return render_template("cursos/detalle.html", curso=curso, es_gestor=es_gestor(curso))

    @app.route("/cursos/<int:curso_id>/contenidos/nuevo", methods=["GET", "POST"])
    @login_required
    def crear_contenido(curso_id):
        curso = db.get_or_404(Curso, curso_id)
        if not es_gestor(curso):
            abort(403)
        form = ContenidoForm()
        if form.validate_on_submit():
            archivo, destino = form.archivo.data, form.enlace.data.strip()
            if archivo and archivo.filename:
                nombre = f"{uuid4().hex}_{secure_filename(archivo.filename)}"
                carpeta = os.path.join(current_app.static_folder, "uploads")
                os.makedirs(carpeta, exist_ok=True)
                archivo.save(os.path.join(carpeta, nombre))
                destino = url_for("static", filename=f"uploads/{nombre}")
            if not destino:
                flash("Indicá un enlace o seleccioná un archivo.", "error")
            else:
                db.session.add(Contenido(titulo=form.titulo.data.strip(), tipo=form.tipo.data.strip(), url_o_archivo=destino, id_curso=curso.id))
                db.session.commit()
                flash("Contenido publicado.", "exito")
                return redirect(url_for("ver_curso", curso_id=curso.id))
        return render_template("contenidos/formulario.html", form=form, curso=curso)

    @app.post("/contenidos/<int:contenido_id>/eliminar")
    @login_required
    def eliminar_contenido(contenido_id):
        contenido = db.get_or_404(Contenido, contenido_id)
        curso = db.get_or_404(Curso, contenido.id_curso)
        if not es_gestor(curso):
            abort(403)
        db.session.delete(contenido)
        db.session.commit()
        flash("Contenido eliminado.", "info")
        return redirect(url_for("ver_curso", curso_id=curso.id))

    @app.route("/cursos/<int:curso_id>/evaluaciones/nueva", methods=["GET", "POST"])
    @login_required
    def crear_evaluacion(curso_id):
        curso = db.get_or_404(Curso, curso_id)
        if not es_gestor(curso):
            abort(403)
        form = EvaluacionForm()
        if form.validate_on_submit():
            evaluacion = Evaluacion(id_curso=curso.id, titulo=form.titulo.data.strip(), descripcion=form.descripcion.data.strip())
            db.session.add(evaluacion)
            for enunciado in form.preguntas.data.splitlines():
                if enunciado.strip():
                    evaluacion.preguntas.append(Pregunta(enunciado=enunciado.strip()))
            db.session.commit()
            flash("Evaluación creada.", "exito")
            return redirect(url_for("ver_curso", curso_id=curso.id))
        return render_template("evaluaciones/formulario.html", form=form, curso=curso)

    @app.route("/evaluaciones/<int:evaluacion_id>", methods=["GET", "POST"])
    @login_required
    def rendir_evaluacion(evaluacion_id):
        evaluacion = db.get_or_404(Evaluacion, evaluacion_id)
        curso = obtener_curso_visible(evaluacion.id_curso)
        if es_gestor(curso):
            return redirect(url_for("ver_curso", curso_id=curso.id))
        existente = EntregaEvaluacion.query.filter_by(id_evaluacion=evaluacion.id, id_estudiante=current_user.id).first()
        form = EntregaForm()
        if form.validate_on_submit() and not existente:
            db.session.add(EntregaEvaluacion(id_evaluacion=evaluacion.id, id_estudiante=current_user.id, respuestas=form.respuestas.data.strip()))
            db.session.commit()
            flash("Evaluación entregada.", "exito")
            return redirect(url_for("ver_curso", curso_id=curso.id))
        return render_template("evaluaciones/rendir.html", evaluacion=evaluacion, curso=curso, form=form, existente=existente)

    @app.route("/entregas/<int:entrega_id>/calificar", methods=["GET", "POST"])
    @login_required
    def calificar_entrega(entrega_id):
        entrega = db.get_or_404(EntregaEvaluacion, entrega_id)
        curso = db.get_or_404(Curso, entrega.evaluacion.id_curso)
        if not es_gestor(curso):
            abort(403)
        form = CalificacionForm(obj=entrega)
        if form.validate_on_submit():
            entrega.calificacion = form.calificacion.data
            db.session.commit()
            flash("Calificación guardada.", "exito")
            return redirect(url_for("ver_curso", curso_id=curso.id))
        return render_template("evaluaciones/calificar.html", form=form, entrega=entrega, curso=curso)
