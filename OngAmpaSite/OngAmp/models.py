from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone  # Importação correta para datas no Django
from .validators import validar_imagem, validar_pdf
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver

# ==============================================================================
# MODELO: PET
# ==============================================================================
class Pet(models.Model):

    class Sexo(models.TextChoices):
        FEMININO = 'F', 'Fêmea'
        MASCULINO = 'M', 'Macho'

    class CategoriaPet(models.TextChoices):
        CACHORRO = 'C', 'Cachorro'
        GATO = 'G', 'Gato'

    class Idade(models.TextChoices):
        FILHOTE = 'FILHOTE', 'Filhote'
        ADULTO = 'ADULTO', 'Adulto'

    class Porte(models.TextChoices):
        PEQUENO = 'P', 'Pequeno'
        MEDIO = 'M', 'Médio'
        GRANDE = 'G', 'Grande'

    class IsCastrado(models.TextChoices):
        CASTRADO = 'C', 'Castrado'
        NAO_CASTRADO = 'NC', 'Não Castrado'

    class IsCondicaoEspecial(models.TextChoices):
        SIM = 'S', 'Sim'
        NAO = 'N', 'Não'

    class StatusAdocao(models.TextChoices):
        DISPONIVEL = 'DISPONIVEL', 'Disponível para Adoção'
        EM_PROCESSO = 'EM_PROCESSO', 'Em Processo de Adoção'
        ADOTADO = 'ADOTADO', 'Adotado'

    # Campos de Texto
    nome = models.CharField(
        max_length=50, # Aumentado para segurança
        blank=False,
        verbose_name="Nome do Pet"
        # Removemos o validador estrito para permitir nomes como "Bolinha 2"
    )

    raca = models.CharField(
        max_length=50,
        default="SRD", # Já vem preenchido como Vira-lata para facilitar
        verbose_name="Raça",
        help_text="Ex: Labrador, Siamês, ou mantenha 'SRD' para Vira-lata."
    )
    
    coloracao = models.CharField(
        max_length=30, 
        blank=False,
        verbose_name="Coloração"
    )
    
    descricao = models.TextField(
        verbose_name="História do Pet", 
        blank=False,
        help_text="Conte um pouco sobre o resgate e a personalidade do animal."
    )

    # Campos de Escolha (Choices)
    sexo = models.CharField(
        max_length=1,
        choices=Sexo.choices,
        default=Sexo.MASCULINO,
    )

    categoria_pet = models.CharField(
        max_length=1,
        choices=CategoriaPet.choices,
        default=CategoriaPet.CACHORRO,
        db_index=True  # Indexado para filtrar rápido (Só Cães ou Só Gatos)
    )

    idade = models.CharField(
        max_length=8,
        choices=Idade.choices,
        default=Idade.ADULTO,
    )

    porte = models.CharField(
        max_length=1,
        choices=Porte.choices,
        default=Porte.MEDIO,
    )

    is_castrado = models.CharField(
        max_length=2,
        choices=IsCastrado.choices,
        default=IsCastrado.CASTRADO,
        verbose_name="É castrado?"
    )

    is_condicao_especial = models.CharField(
        max_length=1,
        choices=IsCondicaoEspecial.choices,
        default=IsCondicaoEspecial.NAO,
        verbose_name="Tem condição especial?"
    )

    is_destaque = models.BooleanField(
        default=False,
        verbose_name="Destaque na Home?",
        help_text="Marque se quiser que este pet apareça na página inicial."
    )

    # Controle
    status_adocao = models.CharField(
        max_length=20,
        choices=StatusAdocao.choices,
        default=StatusAdocao.DISPONIVEL,
        verbose_name="Status de Adoção",
        db_index=True # Ajuda a filtrar rápido no banco
    )

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_pet_display()})"

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets (Animais)"

    def clean(self):
        # Se o voluntário está tentando marcar este pet como destaque
        if self.is_destaque:
            # Conta quantos JÁ existem como destaque (excluindo este próprio, se for uma edição)
            qtd_destaques = Pet.objects.filter(is_destaque=True).exclude(id=self.id).count()
            
            # Se já tiver 4 ou mais, BLOQUEIA
            if qtd_destaques >= 4:
                raise ValidationError({
                    'is_destaque': 'O limite é de 4 destaques na Home. Desmarque outro animal antes de marcar este.'
                })

    # Garante que a validação rode também no Admin
    def save(self, *args, **kwargs):
        self.full_clean() # Chama o clean() antes de salvar
        super().save(*args, **kwargs)


# ==============================================================================
# MODELO: FOTOS DO PET
# ==============================================================================
class FotoPet(models.Model):
    pet = models.ForeignKey(
        Pet, 
        related_name='fotos', 
        on_delete=models.CASCADE, # Se apagar o Pet, as fotos somem (Correto)
        verbose_name="Pet"
    )
    imagem = models.ImageField(
        upload_to="img_pets/", 
        validators=[validar_imagem],
        verbose_name="Imagem"
    )
    
    def __str__(self):
        return f"Foto de {self.pet.nome}"

    class Meta:
        verbose_name = "Foto do Pet"
        verbose_name_plural = "Fotos dos Pets"


# ==============================================================================
# MODELO: ADOTANTE
# ==============================================================================
class Adotante(models.Model):
    nome = models.CharField(
        max_length=100, # Aumentado de 30 para 100 (nomes completos são longos)
        verbose_name="Nome Completo"
    )
    
    cpf = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="CPF (Apenas números)",
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='O CPF deve conter apenas números (11 dígitos).'
            )
        ]
    )
    
    telefone = models.CharField(
        max_length=20, # Aumentado para permitir formatos internacionais ou máscaras
        verbose_name="WhatsApp/Telefone"
    )
    
    email = models.EmailField(
        max_length=100, 
        verbose_name="E-mail",
        unique=True # É bom garantir que o e-mail não se repita
    )
    
    endereco = models.CharField(
        max_length=255, 
        verbose_name="Endereço Completo", 
        blank=True
    )
    
    data_cadastro = models.DateTimeField(auto_now_add=True) # Bom para saber quando chegou

    def __str__(self):
        return f"{self.nome} - {self.cpf}"

    class Meta:
        verbose_name = "Adotante"
        verbose_name_plural = "Adotantes"


# ==============================================================================
# MODELO: VOLUNTÁRIO
# ==============================================================================
class Voluntario(models.Model):
    nome = models.CharField(
        max_length=100, # Aumentado de 30 para 100
        verbose_name="Nome do Voluntário"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo?")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Voluntário"
        verbose_name_plural = "Voluntários"


# ==============================================================================
# MODELO: ADOÇÃO (REGISTRO HISTÓRICO)
# ==============================================================================
class Adocao(models.Model):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT, 
        related_name="adocoes"
    )

    #Muda o status do pet ao salvar a adoção
    def clean(self):
        if not self.pk and self.pet.status_adocao == Pet.StatusAdocao.ADOTADO:
            raise ValidationError(f"Erro: O animal '{self.pet.nome}' já consta como ADOTADO no sistema.")
        
    def save(self, *args, **kwargs):
        # Primeiro, executa a validação acima
        self.full_clean()
        
        # Salva o registro de adoção
        super().save(*args, **kwargs)
        
        # atualiza o Pet para ADOTADO
        if self.pet.status_adocao != Pet.StatusAdocao.ADOTADO:
            self.pet.status_adocao = Pet.StatusAdocao.ADOTADO
            self.pet.save()

    adotante = models.ForeignKey(
        Adotante,
        on_delete=models.PROTECT, 
        related_name="adocoes"
    )

    voluntario = models.ForeignKey(
        Voluntario,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name="adocoes",
        verbose_name="Voluntário Responsável"
    )

    data = models.DateTimeField(
        default=timezone.now, # Usa timezone correto
        verbose_name="Data da Adoção"
    )

    def __str__(self):
        return f"Adoção de {self.pet.nome} por {self.adotante.nome}"
    
    class Meta:
        verbose_name = "Registro de Adoção"
        verbose_name_plural = "Registro de Adoções"


class ConfiguracaoGeral(models.Model):
    email_recebimento = models.EmailField(
        verbose_name="E-mail que recebe as adoções",
        help_text="Para onde devem ir os alertas de novos interessados?",
        default="ampa.mirassol@hotmail.com"
    )

    def __str__(self):
        return "Configuração de E-mail"

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configurações do Site"

    # Truque para garantir que só exista 1 configuração no banco
    def save(self, *args, **kwargs):
        if not self.pk and ConfiguracaoGeral.objects.exists():
            # Se tentar criar uma segunda, a gente bloqueia ou atualiza a primeira
             raise ValidationError('Só pode existir uma configuração geral no site.')
        return super(ConfiguracaoGeral, self).save(*args, **kwargs)
    

# ==============================================================================
# MODELO: TRANSPARÊNCIA
# ==============================================================================
class DocumentoTransparencia(models.Model):
    CATEGORIAS = [
        ('MENSAL', 'Prestação de Contas Mensal'),
        ('ANUAL', 'Prestação de Contas Anual'),
        ('ESTATUTO', 'Estatuto e Atas'),
        ('ATIVIDADES', 'Relatórios de Atividades'),
        ('CERTIDOES', 'Certidões Negativas'),
        ('OUTROS', 'Outros Documentos'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título do Documento")
    arquivo = models.FileField(
        upload_to='transparencia_pdfs/', 
        verbose_name="Arquivo PDF",
        validators=[validar_pdf],
        help_text="Apenas arquivos .pdf são permitidos"
    )

    categoria = models.CharField(
        max_length=20, 
        choices=CATEGORIAS, 
        default='MENSAL',
        db_index=True # Indexado para filtrar rápido nas views
    )
    
    data_publicacao = models.DateField(
        default=timezone.now, 
        verbose_name="Data de Referência"
    )

    def __str__(self):
        return f"{self.titulo} ({self.get_categoria_display()})"

    class Meta:
        verbose_name = "Documento de Transparência"
        verbose_name_plural = "Transparência"
        ordering = ['-data_publicacao']

# ==============================================================================
# SINAIS (GATILHOS AUTOMÁTICOS)
# ==============================================================================
@receiver(post_delete, sender=Adocao)
def reverter_status_pet_ao_excluir_adocao(sender, instance, **kwargs):
    pet = instance.pet
    # Se o pet estava ADOTADO e a adoção foi excluída, volta pra DISPONIVEL
    if pet.status_adocao == Pet.StatusAdocao.ADOTADO:
        pet.status_adocao = Pet.StatusAdocao.DISPONIVEL
        pet.save()