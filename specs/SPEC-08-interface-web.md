# Spec: APPSPEC-08 — Interface Web

**Versão:** 1.0  
**Status:** Aprovada  
**Autor:** Neri  
**Data:** 2026-04-26  
**Depende de:** SPEC-00, SPEC-06, SPEC-07

---

## 1. Resumo

Define a interface web completa: layout base, formulário clínico, tela de resultado dual (Alvarado vs KNN), tela de avaliação do modelo, aba pedagógica e documentação. Design com Bootstrap 5, paleta clínica (azul institucional + branco + vermelho de alerta). Painel pedagógico lateral fixo em todas as páginas. Disclaimer clínico obrigatório e não ocultável em telas de resultado.

---

## 2. Contexto e Motivação

**Problema:** A interface é a camada que o professor e o apresentador veem. Deve deixar Django, KNN e as métricas da disciplina absolutamente explícitos — não só funcionais, mas visualmente evidentes.

**Por que agora:** SPEC-08 é o último módulo — depende de todas as camadas anteriores já definidas.

---

## 3. Goals

- [ ] G-01: Layout base com painel pedagógico lateral fixo em todas as páginas
- [ ] G-02: Formulário clínico claro com labels descritivos e help text com DOIs
- [ ] G-03: Tela de resultado com dois cards lado a lado: Alvarado vs KNN
- [ ] G-04: Tela de avaliação com matriz de confusão e tabela comparativa de métricas
- [ ] G-05: Navbar com 5 seções incluindo "Como Funciona" e "Documentação"
- [ ] G-06: Disclaimer clínico visível sem scroll em telas de resultado

| Métrica | Baseline | Target | Prazo |
|---|---|---|---|
| Páginas implementadas | 0 | 6 | SPEC-08 |
| Tecnologias visíveis na UI | 0/6 | 6/6 | SPEC-08 |
| Disclaimer visível sem scroll | não | sim | SPEC-08 |

---

## 4. Non-Goals

- NG-01: **NÃO** usa React, Vue ou qualquer framework JavaScript pesado
- NG-02: **NÃO** tem animações complexas — interface limpa e funcional
- NG-03: **NÃO** tem modo dark ou temas customizáveis
- NG-04: **NÃO** é responsivo para mobile — prioridade é desktop/projetor

---

## 5. Usuários e Personas

**Primário:** Professor avaliador em tela de desktop/notebook  
**Secundário:** Apresentador durante defesa (projetor)

---

## 6. Requisitos Funcionais

### 6.1 Paleta de Cores e Design

```css
/* Paleta clínica institucional */
--cor-primaria:    #1a5276;  /* Azul institucional UFG */
--cor-secundaria:  #ffffff;  /* Branco */
--cor-alerta:      #e74c3c;  /* Vermelho — alto risco */
--cor-moderado:    #f39c12;  /* Amarelo — risco moderado */
--cor-seguro:      #27ae60;  /* Verde — baixo risco */
--cor-pedagogica:  #2e86c1;  /* Azul claro — badges de tecnologia */
--cor-fundo:       #f8f9fa;  /* Cinza claro Bootstrap */
```

### 6.2 base.html — Layout Base

```html
<!-- Estrutura de todas as páginas -->
<body>
  <!-- NAVBAR -->
  <nav class="navbar navbar-dark" style="background: var(--cor-primaria)">
    🏥 APPSPEC — Diagnóstico de Apendicite
    | Avaliar | Métricas do Modelo | Como Funciona | Histórico | Documentação
  </nav>

  <!-- BANNER DISCIPLINA (fixo abaixo da navbar) -->
  <div class="alert alert-info text-center mb-0">
    <small>
      🎓 Disciplina: <strong>Agentes Inteligentes</strong> — UFG |
      Prof. Ronaldo Martins da Costa |
      Stack: <span class="badge bg-primary">Django 4.2</span>
             <span class="badge bg-success">KNN scikit-learn</span>
             <span class="badge bg-warning text-dark">Orange3</span>
             <span class="badge bg-info">pandas</span>
    </small>
  </div>

  <!-- GRID PRINCIPAL -->
  <div class="container-fluid mt-3">
    <div class="row">

      <!-- CONTEÚDO PRINCIPAL -->
      <div class="col-md-9">
        {% block content %}{% endblock %}
      </div>

      <!-- PAINEL PEDAGÓGICO LATERAL FIXO -->
      <div class="col-md-3">
        <div class="card border-primary sticky-top" style="top: 10px">
          <div class="card-header bg-primary text-white">
            🔧 {{ painel_titulo|default:"Tecnologia em Uso" }}
          </div>
          <div class="card-body">
            <h6 class="text-primary">{{ tecnologia_atual }}</h6>
            <p class="small">{{ descricao_tecnologia }}</p>
            <hr>
            <small class="text-muted">
              <strong>Aula referência:</strong><br>
              {{ aula_referencia }}
            </small>
            <hr>
            <small>
              <strong>Arquivo:</strong><br>
              <code>{{ componente_codigo }}</code>
            </small>
          </div>
          <div class="card-footer">
            <small class="text-muted">
              Acurácia do modelo: <strong>{{ acuracia_modelo }}%</strong><br>
              k = {{ k_modelo }}
            </small>
          </div>
        </div>

        <!-- BADGES DAS TECNOLOGIAS DA DISCIPLINA -->
        <div class="card mt-3">
          <div class="card-header">📚 Tecnologias da Disciplina</div>
          <div class="card-body">
            {% for tech in tecnologias_usadas %}
            <span class="badge bg-{{ tech.cor }} mb-1">{{ tech.nome }}</span>
            {% endfor %}
          </div>
        </div>
      </div>

    </div>
  </div>
</body>
```

### 6.3 index.html — Formulário Clínico

```html
{% extends 'diagnostico/base.html' %}
{% block content %}

<div class="card">
  <div class="card-header bg-primary text-white">
    <h4>🏥 Avaliação de Risco de Apendicite</h4>
    <small>Preencha os dados clínicos do paciente</small>
  </div>
  <div class="card-body">

    <!-- AVISO DE USO -->
    <div class="alert alert-warning">
      <strong>⚠️ Uso Didático:</strong> Este sistema é para fins acadêmicos.
      Não inserir dados de pacientes reais. Não substitui avaliação médica.
    </div>

    <form method="POST" action="{% url 'avaliar' %}">
      {% csrf_token %}

      <!-- SINTOMAS (4 pontos) -->
      <h5 class="mt-3">📋 Sintomas
        <span class="badge bg-secondary">até 3 pontos</span>
      </h5>
      {{ form.dor_migratoria }} {{ form.dor_migratoria.label }}
      <small class="text-muted d-block">{{ form.dor_migratoria.help_text }}</small>
      <!-- ... demais campos de sintomas ... -->

      <!-- SINAIS (5 pontos) -->
      <h5 class="mt-3">🩺 Sinais
        <span class="badge bg-secondary">até 4 pontos</span>
      </h5>
      <!-- ... campos de sinais ... -->

      <!-- LABORATÓRIO (3 pontos) -->
      <h5 class="mt-3">🧪 Laboratório
        <span class="badge bg-secondary">até 3 pontos</span>
      </h5>
      <div class="row">
        <div class="col-md-6">
          <label>{{ form.temperatura.label }}</label>
          {{ form.temperatura }}
          <small>{{ form.temperatura.help_text }}</small>
        </div>
        <div class="col-md-6">
          <label>{{ form.leucocitos.label }}</label>
          {{ form.leucocitos }}
          <small>{{ form.leucocitos.help_text }}</small>
        </div>
      </div>

      <button type="submit" class="btn btn-primary btn-lg mt-4 w-100">
        🔍 Calcular Risco (Alvarado + KNN)
      </button>
    </form>

  </div>
</div>
{% endblock %}
```

### 6.4 resultado.html — Resultado Dual

```html
{% block content %}

<!-- DISCLAIMER CLÍNICO OBRIGATÓRIO — SEMPRE ACIMA DO RESULTADO -->
<div class="alert alert-danger" style="border: 3px solid #e74c3c !important">
  ⚠️ <strong>AVISO OBRIGATÓRIO:</strong> Este é um sistema <strong>didático</strong>.
  A estimativa de risco apresentada abaixo <strong>NÃO</strong> constitui diagnóstico médico
  e <strong>NÃO</strong> deve ser usado para decisão clínica real.
  Consulte sempre um profissional de saúde habilitado.
</div>

<!-- RESULTADO DUAL: dois cards lado a lado -->
<div class="row">

  <!-- CARD ALVARADO SCORE -->
  <div class="col-md-6">
    <div class="card border-{{ resultado_alvarado.cor }}">
      <div class="card-header bg-{{ resultado_alvarado.cor }} text-white">
        📊 Alvarado Score
        <span class="badge bg-light text-dark float-end">Regra Clínica Determinística</span>
      </div>
      <div class="card-body">
        <h2 class="text-center">{{ resultado_alvarado.score }} / 10</h2>
        <h4 class="text-center text-{{ resultado_alvarado.cor }}">
          {{ resultado_alvarado.label }}
        </h4>
        <p>{{ resultado_alvarado.interpretacao }}</p>
        <p><strong>Conduta sugerida:</strong> {{ resultado_alvarado.conduta }}</p>
        <hr>

        <!-- DETALHAMENTO POR CRITÉRIO -->
        <h6>Detalhamento dos critérios:</h6>
        <table class="table table-sm">
          <thead><tr><th>Critério</th><th>Presente</th><th>Pontos</th></tr></thead>
          <tbody>
          {% for item in resultado_alvarado.detalhamento %}
          <tr class="{% if item.presente %}table-success{% endif %}">
            <td>{{ item.criterio }}
              <small><a href="https://doi.org/{{ item.doi }}" target="_blank">
                [DOI]</a></small>
            </td>
            <td>{% if item.presente %}✓{% else %}—{% endif %}</td>
            <td>{{ item.pontos }}</td>
          </tr>
          {% endfor %}
          </tbody>
          <tfoot>
            <tr class="table-primary">
              <td><strong>TOTAL</strong></td><td></td>
              <td><strong>{{ resultado_alvarado.score }}</strong></td>
            </tr>
          </tfoot>
        </table>

        <small class="text-muted">
          Método: Regra determinística baseada em Alvarado, 1986.<br>
          <a href="https://doi.org/10.1016/S0196-0644(86)80468-2" target="_blank">
            DOI: 10.1016/S0196-0644(86)80468-2</a>
        </small>
      </div>
    </div>
  </div>

  <!-- CARD KNN -->
  <div class="col-md-6">
    <div class="card border-{{ cor_knn }}">
      <div class="card-header bg-{{ cor_knn }} text-white">
        🤖 KNN — Machine Learning
        <span class="badge bg-light text-dark float-end">scikit-learn</span>
      </div>
      <div class="card-body">
        <h2 class="text-center">{{ resultado_knn.probabilidade_percentual }}</h2>
        <h4 class="text-center">{{ resultado_knn.label_predita }}</h4>

        <!-- BADGE DE TECNOLOGIA — Django visível -->
        <div class="alert alert-info p-2">
          <small>
            🔬 <strong>Algoritmo:</strong> {{ resultado_knn.algoritmo }}<br>
            📏 <strong>k = {{ resultado_knn.k_vizinhos }}</strong> vizinhos mais próximos<br>
            🎯 <strong>Acurácia do modelo:</strong> {{ resultado_knn.acuracia_modelo|floatformat:1 }}%<br>
            📐 <strong>Distância média:</strong> {{ resultado_knn.distancia_media_vizinhos|floatformat:3 }}<br>
            💪 <strong>Confiança:</strong>
              <span class="badge bg-{% if resultado_knn.confianca == 'Alta' %}success
                {% elif resultado_knn.confianca == 'Média' %}warning
                {% else %}danger{% endif %}">
                {{ resultado_knn.confianca }}
              </span>
          </small>
        </div>

        {% if resultado_knn.confianca == 'Baixa' %}
        <div class="alert alert-warning">
          ⚠️ Resultado inconclusivo: confiança do modelo abaixo de 60%.
          Priorizar o Alvarado Score neste caso.
        </div>
        {% endif %}

        <!-- DATASET -->
        <hr>
        <small class="text-muted">
          Dataset: Regensburg Pediatric Appendicitis<br>
          UCI ML Repository (id=938)<br>
          <a href="https://doi.org/10.5281/zenodo.7669442" target="_blank">
            DOI: 10.5281/zenodo.7669442</a>
        </small>
      </div>
    </div>
  </div>

</div>

<!-- BOTÕES DE NAVEGAÇÃO -->
<div class="row mt-3">
  <div class="col-md-6">
    <a href="{% url 'index' %}" class="btn btn-outline-primary w-100">
      ← Nova Avaliação
    </a>
  </div>
  <div class="col-md-6">
    <a href="{% url 'avaliacao_modelo' %}" class="btn btn-outline-success w-100">
      📊 Ver Métricas do Modelo (Matriz de Confusão)
    </a>
  </div>
</div>

{% endblock %}
```

### 6.5 avaliacao.html — Métricas do Modelo

```
- Título: "Avaliação do Modelo KNN — Tecnologia da Disciplina"
- Imagem PNG da matriz de confusão (gerada no setup.py)
- Legenda explicando VP, FP, FN, VN com definições hardcoded
- Tabela comparativa:
  Métrica        | Fórmula             | Alvarado | KNN
  Sensibilidade  | VP / (VP + FN)      | XX.X%    | XX.X%
  Especificidade | VN / (VN + FP)      | XX.X%    | XX.X%
  Acurácia       | (VP+VN) / Total     | XX.X%    | XX.X%
  VPP            | VP / (VP + FP)      | XX.X%    | XX.X%
  VPN            | VN / (VN + FN)      | XX.X%    | XX.X%
- Card: "Abrir no Orange3"
  "Execute: orange3 orange/validacao_knn.ows"
```

### 6.6 Navbar e Rotas Visíveis

```html
<nav>
  <a href="{% url 'index' %}">🏥 Avaliar</a>
  <a href="{% url 'avaliacao_modelo' %}">📊 Métricas do Modelo</a>
  <a href="{% url 'como_funciona' %}">❓ Como Funciona</a>
  <a href="{% url 'historico' %}">📋 Histórico</a>
  <a href="{% url 'documentacao' %}">📚 Documentação</a>
</nav>
```

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|---|---|---|---|
| RNF-01 | Disclaimer visível sem scroll | Sempre | Posicionado antes do resultado |
| RNF-02 | Painel lateral sticky | Sempre visível | Bootstrap `sticky-top` |
| RNF-03 | Badges de tecnologia visíveis | Em toda página | Banner fixo abaixo da navbar |
| RNF-04 | DOIs como links clicáveis | href para doi.org | Abre nova aba |

---

## 8. Design e Interface

Conforme seção 6.1 (paleta). Fonte: Bootstrap 5 padrão (system-ui). Sem fontes externas.

---

## 9. Modelo de Dados

N/A — todos os dados vêm das views (SPEC-07).

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|---|---|---|
| Bootstrap 5 CDN | Obrigatória | Layout quebrado — pode usar local |
| SPEC-07 (views e context) | Obrigatória | Templates sem dados |
| confusion_matrix.png | Opcional | Página de avaliação mostra "Imagem não gerada — execute setup.py" |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---|---|---|
| Imagem da matriz não existe | setup.py não rodou | Placeholder: "Execute setup.py para gerar a imagem" |
| KNN com baixa confiança | prob < 0.60 | Card KNN exibe banner de aviso amarelo |
| Template recebe None | View com erro silencioso | Exibe "Dados indisponíveis" em lugar de crash |

---

## 12. Segurança e Privacidade

- `{% csrf_token %}` em todos os formulários
- Nenhum dado pessoal exibido ou persistido visivelmente

---

## 13. Plano de Rollout

Último módulo gerado. Testado com `python manage.py runserver` após todos os módulos anteriores.

---

## 14. Open Questions

Nenhuma — sistema completo definido.
