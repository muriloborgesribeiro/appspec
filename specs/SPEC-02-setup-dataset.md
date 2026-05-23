# Spec: APPSPEC-02 — Setup & Dataset

**Versão:** 1.0  
**Status:** Aprovada  
**Autor:** Neri  
**Data:** 2026-04-26  
**Depende de:** SPEC-00, SPEC-01

---

## 1. Resumo

Define e implementa o `setup.py` — ponto de entrada único que executa automaticamente: download do dataset Regensburg (UCI id=938), pré-processamento, treino do KNN, serialização do modelo, geração da matriz de confusão e criação do workflow Orange3. Ao final, o sistema está 100% pronto para rodar sem nenhuma intervenção manual adicional.

---

## 2. Contexto e Motivação

**Problema:** Sistemas acadêmicos frequentemente exigem configuração manual complexa que dificulta a apresentação e avaliação.

**Evidências:** O professor precisa ver o sistema funcionando rapidamente. O setup automático também demonstra boas práticas de engenharia de software.

**Por que agora:** setup.py é a fundação — sem ele, nenhum módulo ML pode ser testado.

---

## 3. Goals

- [ ] G-01: `python setup.py` executa tudo do zero sem intervenção do usuário
- [ ] G-02: Download automático do Regensburg via ucimlrepo com fallback para CSV local
- [ ] G-03: Logs pedagógicos numerados explicando cada etapa com a tecnologia usada
- [ ] G-04: Ao final, imprimir resumo com acurácia, sensibilidade, especificidade e k usado

| Métrica | Baseline | Target | Prazo |
|---|---|---|---|
| Etapas do setup executadas automaticamente | 0 | 10/10 | SPEC-02 |
| Logs didáticos impressos | 0 | ≥ 10 mensagens numeradas | SPEC-02 |
| Tempo total do setup (com boa internet) | — | < 60 segundos | SPEC-02 |

---

## 4. Non-Goals

- NG-01: **NÃO** sobe o servidor Django — o setup apenas prepara os artefatos
- NG-02: **NÃO** cria superusuário Django — não há autenticação
- NG-03: **NÃO** reprocessa se arquivos já existirem (idempotente)
- NG-04: **NÃO** usa argparse ou flags CLI — é um script simples de execução única

---

## 5. Usuários e Personas

**Primário:** Estudante/apresentador executando `python setup.py` antes da demonstração  
**Secundário:** Professor verificando que o sistema é autocontido

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|---|---|---|---|
| RF-01 | Download automático do Regensburg | Must | ucimlrepo.fetch_ucirepo(id=938) executado com sucesso |
| RF-02 | Detecção de dataset existente | Must | Se data/regensburg_raw.csv existe, pula download |
| RF-03 | Pré-processamento automático | Must | regensburg_processed.csv gerado em data/ |
| RF-04 | Treino do KNN e serialização | Must | knn_model.joblib gerado em ml/modelos/ |
| RF-05 | Geração da matriz de confusão | Must | confusion_matrix.png gerado em static/ |
| RF-06 | Geração do workflow Orange .ows | Should | validacao_knn.ows gerado em orange/ |
| RF-07 | Logs pedagógicos numerados | Must | ≥ 10 logs com tecnologia nomeada |
| RF-08 | Resumo final de métricas | Must | Acurácia, sensibilidade, especificidade impressos |
| RF-09 | Migrações Django automáticas | Must | manage.py migrate executado ao final |

### 6.2 Fluxo Principal (Happy Path)

```
[1]  Imprime banner do sistema e disciplina
[2]  Verifica dependências (scikit-learn, pandas, ucimlrepo, django, joblib)
[3]  Verifica se data/regensburg_raw.csv existe
     └─ NÃO: Baixa via ucimlrepo (loga "📥 Baixando Regensburg via ucimlrepo...")
     └─ SIM: Loga "✓ Dataset já disponível em data/"
[4]  Salva regensburg_raw.csv
[5]  Chama preprocessamento.carregar_e_processar() — loga features selecionadas
[6]  Salva regensburg_processed.csv
[7]  Chama knn_engine.treinar_knn() com cross-validation para encontrar melhor k
[8]  Serializa modelo em ml/modelos/knn_model.joblib
[9]  Chama avaliador.avaliar_modelo() — gera confusion_matrix.png
[10] Chama avaliador.gerar_orange_ows() — gera validacao_knn.ows
[11] Executa manage.py migrate (cria banco SQLite)
[12] Imprime resumo final didático
```

### 6.3 Modelo de Log Pedagógico

```
============================================================
  APPSPEC — Sistema de Apoio ao Diagnóstico de Apendicite
  Disciplina: Agentes Inteligentes — UFG
  Prof. Ronaldo Martins da Costa
============================================================

[1/10] Verificando dependências...
       ✓ scikit-learn 1.4 (tecnologia da aula 5 — KNN)
       ✓ pandas 2.x   (tecnologia da aula 5 — manipulação de dados)
       ✓ Django 4.2   (tecnologia da aula — framework web)
       ✓ ucimlrepo    (download do dataset público)
       ✓ joblib       (serialização do modelo treinado)
       ✓ Orange3      (tecnologia da aula — validação visual)

[2/10] Baixando dataset Regensburg Pediatric Appendicitis...
       Fonte: UCI Machine Learning Repository (id=938)
       Referência: Marcinkevics et al., 2023. DOI:10.5281/zenodo.7669442
       ✓ 780 pacientes carregados

[3/10] Pré-processando dados com pandas...
       Tecnologia: pandas DataFrame (ensinada na disciplina)
       Features selecionadas: [alvarado_score, wbc_count, neutrophilia, ...]
       ✓ 12 linhas removidas (valores ausentes)
       ✓ Normalização Min-Max aplicada
       ✓ Split: 70% treino | 15% teste | 15% validação

[4/10] Treinando KNN com scikit-learn...
       Tecnologia: sklearn.neighbors.KNeighborsClassifier
       Testando k = 3, 5, 7, 9, 11 via cross-validation...
       ✓ Melhor k encontrado: k=[k_otimo] (acurácia [X.X]%)

[5/10] Serializando modelo com joblib...
       ✓ Modelo salvo em ml/modelos/knn_model.joblib

[6/10] Avaliando modelo — Matriz de Confusão...
       Tecnologia: sklearn.metrics.confusion_matrix (ensinada na disciplina)
       VP=142  FP=18
       FN=22   VN=96
       ✓ Sensibilidade: 86.6% | Especificidade: 84.2%
       ✓ Imagem salva em static/diagnostico/img/confusion_matrix.png

[7/10] Gerando workflow Orange3...
       Tecnologia: Orange3 (ensinada na disciplina — validação visual)
       ✓ validacao_knn.ows salvo em orange/

[8/10] Configurando banco de dados Django...
       Tecnologia: Django ORM + SQLite (ensinado na disciplina)
       ✓ Migrações aplicadas

============================================================
  SETUP CONCLUÍDO COM SUCESSO
  Acurácia final KNN: 83.2%
  Sensibilidade: 86.6%   Especificidade: 84.2%
  Para iniciar: python manage.py runserver
  Acesse: http://localhost:8000
============================================================
```

### 6.4 Fluxos Alternativos

**Sem internet:**
1. ucimlrepo.fetch falha com ConnectionError
2. setup.py verifica data/regensburg_raw.csv
3. Se existe: usa CSV local, loga aviso
4. Se não existe: para e imprime instrução para download manual

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|---|---|---|---|
| RNF-01 | Idempotência | Total | Executar 2x não corrompe nada |
| RNF-02 | Tempo de execução | < 60s | Com internet de velocidade média |
| RNF-03 | Sem interação do usuário | 0 prompts | Totalmente automático |

---

## 8. Design e Interface

Saída no terminal conforme modelo de log da seção 6.3. Usar caracteres UTF-8 para ícones (✓, 📥, ⚠️).

---

## 9. Modelo de Dados — Pré-processamento do Regensburg

### Features selecionadas do dataset Regensburg:
```
alvarado_score          → Score Alvarado calculado pelos clínicos (0-10)
wbc_count               → Contagem de leucócitos
neutrophilia            → Neutrofilia (bool)
rebound_tenderness      → Descompressão dolorosa (bool)
migration_pain          → Dor migratória (bool)
anorexia                → Anorexia (bool)
nausea_vomiting         → Náusea/vômito (bool)
body_temperature        → Temperatura corporal (float)
appendix_diameter       → Diâmetro do apêndice no US (float)
free_fluids             → Fluido livre no US (bool)

TARGET: diagnosis       → 0 = sem apendicite | 1 = apendicite
```

### Split:
```python
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42)
X_test,  X_val,  y_test,  y_val  = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42)
```

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|---|---|---|
| SPEC-01 (interfaces ml/) | Obrigatória | setup.py não sabe o que chamar |
| ucimlrepo | Obrigatória no primeiro run | Fallback para CSV local |
| ml/preprocessamento.py | Obrigatória | Criado em SPEC-02 junto com setup.py |
| ml/knn_engine.py | Obrigatória | Criado em SPEC-04 |
| ml/avaliador.py | Obrigatória | Criado em SPEC-05 |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---|---|---|
| Dataset corrompido | CSV com colunas faltando | ValueError com lista de colunas esperadas |
| Modelo já existe | knn_model.joblib presente | Loga "✓ Modelo já treinado — pulando treino" |
| Orange3 não instalado | import orange falha | Loga aviso, pula passo 7, continua |
| migrate falha | Problema no settings.py | Para com mensagem: "Verifique appspec/settings.py" |

---

## 12. Segurança e Privacidade

- setup.py nunca transmite dados do usuário
- Download apenas do dataset público Regensburg — sem dados de pacientes reais

---

## 13. Plano de Rollout

Gerado em SPEC-02. Deve ser testado antes de avançar para SPEC-03.

---

## 14. Open Questions

- OQ-01: Incluir appendix_diameter e free_fluids (features de ultrassom) nas features do KNN? Enriquece o modelo mas o formulário web fica mais complexo. Decidir em SPEC-04.
