from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("buscar/", views.buscar, name="buscar"),
    path("comprar/<int:viaje_id>/", views.comprar, name="comprar"),
    path("ingresar/", views.ingresar, name="ingresar"),
    path("registrarse/", views.registrarse, name="registrarse"),
    path("salir/", views.salir, name="salir"),
]
