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
    list_display = ('nome', 'cpf')
    search_fields = ('nome', 'cpf')


class VoluntarioAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('pet', 'adotante', 'voluntario', 'data')
    list_filter = ('data',)
    search_fields = ('pet__nome', 'adotante__nome', 'adotante__cpf')
    readonly_fields = ('data',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pet":
            # Mostra apenas pets DISPONÍVEIS na hora de criar nova adoção
            # Isso pode esconder o pet se você estiver EDITANDO uma adoção antiga
            kwargs["queryset"] = Pet.objects.filter(status_adocao='DISPONIVEL')
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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

admin.site.register(Pet, PetAdmin)
# admin.site.register(FotoPet) # Não precisa registrar separado, já está dentro de Pet
admin.site.register(Adotante, AdotanteAdmin)
admin.site.register(Voluntario, VoluntarioAdmin)
admin.site.register(Adocao, AdocaoAdmin)
admin.site.register(DocumentoTransparencia, DocumentoAdmin)
