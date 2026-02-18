from django.shortcuts import render, get_object_or_404
from .models import DocumentoTransparencia
from .models import Pet
from .forms import CadastroAdotanteForm
from django.core.mail import send_mail
import requests # Comunicação com o Google
from django.contrib import messages # Manda mensagem de erro na tela
from django.conf import settings  # Acesso as chaves
from .models import ConfiguracaoGeral


def sobre(request):
    return render(request, 'sobre.html')


def contato(request):
    return render(request, 'contato.html')


# 1. Página "Capa" (Só visual + Botão)
def transp(request):
    return render(request, 'transparencia.html')


# 2. Página "Arquivo" (Com filtros)
def prestacao_contas(request):
    # --- LÓGICA DE FILTRO ---
    # Pegamos o que veio na URL (ex: ?ano=2025&mes=3)
    ano_filtro = request.GET.get('ano')
    mes_filtro = request.GET.get('mes')

    # Base dos documentos mensais
    docs_mensais = DocumentoTransparencia.objects.filter(categoria='MENSAL')

    # Se escolheu ano, filtra
    if ano_filtro:
        docs_mensais = docs_mensais.filter(data_publicacao__year=ano_filtro)
    
    # Se escolheu mês, filtra
    if mes_filtro:
        docs_mensais = docs_mensais.filter(data_publicacao__month=mes_filtro)

    # Ordena do mais recente para o mais antigo
    docs_mensais = docs_mensais.order_by('-data_publicacao')

    # Documentos anuais (geralmente não precisam de filtro de mês)
    docs_anuais = DocumentoTransparencia.objects.filter(categoria='ANUAL').order_by('-data_publicacao')

    # --- PARA POPULAR O SELECT DO HTML ---
    # Pega todos os anos disponíveis no banco para montar o <select>
    anos_disponiveis = DocumentoTransparencia.objects.dates('data_publicacao', 'year', order='DESC')

    return render(request, 'prestacao_contas.html', {
        'docs_mensais': docs_mensais,
        'docs_anuais': docs_anuais,
        'anos_disponiveis': anos_disponiveis,
        'ano_selecionado': ano_filtro, # Para manter o select marcado
        'mes_selecionado': mes_filtro,
    })


def lista_pets(request):
    # ANTES: .filter(status='DISPONIVEL')
    # AGORA: .filter(status_adocao='DISPONIVEL')
    
    pets = Pet.objects.filter(status_adocao='DISPONIVEL').prefetch_related('fotos')
    return render(request, 'adote.html', {'pets': pets})


def detalhes_pet(request, pet_id):
    # Busca o pet pelo ID. Se não existir (ex: ID 999), dá erro 404 automaticamente.
    pet = get_object_or_404(Pet, pk=pet_id)
    
    return render(request, 'detalhes_pet.html', {'pet': pet})


def cadastro_adotante(request, pet_id=None):
    pet_interesse = None
    
    if pet_id:
        pet_interesse = get_object_or_404(Pet, id=pet_id)

    if request.method == 'POST':
        form = CadastroAdotanteForm(request.POST)
        
        # === VALIDAÇÃO RECAPTCHA ===
        recaptcha_response = request.POST.get('g-recaptcha-response')
        
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        
        # Envia verificação para o servidor do Google
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
    
        if form.is_valid() and result['success']:
            
            # 1. Salva no Banco de Dados
            adotante = form.save()
            
          # 2. Monta o E-mail de Alerta
            assunto = f'Novo Interessado: {adotante.nome}'
            mensagem = f"""
            Olá equipe AMPA,
            
            Uma nova pessoa preencheu a ficha de interesse no site!
            
            --- DADOS DO ADOTANTE ---
            Nome: {adotante.nome}
            Telefone: {adotante.telefone}
            E-mail: {adotante.email}
            Endereço: {adotante.endereco}
            CPF: {adotante.cpf}
            """
            
            if pet_interesse:
                mensagem += f"\n\n--- INTERESSE NO PET ---\nNome: {pet_interesse.nome} (ID: {pet_interesse.id})"
            
            # === [INÍCIO DA ALTERAÇÃO] ===
            # Tenta buscar a configuração personalizada no banco de dados
            config = ConfiguracaoGeral.objects.first()
            
            if config:
                # Se a ONG configurou no admin, usa o e-mail dela
                email_destino = config.email_recebimento
            else:
                # Se não configurou, usa o padrão do arquivo .env (segurança)
                email_destino = settings.EMAIL_ONG_RECEBIMENTO
            # === [FIM DA ALTERAÇÃO] ===

            send_mail(
                subject=assunto,
                message=mensagem,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_destino], # <--- AQUI MUDOU para usar a variável
                fail_silently=False,
            )

            return render(request, 'cadastro_sucesso.html')
        
        else:
            # Se cair aqui, ou o form está errado ou é bot
            if not result['success']:
                messages.error(request, 'Erro no reCAPTCHA. Por favor, confirme que você não é um robô.')
    else:
        form = CadastroAdotanteForm()

    return render(request, 'cadastro_adotante.html', {
        'form': form,
        'pet': pet_interesse,
        'recaptcha_site_key': settings.RECAPTCHA_PUBLIC_KEY   #Passa a chave pública pro HTML
    })


def index(request):
    # Busca pets destaque e disponíveis
    pets_destaque = Pet.objects.filter(
        is_destaque=True, 
        status_adocao='DISPONIVEL'
    ).order_by('-id')[:3] #Limite máximo visual
    
    # Fallback (Se não tiver destaque, pega os 4 últimos)
    if not pets_destaque:
        pets_destaque = Pet.objects.filter(status_adocao='DISPONIVEL').order_by('-id')[:3]

    return render(request, 'index.html', {'pets_destaque': pets_destaque})