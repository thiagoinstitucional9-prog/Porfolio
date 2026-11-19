// static/js/arrastrar_orden.js
// RESPONSABILIDAD DE ESTE ARCHIVO:
// Permitir arrastrar las tarjetas con el mouse para cambiar su orden.
//
// Cuando el usuario suelta una tarjeta, juntamos los ids en el orden nuevo
// y mandamos un formulario POST normal (con su token CSRF) a Flask.
// No usamos librerías nuevas: solamente JavaScript básico del navegador.

document.addEventListener("DOMContentLoaded", function () {
    prepararListasArrastrables();
});


function prepararListasArrastrables() {
    // Solamente trabajamos con las listas que tienen data-lista-orden.
    // Ese atributo se pone en index.html cuando hay una sesión iniciada.
    const listas = document.querySelectorAll("[data-lista-orden]");

    listas.forEach(function (lista) {
        prepararUnaLista(lista);
    });
}


function prepararUnaLista(lista) {
    let tarjetaArrastrada = null;
    const tarjetas = lista.querySelectorAll(".tarjeta-arrastrable");

    tarjetas.forEach(function (tarjeta) {
        tarjeta.addEventListener("dragstart", function (evento) {
            // Si el usuario empieza el arrastre en un botón, enlace o formulario,
            // dejamos que el botón siga funcionando como siempre.
            if (evento.target.closest("button, a, form")) {
                evento.preventDefault();
                return;
            }

            tarjetaArrastrada = tarjeta;
            tarjeta.classList.add("arrastrando");

            // Estas dos líneas ayudan a que el arrastre funcione en todos
            // los navegadores, inclusive Firefox.
            evento.dataTransfer.effectAllowed = "move";
            evento.dataTransfer.setData("text/plain", tarjeta.dataset.id);
        });

        tarjeta.addEventListener("dragend", function () {
            tarjeta.classList.remove("arrastrando");
            tarjetaArrastrada = null;

            // Recién acá guardamos, porque ya se terminó de mover la tarjeta.
            guardarNuevoOrden(lista);
        });
    });

    lista.addEventListener("dragover", function (evento) {
        // Sin preventDefault el navegador no deja soltar nada adentro.
        evento.preventDefault();
    });

    lista.addEventListener("drop", function (evento) {
        evento.preventDefault();

        const tarjetaDestino = evento.target.closest(".tarjeta-arrastrable");

        if (tarjetaArrastrada === null || tarjetaDestino === null) {
            return;
        }

        if (tarjetaArrastrada === tarjetaDestino) {
            return;
        }

        // Miramos si el mouse está arriba o abajo de la mitad de la tarjeta
        // destino. Así sabemos si ponemos la tarjeta antes o después.
        const rectangulo = tarjetaDestino.getBoundingClientRect();
        const mitad = rectangulo.top + rectangulo.height / 2;

        if (evento.clientY < mitad) {
            lista.insertBefore(tarjetaArrastrada, tarjetaDestino);
        } else {
            lista.insertBefore(tarjetaArrastrada, tarjetaDestino.nextSibling);
        }
    });
}


function guardarNuevoOrden(lista) {
    const tipoDeLista = lista.dataset.listaOrden;
    const identificadores = [];

    // Recorremos la lista en el orden que quedó después de arrastrar.
    lista.querySelectorAll(".tarjeta-arrastrable").forEach(function (tarjeta) {
        identificadores.push(tarjeta.dataset.id);
    });

    const formulario = document.getElementById("formulario-orden");
    const campoTipo = document.getElementById("campo-tipo-orden");
    const campoIds = document.getElementById("campo-ids-orden");

    if (!formulario || !campoTipo || !campoIds) {
        return;
    }

    campoTipo.value = tipoDeLista;
    campoIds.value = identificadores.join(",");

    // Enviamos un POST como los demás formularios, con su token CSRF.
    formulario.submit();
}
