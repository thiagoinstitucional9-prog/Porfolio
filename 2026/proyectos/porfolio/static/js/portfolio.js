// static/js/portfolio.js
// RESPONSABILIDAD DE ESTE ARCHIVO:
// Agregar pequenas interacciones con JavaScript:
// 1. Abrir el modal de login cuando el servidor lo pide.
// 2. Completar los modales de edicion con los datos del elemento elegido.
// 3. Pedir confirmacion antes de eliminar.

document.addEventListener("DOMContentLoaded", function () {
    abrirModalLoginSiHaceFalta();
    prepararModalesDeEdicion();
    prepararFormulariosDeEliminacion();
});


function abrirModalLoginSiHaceFalta() {
    const modalLogin = document.getElementById("modalLogin");

    if (!modalLogin) {
        return;
    }

    if (modalLogin.dataset.abrirModal === "true") {
        const modal = bootstrap.Modal.getOrCreateInstance(modalLogin);
        modal.show();
    }
}


function prepararModalesDeEdicion() {
    const modales = document.querySelectorAll(".modal-edicion");

    modales.forEach(function (modal) {
        modal.addEventListener("show.bs.modal", function (evento) {
            const boton = evento.relatedTarget;

            if (!boton) {
                return;
            }

            const formulario = modal.querySelector("form");

            if (!formulario) {
                return;
            }

            // Primero limpiamos el formulario para que no queden datos viejos.
            formulario.reset();

            // Cambiamos la direccion del formulario segun sea agregar o editar.
            if (boton.dataset.accion) {
                formulario.action = boton.dataset.accion;
            }

            // Cambiamos el titulo del modal.
            const titulo = modal.querySelector(".modal-title");

            if (titulo && boton.dataset.titulo) {
                titulo.textContent = boton.dataset.titulo;
            }

            // Si el boton trae datos, los copiamos a los campos.
            if (boton.dataset.registro) {
                completarCampos(formulario, boton.dataset.registro);
            }
        });
    });
}


function completarCampos(formulario, textoRegistro) {
    let registro = {};

    try {
        registro = JSON.parse(textoRegistro);
    } catch (error) {
        // Si el JSON tiene un error, dejamos el formulario vacio.
        return;
    }

    Object.keys(registro).forEach(function (nombreCampo) {
        const campo = formulario.elements[nombreCampo];

        if (campo) {
            campo.value = registro[nombreCampo];
        }
    });
}


function prepararFormulariosDeEliminacion() {
    const formularios = document.querySelectorAll("form[data-confirmar]");

    formularios.forEach(function (formulario) {
        formulario.addEventListener("submit", function (evento) {
            const mensaje = formulario.dataset.confirmar;

            if (!confirm(mensaje)) {
                evento.preventDefault();
            }
        });
    });
}
