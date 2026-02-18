document.addEventListener("DOMContentLoaded", function () {
    const sliderContainer = document.querySelector(".parceiros-container");

    if (!sliderContainer) return;

    // === 1. CLONAGEM PARA GARANTIR O LOOP ===
    const items = Array.from(sliderContainer.children);
    const screenWidth = window.innerWidth;
    let currentContentWidth = sliderContainer.scrollWidth;

    // Clona até preencher pelo menos 3x a tela (garante scroll infinito suave)
    while (currentContentWidth < screenWidth * 3) {
        items.forEach((item) => {
            const clone = item.cloneNode(true);
            sliderContainer.appendChild(clone);
        });
        currentContentWidth = sliderContainer.scrollWidth;
    }

    // === 2. VARIÁVEIS DE CONTROLE ===
    // Velocidade: 1 é padrão (60fps). 0.5 é metade da velocidade.
    // Como usamos requestAnimationFrame, isso roda a cada frame do monitor.
    const scrollSpeed = 1; 
    
    // Usamos uma variável separada para guardar a posição exata (com decimais)
    // Isso evita o problema de arredondamento do navegador
    let preciseScrollPosition = 0; 
    
    // Calcula o ponto de reset (largura do primeiro conjunto original)
    let firstSetWidth = 0;
    items.forEach(item => {
        // OffsetWidth pega largura + padding + borda. Somamos 60 do gap.
        firstSetWidth += item.offsetWidth + 60; 
    });

    let animationId; // Para poder pausar e retomar

    // === 3. A FUNÇÃO DE ANIMAÇÃO (O SEGREDO DO FPS) ===
    function animate() {
        // Incrementa a posição
        preciseScrollPosition += scrollSpeed;

        // Verifica o Reset (Loop Infinito)
        if (preciseScrollPosition >= firstSetWidth) {
            // Subtrai a largura do conjunto, mantendo a fluidez sem "pulo" visual
            preciseScrollPosition -= firstSetWidth;
        }

        // Aplica o movimento
        sliderContainer.scrollLeft = preciseScrollPosition;

        // Chama o próximo quadro (Sincronizado com o Monitor)
        animationId = requestAnimationFrame(animate);
    }

    // === 4. CONTROLES DE MOUSE ===
    function stopScroll() {
        cancelAnimationFrame(animationId);
    }

    function startScroll() {
        // Evita criar múltiplos loops se o usuário passar o mouse rápido demais
        cancelAnimationFrame(animationId);
        animationId = requestAnimationFrame(animate);
    }

    sliderContainer.addEventListener("mouseenter", stopScroll);
    sliderContainer.addEventListener("mouseleave", startScroll);

    // Inicia a animação
    startScroll();

    // Recalcula se a janela mudar de tamanho
    window.addEventListener('resize', () => {
        // Recalcula larguras se necessário (opcional para performance extrema)
        // firstSetWidth geralmente não muda com resize a menos que o CSS mude tamanhos
    });
});