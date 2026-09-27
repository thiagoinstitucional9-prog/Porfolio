from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import Linea, Estacion, Tren




def registro_view(request):

    if request.method == "POST":

        usuario = request.POST["usuario"]
        password = request.POST["password"]

        if usuario != "" and password != "":

            usuario_existe = User.objects.filter(
                username=usuario
            ).exists()

            if usuario_existe == False:

                User.objects.create_user(
                    username=usuario,
                    password=password
                )

                return redirect("login")

        return render(request, "registro.html", {
            "error": "El usuario ya existe o los datos estan vacios"
        })

    return render(request, "registro.html")




def login_view(request):

    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":

        usuario = request.POST["usuario"]
        password = request.POST["password"]

        usuario_valido = authenticate(
            request,
            username=usuario,
            password=password
        )

        if usuario_valido is not None:


            login(request, usuario_valido)

            return redirect("inicio")

        else:

            return render(request, "login.html", {
                "error": "Usuario o contraseña incorrectos"
            })

    return render(request, "login.html")



def inicio(request):

    
    lineas = Linea.objects.all()
    trenes = Tren.objects.all()

    datos = {
        "lineas": lineas,
        "trenes": trenes
    }

    return render(request, "metro.html", datos)



def crear_linea(request):

    
    if request.method == "POST":

        nombre = request.POST["nombre"]

        if nombre != "":

            Linea.objects.create(
                nombre=nombre
            )

    return redirect("inicio")



def eliminar_linea(request, id):

    
    linea = Linea.objects.get(id=id)

    linea.delete()

    return redirect("inicio")



def crear_estacion(request):

    
    if request.method == "POST":

        nombre = request.POST["nombre"]
        accesos = request.POST["accesos"]
        linea_id = request.POST["linea"]

        linea = Linea.objects.get(id=linea_id)

        Estacion.objects.create(
            nombre=nombre,
            accesos=accesos,
            linea=linea
        )

    return redirect("inicio")



def crear_tren(request):

    
    if request.method == "POST":

        id_tren = request.POST["id_tren"]

        if id_tren != "":

            Tren.objects.create(
                id_tren=id_tren
            )

    return redirect("inicio")



def eliminar_tren(request, id):

    
    tren = Tren.objects.get(id=id)

    tren.delete()

    return redirect("inicio")



def mover_tren(request):

    
    if request.method == "POST":

        tren_id = request.POST["tren"]
        destino = request.POST["destino"]

        tren = Tren.objects.get(id=tren_id)

        if destino == "NINGUNA":

            tren.linea = None

        else:

            linea = Linea.objects.get(id=destino)

            tren.linea = linea

        tren.save()

    return redirect("inicio")



def logout_view(request):

    logout(request)

    return redirect("login")

