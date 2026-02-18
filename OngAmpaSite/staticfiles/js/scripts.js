// static/js/scripts.js

document.addEventListener("DOMContentLoaded", function () {
  // === Lógica da Navbar Escondida ===
  let lastScrollTop = 0;
  const navbar = document.getElementById("navbar");

  if (navbar) {
    // Verifica se a navbar existe para evitar erros
    window.addEventListener("scroll", function () {
      const scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;

      if (scrollTop > lastScrollTop) {
        // Rolando para baixo -> Esconde
        navbar.style.top = "-105px";
      } else {
        // Rolando para cima -> Mostra
        navbar.style.top = "0";
      }
      lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    });
  }
});
