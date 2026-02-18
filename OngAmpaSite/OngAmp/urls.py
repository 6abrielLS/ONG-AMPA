from django.contrib import admin
from django.urls import path
from . import views

# === PERSONALIZAÇÃO DO PAINEL ===
admin.site.site_header = "Painel Administrativo - ONG AMPA"
admin.site.site_title = "Admin AMPA"
admin.site.index_title = "Gerenciamento do Sistema"


urlpatterns = [
    path('', views.index, name='index'),
    path('sobre/', views.sobre, name='sobre'), 
    path('contato/', views.contato, name='contato'),
    path('transparencia/', views.transp, name='transparencia'),
    path('transparencia/prestacao-de-contas/', views.prestacao_contas, name='prestacao_contas'),    
    path('adote_pet/', views.lista_pets, name='lista_pets'),
    path('adote-pet/<int:pet_id>/', views.detalhes_pet, name='detalhes_pet'),
    path('adote-pet/cadastro/', views.cadastro_adotante, name='cadastro_adotante'),
    path('adote-pet/cadastro/<int:pet_id>/', views.cadastro_adotante, name='cadastro_adotante_pet'),
    
]