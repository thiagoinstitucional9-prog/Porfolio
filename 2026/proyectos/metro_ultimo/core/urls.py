from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("buscar/", views.buscar, name="buscar"),
    path("comprar/<int:viaje_id>/", views.comprar, name="comprar"),
    path("pago/confirmado/", views.pago_confirmado, name="pago_confirmado"),
    path("ingresar/", views.ingresar, name="ingresar"),
    path("registrarse/", views.registrarse, name="registrarse"),
    path("salir/", views.salir, name="salir"),

    # Personas
    path("personas/", views.PersonaListView.as_view(), name="persona_lista"),
    path("personas/nueva/", views.PersonaCreateView.as_view(),
         name="persona_crear"),
    path("personas/<int:pk>/editar/", views.PersonaUpdateView.as_view(),
         name="persona_editar"),

    # Empleados
    path("empleados/", views.EmpleadoListView.as_view(),
         name="empleado_lista"),
    path("empleados/nuevo/", views.EmpleadoCreateView.as_view(),
         name="empleado_crear"),
    path("empleados/<int:pk>/editar/", views.EmpleadoUpdateView.as_view(),
         name="empleado_editar"),

    # Pasajeros
    path("pasajeros/", views.PasajeroListView.as_view(),
         name="pasajero_lista"),
    path("pasajeros/nuevo/", views.PasajeroCreateView.as_view(),
         name="pasajero_crear"),
    path("pasajeros/<int:pk>/editar/", views.PasajeroUpdateView.as_view(),
         name="pasajero_editar"),

    # Coches
    path("coches/", views.CocheListView.as_view(), name="coche_lista"),
    path("coches/nuevo/", views.CocheCreateView.as_view(),
         name="coche_crear"),
    path("coches/<int:pk>/editar/", views.CocheUpdateView.as_view(),
         name="coche_editar"),

    # Líneas
    path("lineas/", views.LineaListView.as_view(), name="linea_lista"),
    path("lineas/nueva/", views.LineaCreateView.as_view(),
         name="linea_crear"),
    path("lineas/<int:pk>/editar/", views.LineaUpdateView.as_view(),
         name="linea_editar"),

    # Cocheras
    path("cocheras/", views.CocheraListView.as_view(),
         name="cochera_lista"),
    path("cocheras/nueva/", views.CocheraCreateView.as_view(),
         name="cochera_crear"),
    path("cocheras/<int:pk>/editar/", views.CocheraUpdateView.as_view(),
         name="cochera_editar"),

    # Viajes
    path("viajes/", views.ViajeListView.as_view(), name="viaje_lista"),
    path("viajes/<int:pk>/asignar/", views.ViajeUpdateView.as_view(),
         name="viaje_asignar"),
]
