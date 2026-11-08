from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea los grupos Cliente y Empleado con sus permisos."

    def handle(self, *args, **options):
        cliente, _ = Group.objects.get_or_create(name="Cliente")
        empleado, _ = Group.objects.get_or_create(name="Empleado")

        # El cliente usa el sitio publico, no el panel de gestion.
        cliente.permissions.clear()

        # El empleado gestiona personas, empleados y pasajeros.
        # Coches, lineas y cocheras solo los puede ver.
        # Viajes: puede verlos y asignarles un coche.
        permisos = Permission.objects.filter(
            content_type__app_label="core",
            codename__in=[
                "add_empleado", "change_empleado", "delete_empleado",
                "view_empleado",
                "add_pasajero", "change_pasajero", "delete_pasajero",
                "view_pasajero",
                "view_coche", "view_linea", "view_cochera",
                "view_viaje", "change_viaje",
            ],
        )
        empleado.permissions.set(permisos)

        self.stdout.write(self.style.SUCCESS(
            "Grupos listos: Cliente y Empleado."
        ))
