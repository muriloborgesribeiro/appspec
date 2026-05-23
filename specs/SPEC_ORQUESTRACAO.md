---
name: spec-orquestracao-comentador-total
version: "1.0"
description: >
  Especificação de orquestração para análise e comentário de 100% do código
  de qualquer sistema Python/Django. Instrui o Antigravity sobre como usar
  as skills incluídas neste pacote em sequência coordenada.
---

# Spec de Orquestração — Comentador Total de Sistemas
## Como analisar e comentar 100% do código de qualquer projeto

---

## Objetivo

Esta spec instrui o Antigravity a:
1. **Analisar** um sistema inteiro (engenharia reversa)
2. **Comentar** 100% do código com padrão pedagógico
3. **Revisar** comentários já existentes para garantir completude e qualidade
4. Produzir um **relatório de cobertura** que comprove que nenhum arquivo ficou sem comentário

---

## Skills Incluídas neste Pacote

| # | Skill | Arquivo | Papel |
|---|---|---|---|
| 1 | **engenharia-reversa-sistemas** | `engenharia-reversa-sistemas/SKILL.md` | Fase 1: Varredura, inventário, mapa de dependências |
| 2 | **comentador-pedagogico** | `comentador-pedagogico/SKILL.md` | Fase 2: Adicionar comentários pedagógicos ao código |
| 3 | **documentador-ml-dados** | `skill_documentador_ml_dados/skill_documentador_ml_dados.md` | Fase 2+: Conhecimento específico das páginas ML/dados |
| 4 | **redacao-academica** | `redacao-academica/SKILL.md` | Fase 2+: Padrão de linguagem, analogias, glossário |
| 5 | **django-framework-builder** | `django-framework-builder/SKILL.md` | Referência: Estrutura canônica do projeto, nomes, padrões |

---

## Protocolo de Execução — 4 Fases

### ╔══════════════════════════════════════════════╗
### ║  FASE 1 — ENGENHARIA REVERSA (Descoberta)   ║
### ╚══════════════════════════════════════════════╝

**Skill ativada:** `engenharia-reversa-sistemas`

**Ações obrigatórias:**

1. **Inventariar o projeto inteiro**
   - Varrer recursivamente todos os diretórios do projeto-alvo
   - Classificar cada arquivo por categoria (modelo, view, template, config, script, estático, migração)
   - Ignorar: `__pycache__/`, `.pyc`, `migrations/0*.py` (migrações auto-geradas), `.git/`, `node_modules/`

2. **Mapear dependências**
   - Para cada `.py`: extrair `import` e `from ... import`
   - Para cada `views.py`: identificar quais models, templates e URLs são usados
   - Para cada template `.html`: identificar `{% extends %}`, `{% include %}`, `{% url %}`, `{{ variáveis }}`
   - Para cada `urls.py`: mapear rota → view → template

3. **Detectar conceitos e padrões**
   - Usar o dicionário `CONCEITOS_DJANGO` da skill para identificar conceitos presentes
   - Classificar cada view como: FBV-Simples, FBV-Auth, FBV-Create, FBV-Pandas, FBV-Plotly, FBV-ML, CBV-List, CBV-Create, CBV-Update, CBV-Delete
   - Identificar bibliotecas externas usadas (Pandas, Plotly, sklearn, joblib, etc.)

4. **Gerar Relatório de Fase 1**
   ```
   RELATÓRIO DE ENGENHARIA REVERSA
   ================================
   Projeto: [nome]
   Total de arquivos analisáveis: [N]
   
   INVENTÁRIO:
   - Configuração: [lista]
   - Models: [lista]
   - Views: [lista]
   - URLs: [lista]
   - Templates: [lista]
   - Scripts: [lista]
   
   MAPA DE DEPENDÊNCIAS:
   [arquivo] → importa → [arquivo]
   [arquivo] → renderiza → [template]
   [url] → chama → [view] → usa → [model]
   
   CONCEITOS DETECTADOS:
   - [conceito]: encontrado em [arquivos]
   
   ARQUIVOS PARA COMENTAR (Fase 2):
   □ [arquivo 1] — [categoria] — [linhas de código]
   □ [arquivo 2] — [categoria] — [linhas de código]
   ...
   ```

---

### ╔══════════════════════════════════════════════╗
### ║  FASE 2 — COMENTÁRIO PEDAGÓGICO             ║
### ╚══════════════════════════════════════════════╝

**Skills ativadas:** `comentador-pedagogico` + `redacao-academica` + `documentador-ml-dados`

**REGRA ABSOLUTA — ANTI-REWRITE:**
```
⛔ NUNCA alterar código existente
⛔ NUNCA renomear funções, variáveis ou classes
⛔ NUNCA adicionar ou remover importações
⛔ NUNCA mudar indentação do código
✅ APENAS adicionar linhas de comentário
✅ Comentários em Python: # ...
✅ Comentários em HTML: <!-- ... -->
```

**Ordem de processamento (do mais fundamental ao mais complexo):**

```
CAMADA 1 — Configuração (processar primeiro)
  1. settings.py
  2. urls.py do projeto (raiz)

CAMADA 2 — Modelos (base de dados)
  3. models.py de cada app

CAMADA 3 — Administração
  4. admin.py de cada app

CAMADA 4 — Rotas
  5. urls.py de cada app

CAMADA 5 — Lógica (views)
  6. views.py de cada app (FBVs simples primeiro, depois CBVs, depois ML)

CAMADA 6 — Utilidades
  7. tables.py, forms.py, serializers.py, etc.

CAMADA 7 — Templates
  8. base.html (template base, se existir)
  9. Templates individuais (na ordem das URLs)

CAMADA 8 — Scripts
  10. Scripts utilitários na raiz ou em pastas auxiliares

CAMADA 9 — Machine Learning (se aplicável)
  11. Scripts/views de ML (usar documentador-ml-dados como referência)
```

**Para cada arquivo, aplicar este checklist:**

```
□ Cabeçalho do arquivo (nome, propósito, onde se encaixa no sistema)
□ Todas as importações explicadas
□ Toda definição de classe com bloco explicativo (═══)
□ Toda definição de função/método com bloco explicativo (═══)
□ Toda linha de ORM (objects.filter, objects.create, etc.)
□ Todo acesso a request.POST, request.GET, request.FILES
□ Todo bloco {% %} em templates
□ Toda variável {{ }} em templates
□ Toda linha de Pandas, Plotly ou sklearn
□ Analogias médicas onde aplicável (usar banco de analogias da redacao-academica)
□ Equivalentes SQL para operações ORM
```

**Padrão de linguagem (da skill redacao-academica):**
- Português brasileiro
- Granularidade progressiva (3 camadas quando necessário)
- Verbos da Taxonomia de Bloom para objetivos
- Analogias médicas do banco padronizado
- Nunca usar: "obviamente", "é simples", "basta fazer"

---

### ╔══════════════════════════════════════════════╗
### ║  FASE 3 — REVISÃO DE QUALIDADE              ║
### ╚══════════════════════════════════════════════╝

**Após comentar TODOS os arquivos, revisar cada um verificando:**

```
CHECKLIST DE REVISÃO POR ARQUIVO:
═════════════════════════════════
□ 1. INTEGRIDADE: O código original está 100% preservado? (Anti-Rewrite)
□ 2. COBERTURA: Toda definição de classe/função tem bloco ═══?
□ 3. COBERTURA: Toda importação tem comentário?
□ 4. COBERTURA: Todo ORM tem comentário com equivalente SQL?
□ 5. IDIOMA: Todos os comentários estão em português?
□ 6. CLAREZA: Os comentários fazem sentido para um iniciante?
□ 7. ANALOGIAS: Pelo menos 1 analogia médica por arquivo?
□ 8. INDENTAÇÃO: Comentários respeitam a indentação do código?
□ 9. CONSISTÊNCIA: Formato é consistente entre todos os arquivos?
□ 10. RESULTADO: Comentário "O que ver na tela" presente nas views?
```

**Se um comentário existente estiver:**
- **Incorreto** → Corrigir APENAS o texto do comentário (não o código)
- **Incompleto** → Expandir com mais detalhes
- **Ausente** → Adicionar seguindo o padrão
- **Em inglês** → Traduzir para português
- **Redundante** → Manter (preferir excesso a falta)

---

### ╔══════════════════════════════════════════════╗
### ║  FASE 4 — RELATÓRIO DE COBERTURA             ║
### ╚══════════════════════════════════════════════╝

**Gerar relatório final de cobertura:**

```
RELATÓRIO DE COBERTURA DE COMENTÁRIOS
======================================
Projeto: [nome]
Data: [data]
Total de arquivos processados: [N]

DETALHAMENTO POR ARQUIVO:
┌──────────────────────────────┬────────┬────────┬────────┬────────┐
│ Arquivo                      │ Linhas │ Coment.│ Cobert.│ Status │
├──────────────────────────────┼────────┼────────┼────────┼────────┤
│ settings.py                  │ 120    │ 45     │ 100%   │ ✅     │
│ models.py (app1)             │ 80     │ 35     │ 100%   │ ✅     │
│ views.py (app1)              │ 300    │ 120    │ 100%   │ ✅     │
│ ...                          │ ...    │ ...    │ ...    │ ...    │
└──────────────────────────────┴────────┴────────┴────────┴────────┘

TOTAL: [N] arquivos, [X] linhas de código, [Y] comentários adicionados
COBERTURA GLOBAL: [Z]%

CONCEITOS DOCUMENTADOS:
✅ Models e migrations
✅ QuerySets (objects.all, filter, create, get)
✅ FBVs (Function-Based Views)
✅ CBVs (Class-Based Views)
✅ Templates e herança
✅ Autenticação (login/logout)
✅ Formulários POST
✅ Pandas (DataFrame, CSV)
✅ Plotly (gráficos)
✅ KNN (treino, métricas)
[lista dos conceitos encontrados e documentados]

VERIFICAÇÃO ANTI-REWRITE:
✅ Nenhuma linha de código foi alterada
✅ Nenhuma importação foi adicionada/removida
✅ Nenhuma função foi renomeada
✅ Indentação preservada em 100% dos arquivos
```

---

## Como Usar Este Pacote

### Passo 1 — Preparar
```
1. Copiar a pasta pacote_skills_comentador/ para o projeto-alvo
   (ou extrair o ZIP na raiz do projeto)
2. As skills ficam em:
   pacote_skills_comentador/
   ├── SPEC_ORQUESTRACAO.md          ← ESTE ARQUIVO (ler primeiro)
   ├── engenharia-reversa-sistemas/
   │   └── SKILL.md
   ├── comentador-pedagogico/
   │   └── SKILL.md
   ├── skill_documentador_ml_dados/
   │   └── skill_documentador_ml_dados.md
   ├── redacao-academica/
   │   └── SKILL.md
   └── django-framework-builder/
       └── SKILL.md
```

### Passo 2 — Instruir o Antigravity
```
Prompt sugerido:

"Leia a SPEC_ORQUESTRACAO.md em [caminho]. 
 Ela contém instruções para analisar e comentar 100% do código deste projeto.
 Execute as 4 fases na ordem: Engenharia Reversa → Comentário → Revisão → Relatório.
 O projeto-alvo está em: [caminho do projeto]
 Leia cada skill referenciada na spec antes de começar cada fase."
```

### Passo 3 — Acompanhar
```
O Antigravity vai:
1. Ler esta spec
2. Ler cada skill necessária
3. Executar Fase 1 (inventário + mapa)
4. Executar Fase 2 (comentar arquivo por arquivo)
5. Executar Fase 3 (revisar qualidade)
6. Executar Fase 4 (gerar relatório de cobertura)
```

---

## Adaptação para Outros Projetos (Não-Django)

Este pacote foi criado com foco em Django, mas pode ser adaptado:

| Se o projeto usa... | Ajustar... |
|---|---|
| Flask | Substituir referências a views/urls por rotas Flask |
| FastAPI | Substituir por endpoints e schemas |
| Python puro | Usar apenas engenharia-reversa + comentador |
| ML/Data Science | Dar prioridade ao documentador-ml-dados |
| Frontend (JS/TS) | Adaptar padrão de comentário para `//` e `/* */` |

Para projetos não-Django:
- A skill `django-framework-builder` é apenas referência (pode ignorar)
- A skill `documentador-ml-dados` só se aplica se houver ML
- As skills `comentador-pedagogico`, `engenharia-reversa-sistemas` e `redacao-academica` funcionam para QUALQUER projeto Python

---

## Notas Importantes

1. **Tamanho do projeto**: Para projetos muito grandes (>50 arquivos), processar em lotes de 10 arquivos por turno do Antigravity
2. **Prioridade**: Se houver limitação de contexto, priorizar: models → views → templates → scripts
3. **Backup**: Recomenda-se fazer backup do projeto antes de executar (os comentários são adicionados in-place)
4. **Idioma**: Todos os comentários são em português brasileiro
5. **Analogias**: As analogias médicas são opcionais para projetos fora do contexto de saúde — substituir por analogias relevantes ao domínio
