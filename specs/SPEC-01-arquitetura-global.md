# Spec: APPSPEC-01 — Arquitetura Global

**Versão:** 1.0  
**Status:** Aprovada  
**Autor:** Neri  
**Data:** 2026-04-26  
**Depende de:** SPEC-00

---

## 1. Resumo

Define a arquitetura em camadas do APPSPEC, os componentes de cada camada, as interfaces públicas entre módulos e o fluxo de dados de ponta a ponta. Nenhum código é gerado aqui — este documento é a planta que todos os prompts seguintes constroem.

---

## 2. Contexto e Motivação

**Problema:** Sem arquitetura explícita, o Antigravity pode gerar módulos com responsabilidades sobrepostas, interfaces incompatíveis ou ordem de dependência errada.

**Por que agora:** SPEC-01 é o Nível 0 do Sandeco Method — deve existir antes de qualquer módulo ser gerado.

---

## 3. Goals

- [ ] G-01: Definir as 5 camadas do sistema com responsabilidades sem sobreposição
- [ ] G-02: Definir as interfaces públicas (inputs/outputs) de cada módulo
- [ ] G-03: Definir o fluxo de dados do formulário clínico até a exibição do resultado

| Métrica | Baseline | Target | Prazo |
|---|---|---|---|
| Módulos sem sobreposição de responsabilidade | — | 100% | Antes de SPEC-02 |
| Interfaces públicas documentadas | 0 | 1 por módulo | Esta spec |

---

## 4. Non-Goals

- NG-01: **NÃO** gera código nesta spec
- NG-02: **NÃO** define lógica interna dos módulos — apenas seus contratos externos
- NG-03: **NÃO** define SQL ou schema de banco — isso é SPEC-07

---

## 5. Usuários e Personas

**Primário:** Antigravity — consome esta spec para gerar os módulos na ordem correta  
**Secundário:** Professor/avaliador — usa o diagrama para entender a arquitetura

---

## 6. Requisitos Funcionais

### 6.1 As 5 Camadas do Sistema

```
┌─────────────────────────────────────────────────────────┐
│  CAMADA 5 — INTERFACE WEB (Django Templates + Bootstrap) │
│  base.html · index.html · resultado.html · como_funciona│
├─────────────────────────────────────────────────────────┤
│  CAMADA 4 — PEDAGÓGICA (conteúdo estático + referências) │
│  Painel lateral · Aba "Como funciona" · Documentação     │
├─────────────────────────────────────────────────────────┤
│  CAMADA 3 — DJANGO APP (views + models + forms + urls)   │
│  diagnostico/views.py · forms.py · models.py · urls.py  │
├─────────────────────────────────────────────────────────┤
│  CAMADA 2 — MOTOR ML (módulo puro, sem Django)           │
│  ml/alvarado.py · ml/knn_engine.py · ml/avaliador.py    │
├─────────────────────────────────────────────────────────┤
│  CAMADA 1 — DADOS (dataset + modelos serializados)       │
│  data/ · ml/modelos/ · setup.py · preprocessamento.py   │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Interfaces Públicas por Módulo

#### ml/alvarado.py
```python
# INPUT
calcular_alvarado(dados: dict) -> dict
# dados = {
#   "dor_migratoria": bool,
#   "anorexia": bool,
#   "nauseas_vomitos": bool,
#   "dor_fid": bool,
#   "descompressao_dolorosa": bool,
#   "temperatura": float,
#   "leucocitos": int,
#   "neutrofilia": bool
# }

# OUTPUT
# {
#   "score": int,           # 0-10
#   "classificacao": str,   # "baixo" | "moderado" | "alto"
#   "interpretacao": str,   # texto hardcoded com referência
#   "detalhamento": list,   # [{"criterio": str, "pontos": int, "referencia": str}]
# }
```

#### ml/knn_engine.py
```python
# TREINO
treinar_knn(X: DataFrame, y: Series, k: int) -> dict
# OUTPUT: {"modelo": KNeighborsClassifier, "k": int, "acuracia_treino": float}

# PREDIÇÃO
predizer(dados: dict, modelo_path: str) -> dict
# OUTPUT: {
#   "classe_predita": int,       # 0 = sem apendicite, 1 = apendicite
#   "probabilidade": float,      # 0.0 a 1.0
#   "k_vizinhos": int,           # k usado
#   "acuracia_modelo": float,    # acurácia no conjunto de teste
#   "distancias": list           # distâncias dos k vizinhos
# }
```

#### ml/avaliador.py
```python
# INPUT
avaliar_modelo(y_real: array, y_pred: array) -> dict
# OUTPUT: {
#   "vp": int, "fp": int, "fn": int, "vn": int,
#   "acuracia": float,
#   "sensibilidade": float,   # VP / (VP + FN)
#   "especificidade": float,  # VN / (VN + FP)
#   "vpp": float,             # VP / (VP + FP)
#   "vpn": float,             # VN / (VN + FN)
#   "imagem_matrix": str      # path para PNG da matriz de confusão
# }

gerar_orange_ows(dataset_path: str, output_path: str) -> None
# Gera o arquivo .ows do Orange3 com o pipeline KNN completo
```

#### ml/preprocessamento.py
```python
# INPUT
carregar_e_processar(raw_path: str) -> dict
# OUTPUT: {
#   "X_train": DataFrame, "X_test": DataFrame,
#   "y_train": Series,    "y_test": Series,
#   "features": list,     # nomes das features usadas
#   "n_pacientes": int,   # total após limpeza
#   "n_removidos": int    # linhas descartadas
# }
```

### 6.3 Fluxo Principal (Happy Path)

```
[setup.py]
  1. Baixa dataset Regensburg via ucimlrepo
  2. Salva em data/regensburg_raw.csv
  3. Chama preprocessamento.carregar_e_processar()
  4. Salva data/regensburg_processed.csv
  5. Treina KNN via knn_engine.treinar_knn()
  6. Serializa modelo em ml/modelos/knn_model.joblib
  7. Avalia modelo via avaliador.avaliar_modelo()
  8. Salva matriz de confusão em diagnostico/static/diagnostico/img/
  9. Gera validacao_knn.ows via avaliador.gerar_orange_ows()
 10. Imprime resumo didático com todas as métricas

[Usuário acessa localhost:8000]
  1. Django serve index.html com formulário de 8 campos clínicos
  2. Usuário preenche e submete
  3. views.py valida via forms.py (DadosClinicosForm)
  4. views.py chama alvarado.calcular_alvarado(dados)
  5. views.py chama knn_engine.predizer(dados, modelo_path)
  6. views.py salva Avaliacao no banco (SQLite)
  7. views.py renderiza resultado.html com ambos os resultados
  8. Painel pedagógico lateral mostra qual tecnologia foi usada nesta etapa
```

### 6.4 Fluxos Alternativos

**Modelo não treinado:**
1. views.py detecta ausência de knn_model.joblib
2. Redireciona para /setup-necessario/ com instrução: "Execute python setup.py"

**Score Alvarado inválido:**
1. alvarado.py lança AssertionError
2. views.py captura e exibe mensagem de erro sem expor stack trace

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|---|---|---|---|
| RNF-01 | Tempo de resposta da predição | < 500ms | KNN local é rápido |
| RNF-02 | Tempo do setup.py completo | < 60s | Download depende da rede |
| RNF-03 | Tamanho do modelo serializado | < 5MB | KNN com Regensburg (~780 amostras) |
| RNF-04 | Compatibilidade | Windows + Linux + macOS | Python 3.11 padrão |

---

## 8. Design e Interface

N/A — definido em SPEC-08. Regra: painel pedagógico lateral é fixo em todas as páginas.

---

## 9. Modelo de Dados

N/A — definido em SPEC-07.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|---|---|---|
| SPEC-00 | Obrigatória | Stack e convenções não definidos |
| ml/ → diagnostico/ | ml/ é importado por views.py | Views não funcionam sem ml/ |
| setup.py → ml/ | setup.py usa todos os módulos ml/ | Setup falha parcialmente |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---|---|---|
| Camadas chamadas fora de ordem | views.py importa ml/ que não existe | ImportError com mensagem clara |
| Interface pública quebrada | Output de alvarado.py sem chave "score" | KeyError capturado em views.py com log |
| Orange .ows não gerado | setup.py interrompido no passo 9 | Sistema funciona; .ows é opcional em runtime |

---

## 12. Segurança e Privacidade

Conforme SPEC-00.

---

## 13. Plano de Rollout

Esta spec é pré-requisito de todas as outras. Aprovada aqui, segue para SPEC-02.

---

## 14. Open Questions

- OQ-01: Quantas features do Regensburg usar no KNN? (definido em SPEC-02 após análise do dataset)
- OQ-02: Valor inicial de k? (definido em SPEC-04 por cross-validation)
