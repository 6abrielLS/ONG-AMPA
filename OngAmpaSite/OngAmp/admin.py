from django.contrib import admin
from .models import (
    Pet, 
    FotoPet, 
    Adotante, 
    Voluntario, 
    Adocao, 
    DocumentoTransparencia
)


class FotoPetInline(admin.TabularInline):
    model = FotoPet
    extra = 1  


class PetAdmin(admin.ModelAdmin):
  
    list_display = ('nome', 'categoria_pet', 'sexo', 'porte', 'status_adocao', 'is_destaque')
    
    # Filtros na barra lateral direita
    list_filter = ('status_adocao', 'is_destaque', 'categoria_pet', 'sexo')
    
    # Barra de pesquisa (Busca por nome ou descrição)
    search_fields = ('nome', 'descricao')
    
    # editar o status de adoção direto na lista 
    list_editable = ('status_adocao', 'is_destaque')
    
    inlines = [FotoPetInline]
    
    # Paginação (se tiver muitos animais)
    list_per_page = 20


class AdotanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'data_cadastro')
    search_fields = ('nome', 'cpf', 'email') #Campo de busca
    list_filter = ('data_cadastro',) #Filtro por data de cadastro
    readonly_fields = ('data_cadastro',) # Garante que ninguém altere a data de cadastro manualmente

    # Organiza os dados sensíveis dentro do formulário de detalhe
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'cpf')
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'endereco')
        }),
        ('Sistema', {
            'fields': ('data_cadastro',),
            'classes': ('collapse',) # Esconde visualmente para não poluir
        }),
    )



class VoluntarioAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('pet', 'adotante', 'voluntario', 'data')
    list_filter = ('data',)
    search_fields = ('pet__nome', 'adotante__nome', 'adotante__cpf')
    readonly_fields = ('data',)


class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'data_publicacao')
    list_filter = ('categoria', 'data_publicacao') # Cria filtro lateral por data e tipo
    search_fields = ('titulo',)
    
    # Adiciona textos de ajuda na tela
    fieldsets = (
        ('Informações do Arquivo', {
            'fields': ('titulo', 'categoria', 'arquivo')
        }),
        ('Data', {
            'fields': ('data_publicacao',),
            'description': 'A data serve para organizar o arquivo na listagem mensal/anual.'
        }),
    )

from .models import ConfiguracaoGeral # <--- Importe o novo modelo

# Crie a classe de administração
class ConfiguracaoAdmin(admin.ModelAdmin):
    list_display = ('email_recebimento',)
    
    # Remove o botão "Adicionar" se já existir 1 configuração
    def has_add_permission(self, request):
        if ConfiguracaoGeral.objects.exists():
            return False
        return True



admin.site.register(ConfiguracaoGeral, ConfiguracaoAdmin)
admin.site.register(Pet, PetAdmin)
admin.site.register(Adotante, AdotanteAdmin)
admin.site.register(Voluntario, VoluntarioAdmin)
admin.site.register(Adocao, AdocaoAdmin)
admin.site.register(DocumentoTransparencia, DocumentoAdmin)
