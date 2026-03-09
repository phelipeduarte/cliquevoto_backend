from django.contrib import admin
from django.urls import path
from votacao.api import api 
from votacao.views import (
    realizar_inscricao, 
    detalhes_evento_publico, 
    lista_eleicoes_ativas 
)

urlpatterns = [
    # Painel Administrativo
    path('admin/', admin.site.urls),
    
    # Rotas da API (Django Ninja)
    path('api/', api.urls), 
    
    # --- ROTAS DO NOVO RITO DE CADASTRO (Rest Framework) ---
    
    # Adicionamos a barra '/' no final para padrão Django. 
    # O Django redirecionará automaticamente se o Front esquecer a barra.
    
    # 1. Lista Geral de Eventos
    path('api/eleicoes/ativas/', lista_eleicoes_ativas, name='lista_ativas'),
    
    # 2. Detalhes via Slug (Ex: madri-2026)
    path('api/evento/info/<slug:slug>/', detalhes_evento_publico, name='info_evento'),
    
    # 3. Processamento da Inscrição
    path('api/evento/inscrever/', realizar_inscricao, name='inscricao_votante'),
]