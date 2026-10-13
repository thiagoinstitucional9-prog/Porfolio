#!/usr/bin/env python
"""Simulador de Pago y Cobro - Aplicación Flask."""
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, Email
from werkzeug.security import generate_password_hash, check_password_hash

# ========== CONFIGURACIÓN ==========

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# SECRET_KEY desde variable de entorno (no guardar secretos reales en el código)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'simulador-pago-cobro-desarrollo')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', f'sqlite:///{os.path.join(basedir, "instance", "app.db")}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth_login'  # a dónde redirigir si no hay sesión
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'

# Protección CSRF en TODOS los formularios (y función csrf_token() en las plantillas)
csrf = CSRFProtect(app)

# Migraciones de base de datos con Flask-Migrate (opcional: comandos "flask db ...")
Migrate(app, db)


# ========== MODELOS DE LA BASE DE DATOS ==========

class Usuario(UserMixin, db.Model):
    """Usuario de la aplicación."""
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    cuenta_activa = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """Guarda la contraseña con hash seguro (nunca en texto plano)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Comprueba si la contraseña coincide con el hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.email}>'


class Producto(db.Model):
    """Producto que pertenece a un usuario."""
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    activo = db.Column(db.Boolean, default=True)

    # Relación inversa: producto.propietario
    propietario = db.relationship('Usuario', backref='productos')

    def __repr__(self):
        return f'<Producto {self.nombre}>'


class Pedido(db.Model):
    """Pedido creado por un usuario."""
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagado, rechazado
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)

    # Relación inversa: pedido.usuario
    usuario = db.relationship('Usuario', backref='pedidos')

    def calcular_total(self):
        """Calcula el total del pedido en el servidor (nunca se confía en el navegador)."""
        total = 0
        for detalle in self.detalles:
            total += detalle.cantidad * detalle.precio_unitario
        return round(total, 2)

    def __repr__(self):
        return f'<Pedido {self.id} - {self.estado}>'


class DetallePedido(db.Model):
    """Une un pedido con un producto y la cantidad comprada."""
    __tablename__ = 'detalle_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Float, nullable=False)  # precio al momento de crear el pedido

    # Relaciones inversas: detalle.pedido y detalle.producto
    pedido = db.relationship('Pedido', backref='detalles')
    producto = db.relationship('Producto', backref='detalles')

    def __repr__(self):
        return f'<Detalle pedido={self.pedido_id} producto={self.producto_id}>'


class Pago(db.Model):
    """Pago simulado de un pedido."""
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    importe = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(30), nullable=False)
    estado = db.Column(db.String(20), nullable=False)  # aprobado, rechazado, pendiente
    identificador_transaccion = db.Column(db.String(64), unique=True, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)

    # Relaciones inversas: pago.pedido y pago.usuario
    pedido = db.relationship('Pedido', backref='pagos')
    usuario = db.relationship('Usuario', backref='pagos')

    def __repr__(self):
        return f'<Pago {self.id} - {self.estado}>'


# ========== FORMULARIOS ==========

class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio'), Length(min=2, max=100)
    ])
    email = StringField('Email', validators=[
        DataRequired(message='El email es obligatorio'), Email(message='Email inválido'), Length(max=120)
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'), Length(min=6, max=100, message='Mínimo 6 caracteres')
    ])
    submit = SubmitField('Registrarse')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='El email es obligatorio'), Email(message='Email inválido'), Length(max=120)
    ])
    password = PasswordField('Contraseña', validators=[DataRequired(message='La contraseña es obligatoria')])
    submit = SubmitField('Iniciar sesión')


class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio'), Length(min=2, max=100)
    ])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    precio = FloatField('Precio', validators=[
        DataRequired(message='El precio es obligatorio'), NumberRange(min=0, message='El precio no puede ser negativo')
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(message='El stock es obligatorio'), NumberRange(min=0, message='El stock no puede ser negativo')
    ])
    activo = BooleanField('Producto activo')
    submit = SubmitField('Guardar producto')


class PedidoForm(FlaskForm):
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(message='La cantidad es obligatoria'), NumberRange(min=1, message='La cantidad debe ser al menos 1')
    ])
    submit = SubmitField('Crear pedido')


class PagoForm(FlaskForm):
    metodo_pago = SelectField('Método de pago', choices=[
        ('saldo', 'Saldo ficticio'),
        ('tarjeta_credito', 'Tarjeta de crédito de prueba'),
        ('tarjeta_debito', 'Tarjeta de débito de prueba'),
        ('transferencia', 'Transferencia simulada')
    ])
    # Solo para demostración: permite elegir el resultado de la prueba
    resultado_demo = SelectField('Resultado de la prueba (demo)', choices=[
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('pendiente', 'Pendiente')
    ])
    submit = SubmitField('Simular pago')


# ========== CARGAR USUARIO PARA FLASK-LOGIN ==========

@login_manager.user_loader
def cargar_usuario(id_usuario):
    return db.session.get(Usuario, int(id_usuario))


# ========== RUTAS DE AUTENTICACIÓN ==========

@app.route('/auth/registro', methods=['GET', 'POST'])
def auth_registro():
    """Registro de usuarios nuevos."""
    if current_user.is_authenticated:
        return redirect(url_for('main_index'))

    form = RegistroForm()
    if form.validate_on_submit():
        # Verificar que el email no esté registrado
        email_existe = Usuario.query.filter_by(email=form.email.data).first()
        if email_existe:
            flash('Ese email ya está registrado. Inicia sesión.', 'danger')
        else:
            usuario = Usuario()
            usuario.nombre = form.nombre.data
            usuario.email = form.email.data
            usuario.set_password(form.password.data)  # hash seguro
            db.session.add(usuario)
            db.session.commit()
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth_login'))

    return render_template('auth/registro.html', form=form)


@app.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    """Inicio de sesión."""
    if current_user.is_authenticated:
        return redirect(url_for('main_index'))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('main_index'))
        flash('Email o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html', form=form)


@app.route('/auth/logout', methods=['POST'])
@login_required
def auth_logout():
    """Cierre de sesión (POST para evitar cambios por accidente con GET)."""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('auth_login'))


# ========== RUTA PRINCIPAL (DASHBOARD) ==========

@app.route('/')
@app.route('/index')
@login_required
def main_index():
    """Panel principal con resumen del usuario."""
    # Contadores del panel
    total_productos = Producto.query.filter_by(usuario_id=current_user.id, activo=True).count()
    total_pedidos = Pedido.query.filter_by(usuario_id=current_user.id).count()
    pagos_aprobados = Pago.query.filter_by(usuario_id=current_user.id, estado='aprobado').count()

    # Total cobrado (solo importes SIMULADOS, no es dinero real)
    total_cobros = db.session.query(db.func.sum(Pago.importe)).filter(
        Pago.usuario_id == current_user.id, Pago.estado == 'aprobado'
    ).scalar() or 0.0

    # Últimas transacciones, pedidos pendientes y productos recientes
    ultimas_transacciones = Pago.query.filter_by(usuario_id=current_user.id)\
        .order_by(Pago.fecha_creacion.desc()).limit(5).all()
    pedidos_pendientes = Pedido.query.filter_by(usuario_id=current_user.id, estado='pendiente')\
        .order_by(Pedido.fecha_creacion.desc()).all()
    productos_recientes = Producto.query.filter_by(usuario_id=current_user.id)\
        .order_by(Producto.fecha_creacion.desc()).limit(5).all()

    return render_template(
        'main/index.html',
        total_productos=total_productos,
        total_pedidos=total_pedidos,
        pagos_aprobados=pagos_aprobados,
        total_cobros=round(float(total_cobros), 2),
        ultimas_transacciones=ultimas_transacciones,
        pedidos_pendientes=pedidos_pendientes,
        productos_recientes=productos_recientes
    )


# ========== RUTAS DE PRODUCTOS ==========

@app.route('/productos')
@login_required
def productos_lista():
    """Lista TODOS los productos propios (incluye los desactivados)."""
    productos = Producto.query.filter_by(usuario_id=current_user.id)

    # Búsqueda opcional por nombre (?buscar=teclado)
    texto_busqueda = request.args.get('buscar', '').strip()
    if texto_busqueda:
        productos = productos.filter(Producto.nombre.ilike(f'%{texto_busqueda}%'))

    productos = productos.order_by(Producto.fecha_creacion.desc()).all()
    return render_template('productos/lista.html', productos=productos, buscar=texto_busqueda)


@app.route('/catalogo')
@login_required
def catalogo():
    """Catálogo público: productos ACTIVOS de otros usuarios (para comprar)."""
    productos = Producto.query.filter(
        Producto.usuario_id != current_user.id,
        Producto.activo == True
    )

    # Búsqueda opcional por nombre
    texto_busqueda = request.args.get('buscar', '').strip()
    if texto_busqueda:
        productos = productos.filter(Producto.nombre.ilike(f'%{texto_busqueda}%'))

    productos = productos.order_by(Producto.fecha_creacion.desc()).all()
    return render_template('productos/catalogo.html', productos=productos, buscar=texto_busqueda)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def productos_nuevo():
    """Crea un producto nuevo."""
    form = ProductoForm()
    if form.validate_on_submit():
        producto = Producto()
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.precio = form.precio.data
        producto.stock = form.stock.data
        producto.activo = form.activo.data
        producto.usuario_id = current_user.id

        db.session.add(producto)
        db.session.commit()
        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('productos_lista'))

    return render_template('productos/nuevo.html', form=form)


@app.route('/productos/<int:producto_id>')
@login_required
def productos_ver(producto_id):
    """Muestra el detalle de un producto propio o de otro usuario (catálogo)."""
    producto = db.get_or_404(Producto, producto_id)
    es_mio = producto.usuario_id == current_user.id

    # Los productos inactivos de otros usuarios no se muestran
    if not es_mio and not producto.activo:
        flash('Este producto ya no está disponible.', 'warning')
        return redirect(url_for('catalogo'))

    return render_template('productos/ver.html', producto=producto, es_mio=es_mio)


@app.route('/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
@login_required
def productos_editar(producto_id):
    """Edita un producto propio."""
    producto = db.get_or_404(Producto, producto_id)

    if producto.usuario_id != current_user.id:
        flash('No tienes permiso para editar este producto.', 'danger')
        return redirect(url_for('productos_lista'))

    form = ProductoForm(obj=producto)
    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.precio = form.precio.data
        producto.stock = form.stock.data
        producto.activo = form.activo.data

        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('productos_ver', producto_id=producto.id))

    return render_template('productos/editar.html', form=form, producto=producto)


@app.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
@login_required
def productos_eliminar(producto_id):
    """Elimina un producto propio. Solo POST (protegido con CSRF).

    Si el producto ya tiene pedidos, no se borra: se desactiva
    para conservar el historial de los pedidos.
    """
    producto = db.get_or_404(Producto, producto_id)

    if producto.usuario_id != current_user.id:
        flash('No tienes permiso para eliminar este producto.', 'danger')
        return redirect(url_for('productos_lista'))

    if producto.detalles:
        # Tiene pedidos asociados: se desactiva en lugar de borrar
        producto.activo = False
        db.session.commit()
        flash('El producto tiene pedidos asociados. Se desactivó en lugar de eliminarlo.', 'warning')
    else:
        # Sin pedidos: se elimina definitivamente
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente.', 'success')

    return redirect(url_for('productos_lista'))


# ========== RUTAS DE PEDIDOS ==========

@app.route('/pedidos/crear/<int:producto_id>', methods=['GET', 'POST'])
@login_required
def pedidos_crear(producto_id):
    """Crea un pedido a partir de un producto del catálogo."""
    producto = db.get_or_404(Producto, producto_id)

    # No se permite comprar productos propios
    if producto.usuario_id == current_user.id:
        flash('No puedes comprar tus propios productos.', 'danger')
        return redirect(url_for('productos_lista'))

    # No se permiten productos desactivados
    if not producto.activo:
        flash('Este producto ya no está disponible.', 'warning')
        return redirect(url_for('catalogo'))

    # Sin stock no se puede crear el pedido
    if producto.stock <= 0:
        flash('Este producto no tiene stock disponible.', 'danger')
        return redirect(url_for('catalogo'))

    form = PedidoForm()
    if form.validate_on_submit():
        cantidad = form.cantidad.data

        # Verificar stock suficiente en el servidor
        if cantidad > producto.stock:
            flash(f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles.', 'danger')
        else:
            # Crear pedido con estado pendiente
            nuevo_pedido = Pedido(usuario_id=current_user.id, estado='pendiente')
            db.session.add(nuevo_pedido)
            db.session.flush()  # obtiene el id del pedido recién creado

            detalle = DetallePedido(
                pedido_id=nuevo_pedido.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio  # precio registrado al crear el pedido
            )
            db.session.add(detalle)
            db.session.commit()

            flash('Pedido creado exitosamente. Ahora puedes simular el pago.', 'success')
            return redirect(url_for('pedidos_ver', pedido_id=nuevo_pedido.id))

    return render_template('pedidos/crear.html', form=form, producto=producto)


@app.route('/pedidos')
@login_required
def pedidos_lista():
    """Lista todos los pedidos propios."""
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id)\
        .order_by(Pedido.fecha_creacion.desc()).all()
    return render_template('pedidos/lista.html', pedidos=pedidos)


@app.route('/pedidos/<int:pedido_id>')
@login_required
def pedidos_ver(pedido_id):
    """Muestra el detalle de un pedido."""
    pedido = db.get_or_404(Pedido, pedido_id)

    if pedido.usuario_id != current_user.id:
        flash('No tienes acceso a este pedido.', 'danger')
        return redirect(url_for('main_index'))

    return render_template('pedidos/detalle.html', pedido=pedido)


# ========== SIMULADOR DE PAGO ==========

@app.route('/pagos/pagar/<int:pedido_id>', methods=['GET', 'POST'])
@login_required
def pagos_pagar(pedido_id):
    """Simula el pago de un pedido (sin dinero real)."""
    pedido = db.get_or_404(Pedido, pedido_id)

    if pedido.usuario_id != current_user.id:
        flash('No tienes acceso a este pedido.', 'danger')
        return redirect(url_for('main_index'))

    # Un pedido pagado no se puede pagar dos veces
    if pedido.estado == 'pagado':
        flash('Este pedido ya fue pagado. No se permite pagar dos veces.', 'warning')
        return redirect(url_for('pedidos_ver', pedido_id=pedido.id))

    if not pedido.detalles:
        flash('El pedido no tiene productos.', 'danger')
        return redirect(url_for('pedidos_ver', pedido_id=pedido.id))

    form = PagoForm()
    if form.validate_on_submit():
        resultado = form.resultado_demo.data  # aprobado, rechazado o pendiente

        # El importe SIEMPRE se calcula en el servidor
        importe = pedido.calcular_total()
        producto = pedido.detalles[0].producto

        if resultado == 'aprobado':
            # Verificar stock antes de aprobar
            if producto.stock < pedido.detalles[0].cantidad:
                resultado = 'rechazado'
                flash('Pago rechazado: no hay stock suficiente.', 'danger')
            else:
                # Registrar el pago, marcar pedido como pagado y descontar stock UNA sola vez
                pedido.estado = 'pagado'
                producto.stock -= pedido.detalles[0].cantidad
                flash('¡Pago aprobado! El pedido ha sido pagado (importe simulado).', 'success')
        elif resultado == 'rechazado':
            # El pedido queda pendiente y NO se descuenta stock
            flash('Pago rechazado. El pedido continúa pendiente.', 'danger')
        else:
            # Pago pendiente: el pedido no se marca como pagado
            flash('Pago en estado pendiente. Consulta su estado más tarde.', 'info')

        pago = Pago(
            pedido_id=pedido.id,
            usuario_id=current_user.id,
            importe=importe,
            metodo_pago=form.metodo_pago.data,
            estado=resultado,
            identificador_transaccion=f'TX-{pedido.id}-{datetime.now().strftime("%Y%m%d%H%M%S%f")}'
        )
        db.session.add(pago)
        db.session.commit()

        return redirect(url_for('pedidos_ver', pedido_id=pedido.id))

    return render_template('pagos/form.html', form=form, pedido=pedido)


@app.route('/pagos')
@login_required
def pagos_lista():
    """Historial de pagos simulados del usuario."""
    pagos = Pago.query.filter_by(usuario_id=current_user.id)\
        .order_by(Pago.fecha_creacion.desc()).all()
    return render_template('pagos/lista.html', pagos=pagos)


# ========== PÁGINAS DE ERROR ==========

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errores/404.html'), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errores/403.html'), 403


@app.errorhandler(500)
def internal_error(error):
    return render_template('errores/500.html'), 500


# ========== INICIALIZACIÓN ==========

def crear_base_datos():
    """Crea las tablas y un usuario de prueba si no existen."""
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    with app.app_context():
        db.create_all()

        # Usuario de prueba para la demostración
        if not Usuario.query.filter_by(email='test@test.com').first():
            usuario = Usuario()
            usuario.nombre = 'Usuario de Prueba'
            usuario.email = 'test@test.com'
            usuario.set_password('password123')
            db.session.add(usuario)
            db.session.commit()
            print('Usuario de prueba creado: test@test.com / password123')


if __name__ == '__main__':
    crear_base_datos()
    app.run(debug=True)
