---
name: engenharia-reversa-sistemas
description: >
  Skill especializada em analisar projetos de software existentes e reconstruir
  sua arquitetura, dependências, fluxo de dados e narrativa pedagógica.
  Use quando precisar varrer um projeto Django (ou qualquer projeto Python) e
  extrair: estrutura de módulos, mapa de dependências, ordem de execução,
  pontos de entrada, fluxo de dados entre camadas, padrões usados e conceitos
  ensinados. Essencial para gerar documentação acadêmica a partir de código.
---

# Engenharia Reversa de Sistemas
## Analisando código para extrair conhecimento

---

## O que esta skill faz

Transforma um projeto de código em um **mapa de conhecimento estruturado**
que pode ser usado para gerar documentação, material didático ou análise técnica.

Não apenas lista arquivos — **compreende** as relações entre eles.

---

## Protocolo de Análise (executar nesta ordem)

### Fase 1 — Inventário

```python
# Varredura completa da pasta do projeto
import os
from pathlib import Path

def inventariar_projeto(raiz):
    """
    Mapeia todos os arquivos do projeto em categorias:
    - Configuração (settings.py, urls.py raiz)
    - Modelos (models.py)
    - Lógica (views.py, tables.py, admin.py)
    - Rotas (urls.py das apps)
    - Templates (arquivos .html)
    - Estáticos (imagens, CSS, JS)
    - Scripts utilitários (*.py na raiz)
    """
    inventario = {
        'configuracao': [],
        'modelos': [],
        'logica': [],
        'rotas': [],
        'templates': [],
        'estaticos': [],
        'scripts': [],
        'migrações': [],
    }
    for caminho in Path(raiz).rglob('*'):
        if caminho.is_file():
            classificar_arquivo(caminho, inventario)
    return inventario

def classificar_arquivo(caminho, inventario):
    nome = caminho.name
    partes = caminho.parts
    if nome == 'settings.py': inventario['configuracao'].append(caminho)
    elif nome == 'models.py': inventario['modelos'].append(caminho)
    elif nome == 'views.py':  inventario['logica'].append(caminho)
    elif nome == 'urls.py':   inventario['rotas'].append(caminho)
    elif nome == 'tables.py': inventario['logica'].append(caminho)
    elif nome == 'admin.py':  inventario['logica'].append(caminho)
    elif nome.endswith('.html'): inventario['templates'].append(caminho)
    elif nome.endswith(('.png','.jpg','.css','.js')): inventario['estaticos'].append(caminho)
    elif 'migrations' in partes: inventario['migrações'].append(caminho)
    elif nome.endswith('.py'): inventario['scripts'].append(caminho)
```

---

### Fase 2 — Mapa de Dependências

Para cada arquivo, identificar:

```
QUEM IMPORTA QUEM:
views.py      → importa models.py, tables.py
urls.py (app) → importa views.py
urls.py (proj)→ importa urls.py das apps
admin.py      → importa models.py
templates     → referenciam {% url 'alias' %} e {% extends %}

ORDEM DE EXECUÇÃO:
1. settings.py (configuração)
2. urls.py do projeto (roteamento principal)
3. urls.py da app (roteamento da app)
4. views.py (função chamada pela rota)
5. models.py (se a view consulta o banco)
6. template .html (renderização final)
```

```python
def extrair_dependencias(arquivo):
    """
    Lê um arquivo Python e extrai:
    - Imports diretos (from X import Y)
    - Referências a models (objects.filter, objects.all)
    - Templates renderizados (render(request, 'template.html'))
    - URLs referenciadas (reverse_lazy, redirect)
    """
    conteudo = Path(arquivo).read_text(encoding='utf-8', errors='ignore')
    deps = {
        'imports': re.findall(r'^(?:from|import)\s+([\w.]+)', conteudo, re.M),
        'models_usados': re.findall(r'(\w+)\.objects\.', conteudo),
        'templates': re.findall(r"render\(request,\s*['\"]([^'\"]+)['\"]", conteudo),
        'urls': re.findall(r"reverse_lazy\(['\"]([^'\"]+)['\"]", conteudo),
    }
    return deps
```

---

### Fase 3 — Extração de Comentários Pedagógicos

```python
def extrair_comentarios_pedagogicos(arquivo):
    """
    Extrai blocos de comentário que seguem o padrão pedagógico:
    # ================================================================
    # Nome — O que faz
    # Por que existe: ...
    # Analogia médica: ...
    # O que ver: ...
    # ================================================================
    Retorna lista de dicts com: nome, o_que_faz, por_que, analogia, o_que_ver
    """
    conteudo = Path(arquivo).read_text(encoding='utf-8', errors='ignore')
    blocos = re.findall(
        r'# =+\n# (.+?)\n((?:# .+\n)*?)# =+',
        conteudo, re.MULTILINE
    )
    resultado = []
    for titulo, corpo in blocos:
        linhas = [l.strip('# ').strip() for l in corpo.strip().split('\n')]
        resultado.append({
            'titulo': titulo.strip(),
            'linhas': linhas,
            'arquivo': str(arquivo)
        })
    return resultado
```

---

### Fase 4 — Narrativa Pedagógica

Após varrer todos os arquivos, montar a sequência de ensino:

```python
ORDEM_PEDAGOGICA = [
    # (arquivo, título da seção, conceito central ensinado)
    ('bdpratico/settings.py',           'Configurando o Projeto',      'settings e INSTALLED_APPS'),
    ('bdpratico/urls.py',               'Roteamento Principal',         'include e urlpatterns'),
    ('exemplo01/models.py',             'Modelando o Banco de Dados',   'Models e migrations'),
    ('exemplo02/models.py',             'Dados para Machine Learning',  'Model para ML'),
    ('exemplo01/admin.py',              'Painel Administrativo',        'admin.site.register'),
    ('exemplo01/templates/base.html',   'Template Base e Herança',      'extends e block'),
    ('exemplo01/views.py:pagina0',      'Primeira Página HTML',         'render e templates'),
    ('exemplo01/views.py:pagina1-3',    'Passando Dados ao Template',   'contexto e dicionário'),
    ('exemplo01/templates/index.html',  'Sistema de Login',             'authenticate e session'),
    ('exemplo01/views.py:index',        'Autenticação',                 'login/logout'),
    ('exemplo01/views.py:pagina4-5',    'Formulários POST e CREATE',    'request.POST e objects.create'),
    ('exemplo01/tables.py',             'Tabelas Dinâmicas',            'django-tables2'),
    ('exemplo01/views.py:CBVs',         'Class-Based Views CRUD',       'ListView/CreateView/UpdateView/DeleteView'),
    ('exemplo01/templates/exemplo01/',  'Templates do CRUD',            'bootstrap_field e csrf_token'),
    ('exemplo01/views.py:pagina6-8',    'Template Tags',                'for, if, forloop.counter, extends'),
    ('exemplo01/views.py:pagina9-11',   'Pandas Import/Export',         'DataFrame e FileSystemStorage'),
    ('exemplo01/views.py:pagina12',     'Gráficos com Plotly',          'go.Figure e plot_div'),
    ('exemplo02/views.py:ia_import',    'Importando Dataset de ML',     'CSV para banco de dados'),
    ('exemplo02/views.py:knn_treino',   'Treinando o Modelo KNN',       'GridSearchCV e joblib'),
    ('exemplo02/views.py:matriz',       'Avaliando com Matriz',         'confusion_matrix'),
    ('exemplo02/views.py:roc',          'Curva ROC',                    'roc_curve e auc'),
    ('exemplo02/views.py:recall',       'Curva Precision-Recall',       'precision_recall_curve'),
]
```

---

### Fase 5 — Relatório de Engenharia Reversa

Gerar um dicionário estruturado com tudo que foi encontrado:

```python
def gerar_relatorio(raiz_projeto):
    return {
        'inventario': inventariar_projeto(raiz_projeto),
        'dependencias': {arq: extrair_dependencias(arq) for arq in ...},
        'comentarios': {arq: extrair_comentarios_pedagogicos(arq) for arq in ...},
        'ordem_pedagogica': ORDEM_PEDAGOGICA,
        'modelos': extrair_modelos(raiz_projeto),
        'rotas': extrair_todas_rotas(raiz_projeto),
        'templates': mapear_templates(raiz_projeto),
    }
```

---

## Padrões de Detecção

### Detectar tipo de view

```python
def tipo_de_view(codigo_view):
    if 'class ' in codigo_view and 'View' in codigo_view:
        if 'ListView'   in codigo_view: return 'CBV-List'
        if 'CreateView' in codigo_view: return 'CBV-Create'
        if 'UpdateView' in codigo_view: return 'CBV-Update'
        if 'DeleteView' in codigo_view: return 'CBV-Delete'
        return 'CBV-Outro'
    elif 'def ' in codigo_view:
        if 'authenticate' in codigo_view: return 'FBV-Auth'
        if 'objects.create' in codigo_view: return 'FBV-Create'
        if 'pd.DataFrame' in codigo_view: return 'FBV-Pandas'
        if 'plotly' in codigo_view: return 'FBV-Plotly'
        if 'KNeighbors' in codigo_view: return 'FBV-ML'
        return 'FBV-Simples'
```

### Detectar conceitos Django usados

```python
CONCEITOS_DJANGO = {
    'objects.all()':        'QuerySet — busca todos os registros',
    'objects.filter(':      'QuerySet com filtro WHERE',
    'objects.create(':      'INSERT no banco de dados',
    'objects.get(':         'Busca por chave única',
    'makemigrations':       'Criação de arquivo de migração',
    'migrate':              'Aplicação de mudanças no banco',
    'render(':              'Renderização de template HTML',
    'HttpResponse(':        'Resposta HTTP simples (sem template)',
    'redirect(':            'Redirecionamento para outra URL',
    'reverse_lazy(':        'URL reversa (nome → endereço)',
    'authenticate(':        'Verificação de credenciais',
    'login(':               'Criação de sessão autenticada',
    'request.POST.get(':    'Leitura de dados enviados pelo formulário',
    'request.FILES(':       'Leitura de arquivo enviado pelo formulário',
    'FileSystemStorage(':   'Armazenamento de arquivo no servidor',
    'pd.DataFrame(':        'Criação de tabela de dados Pandas',
    'df.to_csv(':           'Exportação para CSV com Pandas',
    'go.Figure(':           'Criação de gráfico Plotly',
    'GridSearchCV(':        'Busca automática de hiperparâmetros KNN',
    'joblib.dump(':         'Salvamento do modelo treinado em arquivo',
    'confusion_matrix(':    'Cálculo da matriz de confusão',
    'roc_curve(':           'Cálculo da curva ROC',
}
```
