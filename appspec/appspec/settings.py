# ============================================================
#  appspec/settings.py
#  APPSPEC — Configurações Django
#  Stack: Django 4.2 + SQLite (SPEC-00 LEI IMUTÁVEL)
#  Segurança: localhost only, DEBUG=True (SPEC-00 § 12)
# ============================================================

# ================================================================
# CONFIGURAÇÃO DO SISTEMA — Manual de Normas e Procedimentos
# Técnico: O settings.py é o arquivo principal de configurações do Django. 
# Ele controla tudo: qual banco de dados usar, quais pastas contém as imagens, 
# quais ferramentas de segurança estão ativas e os aplicativos instalados.
# Clínico: É como o manual de normas e procedimentos de um
# hospital, que define quem tem acesso a quê e como as informações devem fluir.
# ================================================================

import os
# ↑ Importa o módulo 'os' para interagir com o sistema operacional
# ↑ Serve para: Manipular caminhos de arquivos e pastas
# ↑ Analogia: É como o mapa físico do hospital

from pathlib import Path
# ↑ Path serve para manipular caminhos de forma moderna e intuitiva
# ↑ Analogia: É como o sistema de GPS do hospital

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# ↑ BASE_DIR = Pasta raiz do projeto
# ↑ resolve().parent.parent aponta para a pasta onde o manage.py reside
# ↑ É o "marco zero" do hospital para localizar qualquer outra sala

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'appspec-chave-didatica-nao-usar-em-producao-2024'
# ↑ Chave secreta usada para assinar dados (como cookies e sessões)
# ↑ Analogia: É a chave mestra que tranca todos os prontuários

# SECURITY WARNING: don't run with debug turned on in production!
# SPEC-00 § 12: DEBUG=True, localhost only
DEBUG = True
# ↑ DEBUG=True = Mostra erros detalhados no browser quando algo falha
# ↑ Útil para desenvolvimento, mas perigoso em produção
# ↑ Analogia: É como ter um painel de monitoramento que mostra cada batimento do sistema

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# ↑ Lista de endereços que podem acessar este sistema
# ↑ No projeto didático, limitamos apenas ao seu computador local
# ↑ Analogia: Lista de pessoas autorizadas a entrar no hospital

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',        # ↑ Painel administrativo pronto do Django
    'django.contrib.auth',         # ↑ Sistema de autenticação (login/logout)
    'django.contrib.contenttypes', # ↑ Permite ao Django rastrear tipos de conteúdo
    'django.contrib.sessions',     # ↑ Gerenciamento de sessões de usuário
    'django.contrib.messages',     # ↑ Sistema de mensagens de feedback (ex: "Salvo com sucesso")
    'django.contrib.staticfiles', # ↑ Gerenciamento de arquivos estáticos (CSS, Imagens)
    'diagnostico',                 # ↑ Nossa aplicação principal (onde está a inteligência)
]
# ↑ INSTALLED_APPS = Departamentos habilitados no hospital
# ↑ Cada item é uma "ala" do sistema que o Django carrega

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# ↑ Técnico: Middlewares são funções que rodam automaticamente toda vez que uma página é acessada. Eles verificam segurança, senhas e sessões antes de mostrar a página.
# ↑ Clínico: Equipe de triagem que verifica o paciente (filtra os dados) antes de chegar ao médico.

ROOT_URLCONF = 'appspec.urls'
# ↑ Define onde está o arquivo principal de roteamento (ramais do hospital)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # ← Pastas extras de templates (não usadas aqui)
        'APP_DIRS': True, # ← Django busca templates dentro de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'diagnostico.context_processors.contexto_pedagogico', # ← Nosso injetor de dados didáticos
            ],
        },
    },
]
# ↑ Configuração visual (Templates)
# ↑ Analogia: Formulários e laudos pré-definidos do hospital

WSGI_APPLICATION = 'appspec.wsgi.application'
# ↑ Técnico: Define como o seu projeto Django vai "conversar" com a internet quando for publicado em um servidor de verdade.

# Database — SQLite local (SPEC-00 § 5, LEI IMUTÁVEL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # ← Motor SQLite: banco em arquivo local
        'NAME': BASE_DIR / 'db.sqlite3',        # ← Localização física do arquivo do banco
    }
}
# ↑ DATABASES = Onde as informações são guardadas permanentemente
# ↑ Analogia: O arquivo central de prontuários do hospital

# Password validation (mantido por convenção Django)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
# ↑ Regras para aceitar senhas fortes

# Internationalization — Português brasileiro (SPEC-00 § 5)
LANGUAGE_CODE = 'pt-br'
# ↑ Define o idioma do sistema como Português do Brasil

TIME_ZONE = 'America/Sao_Paulo'
# ↑ Define o fuso horário para registros de data/hora

USE_I18N = True # ← Habilita tradução
USE_TZ = True   # ← Habilita fuso horário

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
# ↑ Prefixo usado na URL para acessar arquivos como estilos e imagens
# ↑ Analogia: Corredor onde ficam os materiais de escritório (estáticos)

STATICFILES_DIRS = []
# ↑ Outros diretórios de arquivos estáticos fora das apps

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ↑ Tipo padrão para IDs (chaves primárias) automáticos no banco

