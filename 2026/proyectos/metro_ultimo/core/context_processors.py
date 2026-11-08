def rol_usuario(request):
    """Devuelve el rol del usuario para mostrarlo en las plantillas."""
    if not request.user.is_authenticated:
        return {"rol_usuario": ""}
    if request.user.is_superuser:
        return {"rol_usuario": "Administrador"}
    if request.user.groups.filter(name="Empleado").exists():
        return {"rol_usuario": "Empleado"}
    if request.user.groups.filter(name="Cliente").exists():
        return {"rol_usuario": "Cliente"}
    return {"rol_usuario": "Sin rol"}
