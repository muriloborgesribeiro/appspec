# Spec: APPSPEC-00 — Contrato Inicial

**Versão:** 1.0  
**Status:** Aprovada  
**Autor:** Neri  
**Data:** 2026-04-26

---

## 1. Resumo

Contrato imutável do sistema **APPSPEC** — Sistema de Apoio ao Diagnóstico de Apendicite. Define stack, estrutura de pastas, língua, convenções e leis do projeto. **Nenhum código é gerado aqui.** Todos os prompts seguintes devem respeitar este documento como lei absoluta.

---

## 2. Contexto e Motivação

**Problema:** Trabalho acadêmico da disciplina de Agentes Inteligentes (UFG / Prof. Ronaldo Martins da Costa) exige sistema que não apenas funcione, mas que exiba e explique visivelmente as tecnologias ensinadas: KNN, scikit-learn, Orange3, Django, Pandas, Matriz de Confusão.

**Evidências:** O curso ensinou: KNN como classificador, scikit-learn para implementação em Python, Orange3 para validação visual no-code, Django como framework web full-stack, Pandas para manipulação de dados, e Matriz de Confusão / Sensibilidade / Especificidade como métricas de avaliação.

**Por que agora:** O professor avalia tanto a funcionalidade clínica quanto a clareza pedagógica. O sistema deve ser vitrine didática das tecnologias da disciplina — cada tecnologia visível, nomeada e explicada na interface.

---

## 3. Goals

- [ ] G-01: Sistema funcional de apoio ao diagnóstico de apendicite (Alvarado Score + KNN)
- [ ] G-02: Transparência pedagógica total — 6 tecnologias da disciplina visíveis e explicadas na UI
- [ ] G-03: Dataset real público (Regensburg, UCI id=938) baixado automaticamente pelo setup.py
- [ ] G-04: 100% offline em produção — sem LLMs, sem APIs externas, sem chamadas de rede após setup
- [ ] G-05: Anti-alucinação clínica — todo texto clínico é hardcoded com referência DOI
- [ ] G-06: Documentação pedagógica integrada alinhando o sistema com o conteúdo da disciplina

| Métrica | Baseline | Target | Prazo |
|---|---|---|---|
| Acurácia KNN no Regensburg | — | ≥ 80% | Entrega |
| Tecnologias da disciplina visíveis na UI | 0/6 | 6/6 | Entrega |
| Referências DOI por critério clínico Alvarado | 0 | ≥ 1 por critério | Entrega |
| Disclaimer clínico em telas de resultado | ausente | 100% | Entrega |
| Download automático do dataset | manual | automático via setup.py | Entrega |

---

## 4. Non-Goals

- NG-01: **NÃO** é sistema de produção hospitalar — é didático
- NG-02: **NÃO** usa LLMs para interpretar sintomas ou gerar texto clínico
- NG-03: **NÃO** usa nenhum algoritmo de ML além do KNN (tecnologia da disciplina)
- NG-04: **NÃO** faz diagnóstico definitivo — estima risco com disclaimer obrigatório
- NG-05: **NÃO** integra prontuário, FHIR, HL7 ou qualquer sistema externo
- NG-06: **NÃO** armazena dados de pacientes reais
- NG-07: **NÃO** tem autenticação de usuários nesta versão
- NG-08: **NÃO** usa banco externo — SQLite local via Django ORM

---

## 5. Stack Tecnológico — LEI IMUTÁVEL

```
Linguagem:         Python 3.11
Framework web:     Django 4.2
ML:                scikit-learn 1.4 (KNN exclusivamente)
Dados:             pandas 2.x + numpy
Serialização ML:   joblib
Download dataset:  ucimlrepo
Validação visual:  Orange3 (arquivo .ows gerado pelo sistema)
Banco de dados:    SQLite (Django padrão)
Frontend:          Django Templates + Bootstrap 5
Gráficos:          matplotlib + seaborn (imagens estáticas .png)
Língua do código:  português para domínio clínico, inglês para infraestrutura
Língua da UI:      Português brasileiro
```

---

## 6. Estrutura de Pastas — LEI IMUTÁVEL

```
appspec/
├── setup.py                        # Download dataset + treino KNN + geração Orange .ows
├── manage.py
├── requirements.txt
├── appspec/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── diagnostico/                    # App Django principal
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── templates/diagnostico/
│       ├── base.html               # Layout base com painel pedagógico lateral FIXO
│       ├── index.html              # Formulário de entrada clínica
│       ├── resultado.html          # Resultado dual: Alvarado vs KNN
│       ├── avaliacao.html          # Matriz de confusão + métricas do modelo
│       ├── como_funciona.html      # Aba pedagógica da disciplina
│       └── documentacao.html       # Documentação completa com referências
├── ml/                             # Módulo ML puro (independente do Django)
│   ├── alvarado.py                 # Motor Alvarado Score (determinístico)
│   ├── knn_engine.py               # Motor KNN (treino + predição)
│   ├── avaliador.py                # Métricas (confusão, sensibilidade, especificidade)
│   ├── preprocessamento.py         # Limpeza e normalização do Regensburg
│   └── modelos/
│       └── knn_model.joblib        # Modelo serializado (gerado pelo setup.py)
├── data/
│   ├── regensburg_raw.csv          # Dataset bruto (baixado pelo setup.py)
│   └── regensburg_processed.csv    # Dataset pré-processado (gerado pelo setup.py)
├── orange/
│   └── validacao_knn.ows           # Workflow Orange3 (gerado pelo setup.py)
└── docs/
    └── referencias_clinicas.md     # DOIs de todos os critérios clínicos
```

---

## 7. Convenções — LEI IMUTÁVEL

1. Todo critério clínico no código tem comentário com DOI da referência
2. Nenhuma string clínica é gerada dinamicamente — todas são dicionários hardcoded em `ml/alvarado.py`
3. Score Alvarado sempre entre 0 e 10 — AssertionError se violado
4. KNN nunca exibe resultado sem mostrar: valor de k, acurácia do modelo, distância dos k vizinhos
5. Disclaimer clínico presente em 100% das telas de resultado — não pode ser ocultado por CSS
6. Painel pedagógico lateral fixo em todas as páginas — não colapsável
7. `setup.py` imprime logs didáticos numerados explicando cada etapa executada
8. Toda métrica exibida (sensibilidade, especificidade) tem fórmula visível na UI

---

## 8. Design e Interface

N/A — definido em SPEC-08.

---

## 9. Modelo de Dados

N/A — definido em SPEC-07.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|---|---|---|
| ucimlrepo + internet | Obrigatória apenas no setup.py | Fallback: usar regensburg_raw.csv pré-baixado em /data/ |
| scikit-learn | Obrigatória em runtime | Sistema não funciona |
| Django 4.2 | Obrigatória em runtime | Sistema não funciona |
| Orange3 | Opcional em runtime | Necessária apenas para abrir o .ows gerado |
| matplotlib / seaborn | Obrigatória no setup.py | Gráficos não gerados; sistema funciona sem eles |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---|---|---|
| Sem internet no setup | ucimlrepo.fetch falha | Tenta usar /data/regensburg_raw.csv; se ausente, para e instrui o usuário |
| Dataset já baixado | setup.py executado 2x | Detecta arquivo existente, pula download, loga "✓ Dataset já disponível" |
| Modelo KNN não treinado | View chamada sem knn_model.joblib | Redireciona para /setup com mensagem de instrução |
| Score Alvarado fora de [0,10] | Bug de cálculo | AssertionError com mensagem: "Score inválido: {valor}. Esperado: 0-10" |
| Dataset com linhas corrompidas | NaN em features obrigatórias | Linha descartada; loga quantidade de linhas removidas |

---

## 12. Segurança e Privacidade

- Nenhum dado de paciente real deve ser inserido — formulário tem aviso visível
- SQLite local sem exposição de rede (DEBUG=True, ALLOWED_HOSTS=['localhost'])
- Formulário não coleta nome, CPF ou qualquer identificador pessoal
- Sistema roda exclusivamente em localhost:8000

---

## 13. Plano de Rollout — Sequência de Prompts

```
SPEC-00  → Este contrato                    [sem código — aprovação obrigatória]
SPEC-01  → Arquitetura Global               [diagrama de componentes e interfaces]
SPEC-02  → Setup & Dataset                  [setup.py + preprocessamento.py]
SPEC-03  → Motor Alvarado Score             [ml/alvarado.py]
SPEC-04  → Motor KNN                        [ml/knn_engine.py]
SPEC-05  → Módulo de Avaliação              [ml/avaliador.py + validacao_knn.ows]
SPEC-06  → Camada Pedagógica                [conteúdo, referências, anti-alucinação]
SPEC-07  → App Django                       [models + views + urls + forms]
SPEC-08  → Interface Web                    [templates + static + Bootstrap 5]
```

---

## 14. Open Questions

- OQ-01: Neri enviará mecanismos adicionais de anti-alucinação — incorporar em SPEC-06
- OQ-02: Orange3 instalado no mesmo ambiente ou apenas gerar .ows para uso externo?
