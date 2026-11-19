import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User, Group, Permission

# Ensure groups exist
cliente_group, _ = Group.objects.get_or_create(name='Cliente')
empleado_group, _ = Group.objects.get_or_create(name='Empleado')

# Set up empleado permissions
permisos = Permission.objects.filter(
    content_type__app_label='core',
    codename__in=[
        'add_empleado', 'change_empleado', 'delete_empleado',
        'view_empleado',
        'add_pasajero', 'change_pasajero', 'delete_pasajero',
        'view_pasajero',
        'view_coche', 'view_linea', 'view_cochera',
        'view_viaje', 'change_viaje',
    ],
)
empleado_group.permissions.set(permisos)
cliente_group.permissions.clear()

# Create users
users_data = [
    {'username': 'Admin', 'email': 'admin@metro.com', 'password': 'Admin1234!', 'superuser': True, 'staff': True, 'group': None},
    {'username': 'Empleado1', 'email': 'empleado1@metro.com', 'password': 'Empleado1234!', 'superuser': False, 'staff': False, 'group': empleado_group},
    {'username': 'Cliente1', 'email': 'cliente1@metro.com', 'password': 'Cliente1234!', 'superuser': False, 'staff': False, 'group': cliente_group},
    {'username': 'UsuarioSinRol', 'email': 'sinrol@metro.com', 'password': 'SinRol1234!', 'superuser': False, 'staff': False, 'group': None},
]

for data in users_data:
    user, created_flag = User.objects.get_or_create(username=data['username'], defaults={'email': data['email']})
    user.email = data['email']
    user.set_password(data['password'])
    user.is_superuser = data['superuser']
    user.is_staff = data['staff']
    user.save()
    if data['group']:
        user.groups.clear()
        user.groups.add(data['group'])
    else:
        user.groups.clear()

# Output table
print('| Usuario | Email | Contraseña | Rol | Grupos | Permisos |')
print('|---------|-------|------------|-----|--------|----------|')
for u in User.objects.all().order_by('id'):
    grupos = ', '.join([g.name for g in u.groups.all()]) or 'Sin rol'
    if u.is_superuser:
        rol = 'Administrador/Superusuario'
        perms = 'Todos los permisos'
    elif grupos == 'Empleado':
        rol = 'Empleado'
        perms = 'Gestionar empleados/pasajeros, ver coches/líneas/cocheras, ver/asignar viajes'
    elif grupos == 'Cliente':
        rol = 'Cliente'
        perms = 'Sin permisos en panel de gestión (solo sitio público)'
    else:
        rol = 'Sin rol'
        perms = 'Sin permisos'
    # Find password
    pwd = [d['password'] for d in users_data if d['username'] == u.username]
    pwd_str = pwd[0] if pwd else '(existente)'
    print(f'| {u.username} | {u.email} | {pwd_str} | {rol} | {grupos} | {perms} |')
