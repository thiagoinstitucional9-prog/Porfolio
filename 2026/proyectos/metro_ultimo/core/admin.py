from django.contrib import admin

from .models import (
    Beneficio, Ciudad, ClaseServicio, Coche, Cochera, Destino, Empleado,
    Horario, Linea, Pasajero, Persona, Promocion, Ruta, Tarifa, Viaje,
)


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(ClaseServicio)
class ClaseServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("hora", "clase")
    list_filter = ("clase",)


class TarifaInline(admin.TabularInline):
    model = Tarifa
    extra = 1


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ("origen", "destino", "minutos")
    list_filter = ("origen", "destino")
    search_fields = ("origen__nombre", "destino__nombre")
    inlines = (TarifaInline,)


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ("ruta", "clase", "precio")
    list_filter = ("clase",)


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ("fecha", "ruta", "horario", "coche", "precio", "asientos")
    list_filter = (
        "fecha", "ruta__origen", "ruta__destino", "horario__clase",
        "coche__cochera", "coche__linea",
    )
    date_hierarchy = "fecha"
    search_fields = (
        "ruta__origen__nombre", "ruta__destino__nombre", "coche__patente",
    )
    list_select_related = (
        "ruta__origen", "ruta__destino", "horario__clase", "coche",
    )


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "provincia", "desde", "origen", "orden")
    list_filter = ("provincia", "origen")
    search_fields = ("nombre", "provincia")


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "descuento", "orden")
    search_fields = ("titulo", "bajada")


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "icono", "orden")
    search_fields = ("titulo", "texto")


# --- Sistema de transporte ---

admin.site.register(Persona)
admin.site.register(Empleado)
admin.site.register(Pasajero)
admin.site.register(Linea)
admin.site.register(Cochera)


@admin.register(Coche)
class CocheAdmin(admin.ModelAdmin):
    list_display = ("patente", "modelo", "capacidad", "linea", "cochera")
    list_filter = ("linea", "cochera")
    search_fields = ("patente", "modelo")
