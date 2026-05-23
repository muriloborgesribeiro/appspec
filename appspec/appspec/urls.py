# ================================================================
# ROTEAMENTO PRINCIPAL — Central Telefônica do Hospital
# Técnico: Este é o primeiro arquivo que o Django lê para descobrir 
# quais endereços existem no seu site. Ele funciona como um índice central 
# que distribui os acessos para as pastas corretas.
# Clínico: É como a telefonista da central do hospital que
# transfere as chamadas para os ramais internos.
# ================================================================

from django.contrib import admin
# ↑ Técnico: É o painel administrativo pronto que o Django constrói sozinho, lendo os modelos de dados.
# ↑ Clínico: Departamento de administração médica.

from django.urls import path, include
# ↑ Técnico: 'include()' permite anexar os endereços criados dentro de outro aplicativo (neste caso, o 'diagnostico').
# ↑ Clínico: include é como o ramal de uma ala inteira.

urlpatterns = [
    path('admin/', admin.site.urls),
    # ↑ Define que qualquer endereço começando com /admin/ vai para o painel administrativo

    path('', include('diagnostico.urls')),
    # ↑ path('') define a página inicial (raiz do site)
    # ↑ include('diagnostico.urls') diz ao Django: "Para qualquer outro endereço,
    # ↑ olhe dentro do arquivo urls.py da pasta diagnostico"
    # ↑ É como dizer: "Para falar com a Cardiologia, disque 1 e siga as opções de lá"
]

