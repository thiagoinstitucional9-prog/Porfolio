from django.urls import path

from . import views


urlpatterns = [ 
    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path("registro/",
        views.registro_view, 
        name="registro"
    ),

    path(
        "",
        views.inicio,
        name="inicio"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "crear-linea/",
        views.crear_linea,
        name="crear_linea"
    ),

    path(
        "eliminar-linea/<int:id>/",
        views.eliminar_linea,
        name="eliminar_linea"
    ),

    path(
        "crear-estacion/",
        views.crear_estacion,
        name="crear_estacion"
    ),

    path(
        "crear-tren/",
        views.crear_tren,
        name="crear_tren"
    ),

    path(
        "eliminar-tren/<int:id>/",
        views.eliminar_tren,
        name="eliminar_tren"
    ),

    path(
        "mover-tren/",
        views.mover_tren,
        name="mover_tren"
    ),
]