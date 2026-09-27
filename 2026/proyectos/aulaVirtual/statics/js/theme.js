const button = document.getElementById("theme-toggle");

button.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
});