# ============================================================
#  diagnostico/urls.py
#  APPSPEC — URLs nomeadas (6 rotas)
#  Tecnologia: Django URL dispatcher
#  Contrato: SPEC-07 6.4
# ============================================================

# ================================================================
# RAMAIS DA ALA — Diagnóstico
# Técnico: Este arquivo cria uma lista de endereços web (como '/index'). 
# Quando o usuário acessa um endereço, o Django lê esta lista e chama 
# a função correta (escrita no arquivo views.py) para gerar a página.
# Clínico: São os ramais internos da ala de Diagnóstico.
# Se a central transferiu para cá, aqui decidimos qual sala o 
# paciente (usuário) vai entrar.
# ================================================================

from django.urls import path
# ↑ Importa a função de definição de caminhos

from . import views
# ↑ Importa o arquivo views.py da mesma pasta (onde está a lógica)

app_name = 'diagnostico'
# ↑ Define o nome do "espaço de nomes" para evitar conflito com outras apps
# ↑ Para chamar uma URL daqui, usaremos: 'diagnostico:nome_da_rota'

urlpatterns = [
    # ------------------------------------------------------------
    # Página Principal (Dashboard / Formulário)
    # URL: http://localhost:8000/
    # ------------------------------------------------------------
    path('',                  views.index,           name='index'),
    # ↑ Técnico: A função path() liga um endereço (neste caso, a raiz '') à função views.index. O parâmetro name='index' cria um apelido para este endereço, facilitando criar links nos arquivos HTML.
    # ↑ Clínico: Recepciona pacientes recém-chegados na ala.

    # ------------------------------------------------------------
    # Tela de Inicialização (Splash Screen)
    # URL: http://localhost:8000/inicializacao/
    # ------------------------------------------------------------
    path('inicializacao/',    views.inicializacao,   name='inicializacao'),

    # ------------------------------------------------------------
    # Processamento da Avaliação
    # URL: http://localhost:8000/avaliar/
    # ------------------------------------------------------------
    path('avaliar/',          views.avaliar,          name='avaliar'),
    # ↑ Rota que recebe os dados do formulário via POST

    # ------------------------------------------------------------
    # Avaliação de Desempenho do Modelo
    # URL: http://localhost:8000/avaliacao-modelo/
    # ------------------------------------------------------------
    path('avaliacao-modelo/', views.avaliacao_modelo, name='avaliacao_modelo'),

    # ------------------------------------------------------------
    # Explicação Didática
    # URL: http://localhost:8000/como-funciona/
    # ------------------------------------------------------------
    path('como-funciona/',    views.como_funciona,    name='como_funciona'),

    # ------------------------------------------------------------
    # Documentação do Dataset
    # URL: http://localhost:8000/documentacao/
    # ------------------------------------------------------------
    path('documentacao/',     views.documentacao,     name='documentacao'),

    # ------------------------------------------------------------
    # Histórico de Consultas
    # URL: http://localhost:8000/historico/
    # ------------------------------------------------------------
    path('historico/',        views.historico,        name='historico'),
]

