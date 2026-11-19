import uuid
from datetime import date

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from . import services
from .forms import (
    CocheForm, CocheraForm, EmpleadoForm, LineaForm, PagoSimuladoForm,
    PasajeroForm, PersonaForm, ViajeForm,
)
from .models import (
    Beneficio, Ciudad, Coche, Cochera, Destino, Empleado, Linea, Pasajero,
    Persona, Promocion, Viaje,
)
from .utils import fecha_legible, formato_miles


def _pasajeros(valor):
    """Convierte el valor del formulario en un número entre 1 y 9."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return 1
    return max(1, min(numero, 9))


def _fecha(valor):
    """Devuelve (fecha, es_valida). Sin fecha se considera válido."""
    if not valor:
        return None, True
    try:
        return date.fromisoformat(valor), True
    except (TypeError, ValueError):
        return None, False


def inicio(request):
    """Página principal: hero, buscador, destinos, promociones y beneficios."""
    contexto = {
        "hoy": date.today().isoformat(),
        "ciudades": Ciudad.objects.all(),
        "destinos": Destino.objects.select_related("origen"),
        "promociones": Promocion.objects.all(),
        "beneficios": Beneficio.objects.all(),
    }
    return render(request, "core/inicio.html", contexto)


def buscar(request):
    """Muestra las salidas guardadas en MySQL que coinciden con la búsqueda."""
    origen = request.GET.get("origen", "").strip()
    destino = request.GET.get("destino", "").strip()
    fecha_txt = request.GET.get("fecha", "").strip()
    pasajeros = _pasajeros(request.GET.get("pasajeros"))

    fecha, fecha_valida = _fecha(fecha_txt)

    if fecha_valida:
        services.asegurar_viajes()
        viajes = list(services.buscar_viajes(origen, destino, fecha))
    else:
        viajes = []

    # Se agrega el total por la cantidad de pasajeros elegida.
    for viaje in viajes:
        viaje.total_txt = formato_miles(viaje.precio * pasajeros)

    contexto = {
        "hoy": date.today().isoformat(),
        "ciudades": Ciudad.objects.all(),
        "origen": origen,
        "destino": destino,
        "fecha": fecha_txt,
        "fecha_legible": fecha_legible(fecha_txt),
        "pasajeros": pasajeros,
        "viajes": viajes,
        "destinos": Destino.objects.select_related("origen"),
    }
    return render(request, "core/buscar.html", contexto)


def comprar(request, viaje_id):
    """Resumen del viaje y checkout simulado.

    No se contacta ninguna pasarela de pago ni se guardan datos de tarjeta.
    Las tarjetas terminadas en 0000 se rechazan para poder probar el flujo
    de error; el resto se considera aprobado.
    """
    viaje = get_object_or_404(
        Viaje.objects.select_related(
            "ruta__origen", "ruta__destino", "horario__clase",
        ),
        pk=viaje_id,
    )

    pasajeros = _pasajeros(
        request.POST.get("pasajeros") or request.GET.get("pasajeros")
    )
    total = viaje.precio * pasajeros
    total_txt = formato_miles(total)
    form = PagoSimuladoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        if pasajeros > viaje.asientos:
            form.add_error(
                None,
                "No hay suficientes butacas disponibles para esa cantidad "
                "de pasajeros.",
            )
        elif form.pago_aprobado():
            cuotas = int(form.cleaned_data["cuotas"])
            request.session["pago_simulado"] = {
                "viaje_id": viaje.pk,
                "pasajeros": pasajeros,
                "total_txt": total_txt,
                "codigo": f"METRO-{uuid.uuid4().hex[:8].upper()}",
                "tarjeta": form.tarjeta_enmascarada(),
                "cuotas": cuotas,
                "cuota_txt": formato_miles(round(total / cuotas)),
                "email": form.cleaned_data.get("email", ""),
            }
            viaje.asientos -= pasajeros
            viaje.save(update_fields=["asientos"])
            return redirect("core:pago_confirmado")
        else:
            form.add_error(
                None,
                "Pago rechazado por el banco simulado. "
                "Probá con otra tarjeta.",
            )

    contexto = {
        "viaje": viaje,
        "pasajeros": pasajeros,
        "total_txt": total_txt,
        "origen": viaje.origen,
        "destino": viaje.destino,
        "fecha": viaje.fecha_iso,
        "form": form,
    }
    return render(request, "core/comprar.html", contexto)


def pago_confirmado(request):
    """Muestra el comprobante del último pago simulado aprobado."""
    datos = request.session.pop("pago_simulado", None)
    if not datos:
        return redirect("core:inicio")

    viaje_id = datos.pop("viaje_id")
    viaje = get_object_or_404(
        Viaje.objects.select_related(
            "ruta__origen", "ruta__destino", "horario__clase",
        ),
        pk=viaje_id,
    )
    contexto = {"viaje": viaje, **datos}
    return render(request, "core/pago_confirmado.html", contexto)


def ingresar(request):
    """Inicio de sesión con el formulario que ya trae Django."""
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("core:inicio")
    return render(request, "core/ingresar.html", {"form": form})


def registrarse(request):
    """Crea un usuario nuevo y lo deja con la sesión iniciada."""
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        grupo_cliente, _ = Group.objects.get_or_create(name="Cliente")
        usuario.groups.add(grupo_cliente)
        login(request, usuario)
        return redirect("core:inicio")
    return render(request, "core/registrarse.html", {"form": form})


def salir(request):
    """Cierra la sesión y vuelve a la página principal."""
    logout(request)
    return redirect("core:inicio")


# ------------------------------------------------------------------
# Sistema de transporte: listados y formularios con permisos
# ------------------------------------------------------------------

class PermisoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Pide login. Si ya está logueado pero no tiene permiso, da 403."""

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class ListaBase(PermisoMixin, ListView):
    """Listado simple. Pide estar logueado y tener permiso de ver."""

    template_name = "core/lista.html"
    context_object_name = "objetos"
    titulo = ""
    url_crear = ""
    url_editar = ""
    permiso_agregar = ""
    permiso_editar = ""

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = self.titulo
        contexto["url_crear"] = self.url_crear
        contexto["url_editar"] = self.url_editar
        contexto["puede_agregar"] = bool(
            self.permiso_agregar
            and self.request.user.has_perm(self.permiso_agregar)
        )
        contexto["puede_editar"] = bool(
            self.permiso_editar
            and self.request.user.has_perm(self.permiso_editar)
        )
        return contexto


class CrearBase(PermisoMixin, CreateView):
    """Formulario para crear. Pide estar logueado y tener permiso de agregar."""

    template_name = "core/formulario.html"
    titulo = ""
    url_volver = ""

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = self.titulo
        contexto["url_volver"] = self.url_volver
        return contexto


class EditarBase(PermisoMixin, UpdateView):
    """Formulario para editar. Pide estar logueado y tener permiso de cambiar."""

    template_name = "core/formulario.html"
    titulo = ""
    url_volver = ""

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = self.titulo
        contexto["url_volver"] = self.url_volver
        return contexto


# --- Personas ---

class PersonaListView(ListaBase):
    model = Persona
    permission_required = "core.view_persona"
    titulo = "Personas"
    url_crear = reverse_lazy("core:persona_crear")
    url_editar = "core:persona_editar"
    permiso_agregar = "core.add_persona"
    permiso_editar = "core.change_persona"


class PersonaCreateView(CrearBase):
    model = Persona
    form_class = PersonaForm
    permission_required = "core.add_persona"
    titulo = "Nueva persona"
    url_volver = reverse_lazy("core:persona_lista")
    success_url = reverse_lazy("core:persona_lista")


class PersonaUpdateView(EditarBase):
    model = Persona
    form_class = PersonaForm
    permission_required = "core.change_persona"
    titulo = "Editar persona"
    url_volver = reverse_lazy("core:persona_lista")
    success_url = reverse_lazy("core:persona_lista")


# --- Empleados ---

class EmpleadoListView(ListaBase):
    model = Empleado
    permission_required = "core.view_empleado"
    titulo = "Empleados"
    url_crear = reverse_lazy("core:empleado_crear")
    url_editar = "core:empleado_editar"
    permiso_agregar = "core.add_empleado"
    permiso_editar = "core.change_empleado"


class EmpleadoCreateView(CrearBase):
    model = Empleado
    form_class = EmpleadoForm
    permission_required = "core.add_empleado"
    titulo = "Nuevo empleado"
    url_volver = reverse_lazy("core:empleado_lista")
    success_url = reverse_lazy("core:empleado_lista")


class EmpleadoUpdateView(EditarBase):
    model = Empleado
    form_class = EmpleadoForm
    permission_required = "core.change_empleado"
    titulo = "Editar empleado"
    url_volver = reverse_lazy("core:empleado_lista")
    success_url = reverse_lazy("core:empleado_lista")


# --- Pasajeros ---

class PasajeroListView(ListaBase):
    model = Pasajero
    permission_required = "core.view_pasajero"
    titulo = "Pasajeros"
    url_crear = reverse_lazy("core:pasajero_crear")
    url_editar = "core:pasajero_editar"
    permiso_agregar = "core.add_pasajero"
    permiso_editar = "core.change_pasajero"


class PasajeroCreateView(CrearBase):
    model = Pasajero
    form_class = PasajeroForm
    permission_required = "core.add_pasajero"
    titulo = "Nuevo pasajero"
    url_volver = reverse_lazy("core:pasajero_lista")
    success_url = reverse_lazy("core:pasajero_lista")


class PasajeroUpdateView(EditarBase):
    model = Pasajero
    form_class = PasajeroForm
    permission_required = "core.change_pasajero"
    titulo = "Editar pasajero"
    url_volver = reverse_lazy("core:pasajero_lista")
    success_url = reverse_lazy("core:pasajero_lista")


# --- Coches ---

class CocheListView(ListaBase):
    model = Coche
    permission_required = "core.view_coche"
    template_name = "core/coche_lista.html"
    titulo = "Coches"
    url_crear = reverse_lazy("core:coche_crear")
    url_editar = "core:coche_editar"
    permiso_agregar = "core.add_coche"
    permiso_editar = "core.change_coche"


class CocheCreateView(CrearBase):
    model = Coche
    form_class = CocheForm
    permission_required = "core.add_coche"
    titulo = "Nuevo coche"
    url_volver = reverse_lazy("core:coche_lista")
    success_url = reverse_lazy("core:coche_lista")


class CocheUpdateView(EditarBase):
    model = Coche
    form_class = CocheForm
    permission_required = "core.change_coche"
    titulo = "Editar coche"
    url_volver = reverse_lazy("core:coche_lista")
    success_url = reverse_lazy("core:coche_lista")


# --- Líneas ---

class LineaListView(ListaBase):
    model = Linea
    permission_required = "core.view_linea"
    titulo = "Líneas"
    url_crear = reverse_lazy("core:linea_crear")
    url_editar = "core:linea_editar"
    permiso_agregar = "core.add_linea"
    permiso_editar = "core.change_linea"


class LineaCreateView(CrearBase):
    model = Linea
    form_class = LineaForm
    permission_required = "core.add_linea"
    titulo = "Nueva línea"
    url_volver = reverse_lazy("core:linea_lista")
    success_url = reverse_lazy("core:linea_lista")


class LineaUpdateView(EditarBase):
    model = Linea
    form_class = LineaForm
    permission_required = "core.change_linea"
    titulo = "Editar línea"
    url_volver = reverse_lazy("core:linea_lista")
    success_url = reverse_lazy("core:linea_lista")


# --- Cocheras ---

class CocheraListView(ListaBase):
    model = Cochera
    permission_required = "core.view_cochera"
    template_name = "core/cochera_lista.html"
    titulo = "Cocheras"
    url_crear = reverse_lazy("core:cochera_crear")
    url_editar = "core:cochera_editar"
    permiso_agregar = "core.add_cochera"
    permiso_editar = "core.change_cochera"


class CocheraCreateView(CrearBase):
    model = Cochera
    form_class = CocheraForm
    permission_required = "core.add_cochera"
    titulo = "Nueva cochera"
    url_volver = reverse_lazy("core:cochera_lista")
    success_url = reverse_lazy("core:cochera_lista")


class CocheraUpdateView(EditarBase):
    model = Cochera
    form_class = CocheraForm
    permission_required = "core.change_cochera"
    titulo = "Editar cochera"
    url_volver = reverse_lazy("core:cochera_lista")
    success_url = reverse_lazy("core:cochera_lista")


# --- Viajes ---

class ViajeListView(ListaBase):
    model = Viaje
    permission_required = "core.view_viaje"
    template_name = "core/viaje_lista.html"
    titulo = "Viajes"
    url_crear = ""
    url_editar = "core:viaje_asignar"
    permiso_agregar = ""
    permiso_editar = "core.change_viaje"

    def get_queryset(self):
        return Viaje.objects.select_related(
            "ruta__origen", "ruta__destino", "horario__clase", "coche",
        )


class ViajeUpdateView(EditarBase):
    model = Viaje
    form_class = ViajeForm
    permission_required = "core.change_viaje"
    titulo = "Asignar coche al viaje"
    url_volver = reverse_lazy("core:viaje_lista")
    success_url = reverse_lazy("core:viaje_lista")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["descripcion"] = (
            f"{self.object.fecha:%d/%m/%Y} · {self.object.ruta} · "
            f"{self.object.hora} hs"
        )
        return contexto
