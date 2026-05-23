---
name: django-framework-builder
description: >
  Skill especializada em construir o projeto bdpratico do curso Framework Django UFG
  (Prof. Ronaldo Martins da Costa). Use sempre que o Antigravity precisar criar,
  modificar ou depurar qualquer arquivo do projeto: models.py, views.py, urls.py,
  templates HTML, tables.py, admin.py, settings.py, scripts Pandas, Plotly ou sklearn.
  Esta skill conhece a estrutura exata do curso, a ordem correta de construção,
  os nomes precisos dos arquivos e o padrão de comentários pedagógicos obrigatórios.
---

# Django Framework Builder
## Projeto bdpratico — Curso UFG

---

## Regra de Ouro

TODO arquivo criado deve ter comentários que respondam:
1. **O que faz** — 1 frase simples
2. **Por que existe** — qual problema resolve
3. **O que ver** — resultado visual no browser ou terminal

Nível: para alguém que nunca programou. Analogias médicas sempre que possível.

---

## Estrutura Completa do Projeto

```
bdpratico/
├── manage.py
├── knn_model.pkl              ← modelo KNN salvo (gerado na spec16)
├── bdpratico/
│   ├── settings.py
│   ├── urls.py                ← porteiro principal
│   └── wsgi.py
├── exemplo01/
│   ├── migrations/
│   ├── static/
│   │   ├── pessoa.png
│   │   └── direitos.png
│   ├── templates/
│   │   ├── index.html         ← login
│   │   ├── base.html          ← herança
│   │   ├── pagina0.html       ← Hello World
│   │   ├── pagina1.html       ← dados servidor
│   │   ├── pagina2.html       ← dados banco
│   │   ├── pagina3.html       ← filtro
│   │   ├── pagina4.html       ← POST form
│   │   ├── pagina5.html       ← CREATE
│   │   ├── pagina6.html       ← if/for tags
│   │   ├── pagina7.html       ← datas/counter
│   │   ├── pagina11.html      ← upload TXT
│   │   ├── pagina12.html      ← gráfico Plotly
│   │   └── exemplo01/
│   │       ├── listar_pessoas.html
│   │       ├── pessoa_menu.html
│   │       ├── pessoa_list.html
│   │       ├── pessoa_form.html
│   │       └── pessoa_delete.html
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tables.py
│   ├── urls.py
│   └── views.py
└── exemplo02/
    ├── migrations/
    ├── templates/
    │   ├── ia_import.html
    │   ├── ia_import_list.html
    │   ├── ia_knn_treino.html
    │   ├── ia_knn_matriz.html
    │   ├── ia_knn_roc.html
    │   └── ia_knn_recall.html
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── urls.py
    └── views.py
```

---

## Modelos (models.py — exemplo01)

```python
from django.db import models

# ================================================================
# Model pessoa — Cadastro de pessoas do sistema
# Analogia médica: é como o prontuário do paciente
# Campos: dados pessoais e profissionais de cada pessoa
# ================================================================
class pessoa(models.Model):
    nome = models.CharField(max_length=50, verbose_name='Nome')
    email = models.CharField(max_length=50, verbose_name='eMail')
    celular = models.CharField(max_length=20, verbose_name='Celular')
    funcao = models.CharField(max_length=50, verbose_name='Função')
    nascimento = models.DateField(verbose_name='Nascimento')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    def __str__(self):
        return self.nome
    class Meta:
        ordering = ['nome']

# ================================================================
# Model procedimento — Tabela de procedimentos médicos
# Analogia: tabela CBHPM de procedimentos com CID e valor
# ================================================================
class procedimento(models.Model):
    descricao = models.CharField(max_length=50, verbose_name='Descrição')
    cid = models.CharField(max_length=20, verbose_name='CID')
    valor = models.FloatField(null=True, blank=True, verbose_name='Valor')
    def __str__(self):
        return self.descricao
    class Meta:
        ordering = ['descricao']

# ================================================================
# Model procedimento_executado — Relaciona pessoas a procedimentos
# Analogia: o registro de atendimento que une paciente a procedimento
# ForeignKey = chave estrangeira = referência para outra tabela
# CASCADE = se o pai for deletado, o filho também é deletado
# ================================================================
class procedimento_executado(models.Model):
    pessoa = models.ForeignKey(pessoa, on_delete=models.CASCADE)
    procedimento = models.ForeignKey(procedimento, on_delete=models.CASCADE)
    obs = models.CharField(max_length=50, verbose_name='Observação')
    quantidade = models.FloatField(null=True, blank=True, verbose_name='Quantidade')
    def __str__(self):
        return self.obs
    class Meta:
        ordering = ['pessoa', 'procedimento']

# ================================================================
# Model exame — Armazena valores de exames (batimento cardíaco)
# Alimentado pelo upload do arquivo Framework-aula-4-Exames.txt
# ================================================================
class exame(models.Model):
    valor = models.FloatField(verbose_name='Valor')
    def __str__(self):
        return str(self.valor)
```

---

## Modelos (models.py — exemplo02)

```python
# ================================================================
# Model dados — Dataset para treinamento do modelo KNN
# Analogia: planilha de resultados de exames de pacientes
# usada para treinar o sistema a identificar padrões diagnósticos
# Grupos: 'Controle' (saudável) ou 'Experimental' (doente)
# Colunas: métricas extraídas de sinais biomédicos
# ================================================================
class dados(models.Model):
    grupo = models.CharField(max_length=20, verbose_name='Grupo')
    mdw = models.FloatField(verbose_name='MDW')
    latw = models.FloatField(verbose_name='LATW')
    tmcw = models.FloatField(verbose_name='TMCW')
    racw = models.FloatField(verbose_name='RACW')
    araw = models.FloatField(verbose_name='ARAW')
    def __str__(self):
        return self.grupo
    class Meta:
        ordering = ['grupo']
```

---

## settings.py — Configurações Obrigatórias

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'exemplo01',   # app principal do curso
    'exemplo02',   # app de Machine Learning
    'bootstrap5',  # Bootstrap 5 via django-bootstrap5
    'django_tables2',  # tabelas dinâmicas
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,  # OBRIGATÓRIO: permite encontrar pasta templates/ dentro das apps
    ...
}]

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'exemplo01' / 'static']
LOGIN_URL = '/'
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
```

---

## urls.py do Projeto

```python
from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('', include('exemplo01.urls')),        # raiz → exemplo01
    path('exemplo01/', include('exemplo01.urls')),
    path('exemplo02/', include('exemplo02.urls')),
    path('admin/', admin.site.urls),
]
```

---

## urls.py Final do exemplo01 (todas as rotas)

```python
urlpatterns = [
    path('', views.index, name='index_alias'),
    path('pagina0', views.pagina0, name='pagina0_alias'),
    path('pagina1', views.pagina1, name='pagina1_alias'),
    path('pagina2', views.pagina2, name='pagina2_alias'),
    path('pagina3', views.pagina3, name='pagina3_alias'),
    path('pagina4', views.pagina4, name='pagina4_alias'),
    path('pagina5', views.pagina5, name='pagina5_alias'),
    path('pagina6', views.pagina6, name='pagina6_alias'),
    path('pagina7', views.pagina7, name='pagina7_alias'),
    path('pagina8', views.pagina8, name='pagina8_alias'),
    path('pagina9', views.pagina9, name='pagina9_alias'),
    path('pagina10', views.pagina10, name='pagina10_alias'),
    path('pagina11', views.pagina11, name='pagina11_alias'),
    path('pagina12', views.pagina12, name='pagina12_alias'),
    path('menu', views.pessoa_menu, name='menu_alias'),
    path('pessoa_menu', views.pessoa_menu.as_view(), name='pessoa_menu_alias'),
    path('pessoa_list/', views.pessoa_list.as_view(), name='pessoa_list_alias'),
    path('pessoa_create/', views.pessoa_create.as_view(), name='pessoa_create_alias'),
    path('pessoa_update/<int:pk>/', views.pessoa_update.as_view(), name='pessoa_update_alias'),
    path('pessoa_delete/<int:pk>/', views.pessoa_delete.as_view(), name='pessoa_delete_alias'),
]
```

---

## Padrão de Comentário de View

```python
def pagina_X(request):
    # ================================================================
    # paginaX — [O que faz em 1 frase]
    # Por que existe: [qual problema resolve]
    # Analogia médica: [comparação com contexto médico]
    # O que o usuário verá: [descrição do resultado visual]
    # ================================================================
```

---

## Comandos Essenciais

```bash
python manage.py makemigrations exemplo01
python manage.py makemigrations exemplo02
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Arquivo Framework-aula-4-Exames.txt

O arquivo TXT tem registros separados por vírgula.
A coluna de índice 8 (nona coluna) contém o valor do batimento cardíaco.
Leitura na view pagina11:

```python
file2 = open(file1, 'r')
for row in file2:
    colunas = row.replace("(", "").replace(")", "").split(",")
    exame.objects.create(valor=float(colunas[8]))
file2.close()
```

---

## KNN — Padrão Completo

```python
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# Carrega dados do banco
dados_queryset = dados.objects.all()
df = pd.DataFrame(list(dados_queryset.values()))
X = df.drop(columns=['grupo', 'id'])   # features
y = df['grupo']                         # target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

parametros = {'n_neighbors': list(range(1, 21))}
knn = KNeighborsClassifier()
grid = GridSearchCV(knn, parametros, cv=5, scoring='accuracy')
grid.fit(X_train, y_train)

best_knn = grid.best_estimator_
y_pred = best_knn.predict(X_test)
acuracia = accuracy_score(y_test, y_pred)

model_filename = 'knn_model.pkl'
joblib.dump(best_knn, model_filename)
```
