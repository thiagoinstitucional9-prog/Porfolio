from django.contrib.auth.models import User

usuarios = User.objects.all().order_by('id')
print('| ID | Usuario | Email | Contraseña (nota) | Superusuario | Staff | Grupos | Permisos |')
print('|----|---------|-------|-------------------|--------------|-------|--------|----------|')
for u in usuarios:
    grupos = ', '.join([g.name for g in u.groups.all()]) or 'Sin rol'
    if u.is_superuser:
        rol = 'Administrador/Superusuario'
        perms = 'Todos los permisos'
    elif grupos == 'Empleado':
        perms = 'Gestionar empleados/pasajeros, ver coches/líneas/cocheras, ver/asignar viajes'
    elif grupos == 'Cliente':
        perms = 'Sin permisos en panel de gestión (solo sitio público)'
    else:
        perms = 'Sin permisos'
    print(f"| {u.id} | {u.username} | {u.email} | (hasheada) | {'Sí' if u.is_superuser else 'No'} | {'Sí' if u.is_staff else 'No'} | {grupos} | {perms} |")
