from django.contrib.auth.models import User, Group, Permission

# Ensure groups exist
cliente_group, _ = Group.objects.get_or_create(name='Cliente')
empleado_group, _ = Group.objects.get_or_create(name='Empleado')

# Set up empleado permissions like in crear_grupos
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

created = []
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
    if user.is_superuser:
        perms_desc = 'Todos los permisos (Superusuario)'
        rol = 'Administrador/Superusuario'
    elif user.groups.filter(name='Empleado').exists():
        perms_desc = 'Gestionar empleados/pasajeros, ver coches/líneas/cocheras, ver/asignar viajes'
        rol = 'Empleado'
    elif user.groups.filter(name='Cliente').exists():
        perms_desc = 'Sin permisos en panel de gestión (solo sitio público)'
        rol = 'Cliente'
    else:
        perms_desc = 'Sin permisos'
        rol = 'Sin rol'
    created.append({
        'username': user.username,
        'email': user.email,
        'password': data['password'],
        'rol': rol,
        'permisos': perms_desc
    })

print('| Usuario | Email | Contraseña | Rol | Permisos |')
print('|---------|-------|------------|-----|----------|')
for c in created:
    print(f"| {c['username']} | {c['email']} | {c['password']} | {c['rol']} | {c['permisos']} |")
