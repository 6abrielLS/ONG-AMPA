// índice da foto (0, 1, 2...)
let indiceAtual = 0;

// Pega todas as miniaturas assim que a página carrega
const miniaturas = document.querySelectorAll(".miniatura");
const destaque = document.getElementById("imgDestaque");

function trocarFoto(elemento, novoIndice) {
  destaque.src = elemento.src;

  indiceAtual = novoIndice;

  atualizarClasseAtiva();
}
function mudarSlide(direcao) {
  if (miniaturas.length === 0) return;
  indiceAtual += direcao;
  if (indiceAtual >= miniaturas.length) {
    indiceAtual = 0;
  }
  if (indiceAtual < 0) {
    indiceAtual = miniaturas.length - 1;
  }
  const novaMiniatura = miniaturas[indiceAtual];
  destaque.src = novaMiniatura.src;
  atualizarClasseAtiva();
}

function atualizarClasseAtiva() {
  miniaturas.forEach((min) => min.classList.remove("ativa"));

  miniaturas[indiceAtual].classList.add("ativa");

  miniaturas[indiceAtual].scrollIntoView({
    behavior: "smooth",
    block: "nearest",
    inline: "center",
  });
}
