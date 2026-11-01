from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("buscar/", views.buscar, name="buscar"),
    path("comprar/<int:viaje_id>/", views.comprar, name="comprar"),
]
