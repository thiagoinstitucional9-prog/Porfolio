// Menú del celular: abre y cierra la navegación.
const boton = document.querySelector(".menu-toggle");
const nav = document.querySelector(".nav");

if (boton && nav) {
  boton.addEventListener("click", () => {
    const abierto = nav.classList.toggle("abierto");
    boton.setAttribute("aria-expanded", abierto ? "true" : "false");
  });
  nav.querySelectorAll("a").forEach((enlace) => {
    enlace.addEventListener("click", () => {
      nav.classList.remove("abierto");
      boton.setAttribute("aria-expanded", "false");
    });
  });
}

// La fecha de vuelta nunca puede ser anterior a la de ida.
const formularios = document.querySelectorAll("form.buscador");
formularios.forEach((form) => {
  const ida = form.querySelector("[name='fecha']");
  const vuelta = form.querySelector("[name='vuelta']");
  if (ida && vuelta) {
    ida.addEventListener("change", () => {
      vuelta.min = ida.value || "";
    });
  }
});
