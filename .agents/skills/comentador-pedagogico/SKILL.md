---
name: comentador-pedagogico
description: >
  Skill especializada em adicionar comentários pedagógicos em português a código
  Python e HTML já existente. Use APÓS o django-framework-builder criar os arquivos.
  Esta skill NUNCA reescreve código — apenas adiciona comentários que explicam
  o que cada linha faz, por que existe e o que se espera ver. 
  Nível de explicação DUPLO: (1) Analogias médicas para contexto e (2) Comentários 
  TÉCNICOS amigáveis para INICIANTES sobre a tecnologia (Django, Scikit-learn, Python, Pandas) 
  explicando o funcionamento algorítmico sem usar jargões impenetráveis (NÃO USE termos como "metaprogramação", "CBV", "Platt Scaling", "isometria").
  Segue o princípio Anti-Rewrite: o código original é intocável, apenas comentários 
  são adicionados.
---

# Comentador Pedagógico
## Adiciona explicações técnicas e contextuais sem tocar no código

---

## Princípio Fundamental — Anti-Rewrite

```
REGRA ABSOLUTA: Esta skill NUNCA altera código.
Só adiciona linhas que começam com # (Python) ou <!-- --> (HTML).
Se uma linha de código parecer errada, NÃO corrija — apenas documente.
A correção é responsabilidade do django-framework-builder.
```

Inspirado no mecanismo **Anti-Rewrite V3** do MedVoice:
> "O LLM Orquestrador NUNCA pode reescrever a prescrição."
> Aqui: o comentador NUNCA pode reescrever o código.

---

## A Estrutura de Camadas Duplas (Técnico + Clínico)

Todo comentário importante deve ter duas camadas:
1. **A Camada Tecnológica:** Explica o que a linha faz do ponto de vista de programação PARA INICIANTES (ex: "Liga uma página de internet a uma função", "Divide os dados em duas tabelas"). Evite jargões densos. Use uma linguagem simples que um aluno do primeiro ano de computação entenderia.
2. **A Camada Clínica (Analogia):** Faz a ponte com a realidade médica.

## Padrão de Comentário por Tipo de Linha

### Importações
```python
# Importa X de Y
# Técnico: [Explicação de engenharia de software ou biblioteca]
# Clínico: [Analogia com o mundo real/hospital]
from django.shortcuts import render  
# ↑ Técnico: A função render() junta o modelo da página HTML com os dados do Python e devolve a página pronta para o navegador.
# ↑ Clínico: É como a impressora que pega o modelo do laudo (template) e preenche com os dados do paciente.
```

### Definição de classe (Model)
```python
# ================================================================
# [NomeModel] — [O que representa no sistema]
# Técnico: A classe herda de models.Model, o que avisa ao Django para transformar isso em uma tabela de banco de dados.
# Clínico: O prontuário eletrônico do paciente.
# Campos: [lista resumida dos campos com tipos de dados]
# ================================================================
class pessoa(models.Model):
```

### Definição de função (View)
```python
# ================================================================
# [nome_view] — [O que faz em 1 frase]
# Técnico: Esta é uma função (view) que recebe as informações digitadas na página, processa e devolve a resposta.
# Clínico: O médico plantonista recebendo a ficha de triagem.
# Recebe: request (HttpRequest object)
# Retorna: render (HttpResponse)
# ================================================================
def pagina0(request):
```

### Cada linha de código relevante
```python
pacientes = pessoa.objects.all()
# ↑ Técnico: objects.all() vai até o banco de dados e traz uma lista com todas as linhas salvas nesta tabela.
# ↑ SQL: SELECT * FROM exemplo01_pessoa
# ↑ Clínico: Busca todas as fichas ativas no arquivo médico (SAME).

pacientes = pessoa.objects.filter(ativo=True)
# ↑ Técnico: O método .filter() vai até o banco de dados e traz uma lista apenas com as linhas que obedecem à regra (ativo=True).
# ↑ SQL: SELECT * FROM exemplo01_pessoa WHERE ativo=1
# ↑ Clínico: Separar apenas os pacientes que ainda estão internados na ala.
```

### Class-Based Views
```python
class pessoa_list(ListView):
# ↑ Técnico: ListView é uma ferramenta pronta do Django que serve para listar os itens do banco de dados na tela, criando até páginas (1, 2, 3...) se houver muitos.
# ↑ Clínico: Uma rotina automatizada do hospital para listar as altas do dia.

    def dispatch(self, request, *args, **kwargs):
    # ↑ Técnico: A função dispatch() é a porta de entrada. Ela roda antes de tudo para ver se o acesso é válido.
    # ↑ Clínico: O porteiro da ala verificando o crachá antes de deixar entrar.
```

### Templates HTML
```html
<!-- ================================================================ -->
<!-- [nome_template].html — [O que esta página mostra]               -->
<!-- Técnico: Template Django usando DTL (Django Template Language). -->
<!-- ================================================================ -->

{% extends 'base.html' %}
<!-- ↑ Técnico: Herança de templates. Este arquivo injeta conteúdo nos blocos definidos em base.html. -->
<!-- ↑ Clínico: Papel timbrado pré-impresso do hospital. -->

{% csrf_token %}
<!-- ↑ Técnico: Cross-Site Request Forgery token. Previne ataques de injeção de formulários de terceiros. -->
```

### Código KNN (Machine Learning)
```python
modelo_teste = KNeighborsClassifier(n_neighbors=k_teste, metric='euclidean')
# ↑ Técnico: Instancia o modelo KNN usando distância Euclidiana (raiz da soma dos quadrados das diferenças) no espaço n-dimensional.
# ↑ Clínico: O algoritmo procura os K pacientes matematicamente mais idênticos nos exames para basear o diagnóstico.

probabilidades = modelo.predict_proba(X_input)[0]
# ↑ Técnico: Retorna um array numpy com a probabilidade computada (fração de vizinhos majoritários) para cada classe.
# ↑ Clínico: O grau de certeza (ex: 80% dos vizinhos tinham apendicite).
```

---

## Regras de Aplicação

### O que SEMPRE comentar
- Primeira linha de cada arquivo (cabeçalho com viés tecnológico e clínico)
- Todas as importações
- Toda definição de classe ou função
- Toda linha de ORM (objects.filter, objects.create, etc.)
- Todo acesso a request.POST ou request.FILES
- Toda linha de Pandas, Plotly ou sklearn
- Todo bloco {% %} nos templates
- Toda variável {{ }} nos templates

### O que NÃO comentar
- Linhas em branco
- Colchetes e parênteses de fechamento sozinhos
- `pass` quando o contexto é óbvio
- Linhas já comentadas pelo builder

### Verificação Anti-Rewrite antes de entregar
```
□ Alguma linha de código foi alterada? → REVERTIDA
□ Alguma importação foi adicionada? → REMOVIDA
□ Alguma função foi renomeada? → REVERTIDA
□ A indentação foi respeitada? → OBRIGATÓRIO
□ Todos os comentários estão em português? → OBRIGATÓRIO
□ O comentário tem base TÉCNICA sólida (Engenharia de Software)? → OBRIGATÓRIO
```
