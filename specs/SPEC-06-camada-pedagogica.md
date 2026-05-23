# Spec: APPSPEC-06 — Camada Pedagógica & Anti-Alucinação

**Versão:** 1.0  
**Status:** Aprovada  
**Autor:** Neri  
**Data:** 2026-04-26  
**Depende de:** SPEC-00, SPEC-01, SPEC-03, SPEC-04, SPEC-05

---

## 1. Resumo

Define todo o conteúdo pedagógico do sistema: o painel lateral fixo que explica em tempo real qual tecnologia da disciplina está sendo usada, a aba "Como Funciona", a área de documentação e todos os mecanismos anti-alucinação clínica. Este módulo é o que diferencia o APPSPEC de um simples sistema clínico — é a demonstração explícita da disciplina de Agentes Inteligentes.

---

## 2. Contexto e Motivação

**Problema:** Sistemas técnicos podem funcionar corretamente mas ser opacos para avaliação pedagógica — o professor não consegue ver as tecnologias em uso sem inspecionar o código.

**Por que agora:** SPEC-06 é pré-requisito de SPEC-07 e SPEC-08 porque define o conteúdo que os templates precisam renderizar.

---

## 3. Goals

- [ ] G-01: Painel lateral ativo em todas as páginas mostrando tecnologia em uso
- [ ] G-02: Aba "Como Funciona" com mapa visual da disciplina → sistema
- [ ] G-03: Área de documentação com alinhamento explícito matéria ↔ código
- [ ] G-04: 8 mecanismos anti-alucinação implementados e documentados
- [ ] G-05: Referências científicas clicáveis em toda tela de resultado

| Métrica | Baseline | Target | Prazo |
|---|---|---|---|
| Tecnologias da disciplina visíveis | 0/6 | 6/6 | SPEC-06 |
| Mecanismos anti-alucinação | 0/8 | 8/8 | SPEC-06 |
| Referências DOI clicáveis no resultado | 0 | ≥ 3 por resultado | SPEC-06 |

---

## 4. Non-Goals

- NG-01: **NÃO** usa LLMs para gerar nenhum conteúdo pedagógico — tudo hardcoded
- NG-02: **NÃO** é um tutorial interativo — é documentação estática integrada
- NG-03: **NÃO** tem quiz ou avaliação do aluno

---

## 5. Usuários e Personas

**Primário:** Professor avaliador — usa para verificar que as tecnologias da disciplina foram aplicadas corretamente  
**Secundário:** Apresentador (Neri) — usa para narrar o sistema durante a defesa

---

## 6. Requisitos Funcionais

### 6.1 Painel Lateral Pedagógico (presente em TODAS as páginas)

O painel lateral direito (Bootstrap col-md-3) exibe um card fixo com estado dinâmico por página:

```python
PAINEL_POR_PAGINA = {
    "index": {
        "titulo": "🔧 Tecnologia em Uso",
        "tecnologia_principal": "Django 4.2 — Framework Web",
        "descricao": "Este formulário é uma Django View (views.py) "
                     "com um Django Form (forms.py) validando os dados. "
                     "O Bootstrap 5 estiliza a interface via Django Templates.",
        "aula_referencia": "Aula 5 da disciplina — Django como framework web",
        "componente_codigo": "diagnostico/views.py → def avaliar(request)",
        "badge_cor": "primary"
    },
    "resultado": {
        "titulo": "🤖 Tecnologia em Uso",
        "tecnologia_principal": "KNN (scikit-learn) + Alvarado Score",
        "descricao": "O KNN (K-Nearest Neighbors) classificou este caso "
                     "comparando com os {k} vizinhos mais próximos no dataset Regensburg. "
                     "O Alvarado Score calculou o risco com regra determinística clínica.",
        "aula_referencia": "Aula 5 — KNN com scikit-learn",
        "componente_codigo": "ml/knn_engine.py → def predizer()",
        "badge_cor": "success"
    },
    "avaliacao": {
        "titulo": "📊 Tecnologia em Uso",
        "tecnologia_principal": "Matriz de Confusão — scikit-learn",
        "descricao": "A Matriz de Confusão foi gerada com sklearn.metrics.confusion_matrix. "
                     "Sensibilidade e Especificidade são as métricas centrais para "
                     "avaliação de classificadores clínicos.",
        "aula_referencia": "Aula 5 — Avaliação de modelos: VP, FP, FN, VN",
        "componente_codigo": "ml/avaliador.py → def avaliar_modelo()",
        "badge_cor": "warning"
    },
    "como_funciona": {
        "titulo": "📚 Mapa da Disciplina",
        "tecnologia_principal": "Visão geral do sistema",
        "descricao": "Esta página mapeia cada tecnologia ensinada na disciplina "
                     "para o componente correspondente no sistema APPSPEC.",
        "badge_cor": "info"
    }
}
```

### 6.2 Aba "Como Funciona" — Conteúdo

```
SEÇÃO 1: A Disciplina e o Sistema
  Tabela: Conteúdo da Aula → Tecnologia → Componente no APPSPEC → Arquivo
  ─────────────────────────────────────────────────────────────────
  KNN                 → scikit-learn KNeighborsClassifier → ml/knn_engine.py
  Validação visual    → Orange3 (.ows)                    → orange/validacao_knn.ows
  Framework web       → Django 4.2                        → diagnostico/views.py
  Manipulação dados   → pandas DataFrame                  → ml/preprocessamento.py
  Serialização modelo → joblib                            → ml/modelos/knn_model.joblib
  Métricas avaliação  → sklearn.metrics                   → ml/avaliador.py

SEÇÃO 2: O Dataset
  - Nome: Regensburg Pediatric Appendicitis
  - Fonte: UCI Machine Learning Repository (id=938)
  - Pacientes: 780 (após limpeza)
  - Features usadas: [lista dinâmica das features]
  - Referência: Marcinkevics et al., 2023. DOI:10.5281/zenodo.7669442
  - Como foi baixado: ucimlrepo.fetch_ucirepo(id=938) — automático no setup.py

SEÇÃO 3: O KNN Explicado
  - O que é KNN: classificação por distância euclidiana no hiperplano de features
  - Por que KNN para apendicite: interpretável, sem caixa-preta, bom para datasets médicos
  - k utilizado: {k_otimo} (selecionado por cross-validation)
  - Features do modelo: [lista com nomes]
  - Acurácia: {acuracia_teste}%

SEÇÃO 4: O Alvarado Score Explicado
  - História: criado em 1986 por Alfredo Alvarado no Hospital de Los Angeles, Califórnia
  - Critérios: tabela com os 8 critérios, pesos e DOIs
  - Pontos de corte: 0-4 baixo | 5-6 moderado | 7-10 alto
  - Limitações conhecidas: menor sensibilidade em mulheres em idade fértil, crianças pequenas

SEÇÃO 5: Como Usar Este Sistema
  - Passo a passo do fluxo clínico
  - O que o sistema faz e o que NÃO faz
  - Disclaimer completo
```

### 6.3 Área de Documentação — Conteúdo

```
SEÇÃO 1: Visão Geral do Projeto
  Objetivo acadêmico, disciplina, professor, instituição

SEÇÃO 2: Arquitetura do Sistema
  Diagrama das 5 camadas (texto/ASCII)

SEÇÃO 3: Stack Tecnológico
  Cada biblioteca com versão, função no sistema e aula onde foi ensinada

SEÇÃO 4: Dataset Regensburg
  Descrição completa, licença, como citar, link para UCI

SEÇÃO 5: Referências Clínicas
  Todos os DOIs usados no sistema com citação completa

SEÇÃO 6: Referências Técnicas (ML)
  Cover & Hart (1967) KNN, Fawcett (2006) Métricas, scikit-learn paper

SEÇÃO 7: Limitações e Disclaimer
  O que o sistema não faz, populações não cobertas, aviso clínico formal
```

### 6.4 Os 8 Mecanismos Anti-Alucinação

```python
ANTI_ALUCINACAO = {

    # 1. Texto clínico hardcoded
    "1_texto_hardcoded": {
        "descricao": "Nenhuma string clínica é gerada dinamicamente",
        "implementacao": "Todo texto clínico está em dicionários em ml/alvarado.py",
        "motivo": "Texto gerado por LLM pode conter informações clínicas incorretas"
    },

    # 2. Bounds do score
    "2_score_bounds": {
        "descricao": "Alvarado Score sempre entre 0 e 10",
        "implementacao": "assert 0 <= score <= 10 em ml/alvarado.py",
        "motivo": "Score fora de range indica bug — nunca deve chegar ao usuário"
    },

    # 3. Disclaimer obrigatório
    "3_disclaimer_obrigatorio": {
        "descricao": "Aviso clínico em 100% das telas de resultado",
        "implementacao": "Bloco HTML fixo no base.html — não pode ser ocultado",
        "texto": "⚠️ AVISO: Este sistema é uma ferramenta de apoio didática. "
                 "NÃO substitui avaliação médica presencial. "
                 "NÃO deve ser usado para decisão clínica real.",
        "motivo": "Prevenir uso indevido em contexto clínico real"
    },

    # 4. Referências DOI em cada critério
    "4_referencias_doi": {
        "descricao": "Toda afirmação clínica tem DOI rastreável",
        "implementacao": "Campo 'referencia' em CRITERIOS e CLASSIFICACOES",
        "motivo": "Rastreabilidade científica — sem afirmações sem fonte"
    },

    # 5. Confiança mínima do KNN
    "5_confianca_minima": {
        "descricao": "KNN mostra aviso se confiança < 60%",
        "implementacao": "Campo 'confianca' em predizer() — 'Baixa' se prob < 0.60",
        "texto_aviso": "⚠️ Resultado inconclusivo: confiança do modelo abaixo de 60%",
        "motivo": "Não exibir resultado como conclusivo quando o modelo está inseguro"
    },

    # 6. Separação de responsabilidade diagnóstica
    "6_linguagem_risco": {
        "descricao": "Sistema nunca usa a palavra 'diagnóstico' — apenas 'estimativa de risco'",
        "implementacao": "Revisão de todos os templates e strings hardcoded",
        "motivo": "Diagnóstico é ato médico privativo — sistema faz triagem de risco"
    },

    # 7. Dados não identificáveis
    "7_sem_identificacao": {
        "descricao": "Formulário não coleta nome, CPF ou qualquer dado pessoal",
        "implementacao": "DadosClinicosForm sem campos identificadores",
        "motivo": "Privacidade e LGPD — sistema não deve processar dados identificáveis"
    },

    # 8. Validação estrita de entrada
    "8_validacao_entrada": {
        "descricao": "Todos os campos clínicos têm validação de range",
        "implementacao": "DadosClinicosForm com validators em forms.py",
        "ranges": {
            "temperatura": (35.0, 42.0),
            "leucocitos": (1000, 50000)
        },
        "motivo": "Valores fora de range fisiológico indicam erro de digitação"
    }
}
```

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|---|---|---|---|
| RNF-01 | Painel lateral visível em todas as páginas | 100% | Bootstrap col-md-3, sticky |
| RNF-02 | Disclaimer visível sem scroll | Sempre | Posicionado acima do resultado |
| RNF-03 | Referências DOI clicáveis | Links para DOI.org | `<a href="https://doi.org/...">` |

---

## 8. Design e Interface

```
Layout geral de todas as páginas (Bootstrap grid):
┌──────────────────────────────┬────────────────────┐
│  col-md-9 — Conteúdo         │  col-md-3          │
│  (formulário / resultado /   │  PAINEL PEDAGÓGICO │
│   avaliação / documentação)  │  [fixo, sticky]    │
│                              │                    │
│  ┌──────────────────────┐    │  🔧 Tecnologia     │
│  │ ⚠️ DISCLAIMER        │    │  em Uso Agora      │
│  │ (sempre visível,     │    │  ─────────────     │
│  │  acima do resultado) │    │  Django Views      │
│  └──────────────────────┘    │  Aula 5 ↗          │
│                              │                    │
└──────────────────────────────┴────────────────────┘
```

---

## 9. Modelo de Dados

```python
# Contexto pedagógico injetado em todas as views via context_processor
CONTEXTO_PEDAGOGICO = {
    "disciplina": "Agentes Inteligentes",
    "professor": "Prof. Ronaldo Martins da Costa",
    "instituicao": "UFG — Instituto de Informática",
    "tecnologias": ["Django 4.2", "KNN (scikit-learn)", "Orange3",
                    "pandas", "joblib", "Matriz de Confusão"],
    "dataset": "Regensburg Pediatric Appendicitis (UCI id=938)",
    "versao_sistema": "1.0"
}
```

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|---|---|---|
| base.html (SPEC-08) | Obrigatória | Painel lateral não renderiza |
| SPEC-03 (Alvarado) | Obrigatória | Conteúdo do painel no resultado incompleto |
| SPEC-04 (KNN) | Obrigatória | Metadados pedagógicos do KNN ausentes |
| Anti-alucinação Neri | Complementar | Incorporar quando recebidos |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---|---|---|
| Métricas do modelo não calculadas | setup.py não rodou | Painel mostra "Modelo não avaliado — execute setup.py" |
| DOI inacessível | Link clicado offline | Link abre DOI.org — falha silenciosa do browser |
| Disclaimer ocultado por CSS | Tentativa de override | Disclaimer usa `!important` e `z-index` alto |

---

## 12. Segurança e Privacidade

- Todo conteúdo pedagógico é estático — sem processamento de dados do usuário
- Nenhum dado de avaliação é enviado a servidores externos

---

## 13. Plano de Rollout

Conteúdo desta spec é incorporado em SPEC-07 (views/context_processors) e SPEC-08 (templates).

---

## 14. Open Questions

- OQ-01: Neri enviará mecanismos adicionais de anti-alucinação — adicionar como itens 9, 10... na lista ANTI_ALUCINACAO
