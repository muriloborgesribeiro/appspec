---
name: redacao-academica
description: >
  Skill de redação acadêmica em português brasileiro para documentação técnica
  e material didático. Use quando precisar redigir: introduções de seção,
  explicações progressivas de conceitos técnicos, objetivos de aprendizagem,
  conclusões de módulo, glossários, legendas de código e qualquer texto
  que precisa soar acadêmico, claro e pedagogicamente estruturado.
  Especializada em traduzir jargão técnico para linguagem acessível a leigos
  mantendo rigor acadêmico.
---

# Redação Acadêmica
## Para Documentação Técnica e Material Didático

---

## Princípios Fundamentais

### 1. Granularidade Progressiva
Cada conceito deve ser apresentado em 3 camadas:

```
CAMADA 1 — Definição simples (1 frase, para qualquer pessoa)
CAMADA 2 — Explicação técnica (para alguém aprendendo)
CAMADA 3 — Detalhe de implementação (para quem vai usar)
```

**Exemplo — o que é um Model Django:**

Camada 1:
> "Um Model é uma classe Python que define a estrutura de uma tabela no banco de dados."

Camada 2:
> "Quando você cria um Model, o Django automaticamente cria a tabela correspondente
> no banco de dados SQLite. Cada atributo da classe vira uma coluna da tabela.
> Você nunca precisa escrever SQL diretamente — o Django faz isso por você."

Camada 3:
> "O Model herda de `django.db.models.Model`. Cada campo é uma instância de uma
> classe de campo (CharField, IntegerField, ForeignKey, etc.) que define o tipo
> da coluna e suas restrições. As migrations são arquivos Python gerados pelo
> Django que traduzem as mudanças no Model em comandos SQL."

---

### 2. Estrutura de Cada Seção

```
TÍTULO DA SEÇÃO
│
├── Objetivo de Aprendizagem
│   "Ao final desta seção, você será capaz de: ..."
│   (verbos mensuráveis: criar, configurar, identificar, aplicar)
│
├── Contexto e Motivação
│   Por que este conceito existe? Qual problema resolve?
│   Analogia com medicina ou cotidiano
│
├── Conceito Teórico
│   Explicação progressiva (3 camadas)
│   Diagrama ou esquema quando aplicável
│
├── Implementação no Projeto
│   "No projeto bdpratico, isso é feito em..."
│   Código com explicação linha por linha
│
├── Resultado Esperado
│   O que aparece na tela/terminal quando está correto
│
└── Conexão com o Próximo Conceito
    "Este conceito será a base para..."
```

---

### 3. Padrões de Linguagem

#### Introduzindo conceitos novos

```
✅ USAR:
"Um QuerySet é, em essência, uma consulta ao banco de dados representada como objeto Python."
"Em termos práticos, isso significa que..."
"Para entender X, é útil pensar em Y como analogia."
"A diferença fundamental entre A e B é..."

❌ EVITAR:
"Obviamente, X faz Y." (nunca presuma que é óbvio)
"É simples:" (o que é simples para um expert pode não ser para o aluno)
"Como todos sabem..." (o aluno pode não saber)
"Basta fazer X." (minimiza a dificuldade real)
```

#### Explicando código linha por linha

```
FORMATO OBRIGATÓRIO:
linha de código  ← [explicação do que faz]

EXEMPLO:
pessoa.objects.filter(ativo=True)  ← [busca no banco apenas pessoas com ativo=True]
                                       [equivale ao SQL: SELECT * FROM pessoa WHERE ativo=1]
                                       [retorna um QuerySet, não uma lista Python]
```

#### Analogias médicas — banco de analogias

| Conceito técnico | Analogia médica |
|---|---|
| Model | Formulário de prontuário em branco |
| Migration | Atualização do protocolo de preenchimento do prontuário |
| QuerySet | Resultado de busca no sistema de prontuários |
| View | Médico plantonista que recebe o pedido e decide o que fazer |
| Template | Laudo com campos pré-definidos a preencher |
| URL/rota | Ramal telefônico do hospital |
| settings.py | Manual de normas e procedimentos do hospital |
| INSTALLED_APPS | Departamentos habilitados no hospital |
| ForeignKey | Número do prontuário referenciado na guia de encaminhamento |
| autenticação | Crachá de acesso com senha |
| sessão | Tempo de validade do crachá de acesso |
| CRUD | Admissão (Create), Consulta (Read), Atualização (Update), Alta (Delete) |
| Bootstrap | Formulário padronizado do hospital |
| Pandas | Planilha de dados laboratoriais |
| KNN | Diagnóstico por semelhança com casos anteriores |
| overfitting | Médico que memoriza casos mas não raciocina clinicamente |
| validação cruzada | Estudo multicêntrico para validar um protocolo |
| matriz de confusão | Tabela de sensibilidade e especificidade |
| curva ROC | Curva ROC da medicina baseada em evidências |

---

### 4. Objetivos de Aprendizagem

Usar verbos da Taxonomia de Bloom:

```
NÍVEL 1 — Lembrar:    "Identificar os arquivos que compõem uma app Django"
NÍVEL 2 — Entender:   "Explicar a diferença entre Model, View e Template"
NÍVEL 3 — Aplicar:    "Criar um Model com os campos necessários"
NÍVEL 4 — Analisar:   "Comparar Class-Based Views com Function-Based Views"
NÍVEL 5 — Avaliar:    "Determinar qual tipo de view usar em cada situação"
NÍVEL 6 — Criar:      "Construir um CRUD completo para uma nova entidade"
```

---

### 5. Estrutura do Texto por Tipo de Conteúdo

#### Para CONFIGURAÇÃO (settings.py, urls.py):
```
Introdução: "A configuração é o ponto de partida de qualquer projeto Django..."
Propósito: "Este arquivo define as regras globais do sistema..."
Cada variável: Nome → O que faz → Por que importa → Valor padrão vs. modificado
```

#### Para MODELOS (models.py):
```
Introdução: "Os models definem como os dados são organizados no banco..."
Para cada model: Nome → O que representa → Campos → Relacionamentos → Métodos especiais
Nota pedagógica: "Note que não escrevemos SQL — o Django faz isso por nós."
```

#### Para VIEWS (views.py):
```
Introdução: "As views são o coração lógico da aplicação..."
Para cada view: Assinatura → Fluxo passo a passo → Dados recebidos → Dados enviados → Template usado
```

#### Para TEMPLATES (.html):
```
Introdução: "Os templates separam a apresentação da lógica..."
Estrutura: Tags usadas → Variáveis do contexto → Herança → Formulários
```

#### Para MACHINE LEARNING (exemplo02):
```
Introdução conceitual: o que é KNN sem matemática
Fluxo: Dados → Preparação → Treino → Avaliação → Uso
Cada métrica: O que mede → Como interpretar → Valor ideal
```

---

### 6. Introdução e Conclusão de Cada Seção

**Modelo de introdução:**
```
"Nesta seção, exploraremos [conceito]. Este é um dos pilares do desenvolvimento
Django pois [razão de importância]. Ao dominar [conceito], você será capaz de
[benefício prático para o aluno]. Começaremos por [primeiro ponto], avançando
progressivamente até [objetivo final da seção]."
```

**Modelo de conclusão:**
```
"Nesta seção construímos [o que foi feito]. Vimos que [conceito principal]
permite [benefício]. O arquivo [arquivo criado] agora contém [o que tem],
e ao acessar [URL] você pode verificar [resultado visual]. Na próxima seção,
utilizaremos [o que foi criado aqui] como base para [próximo conceito]."
```

---

### 7. Caixas de Destaque

```
┌─────────────────────────────────────┐
│  💡 CONCEITO-CHAVE                  │
│  [Definição em 1-2 frases]          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  ⚠️  ATENÇÃO                        │
│  [Erro comum ou armadilha]          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  🏥 ANALOGIA MÉDICA                 │
│  [Comparação com contexto médico]   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  👀 O QUE VER NA TELA               │
│  [Resultado visual esperado]        │
└─────────────────────────────────────┘
```

---

### 8. Glossário — Padrão de Entrada

```
TERMO
Definição simples: [1 frase, sem jargão]
Definição técnica: [como funciona internamente]
No projeto bdpratico: [onde e como aparece]
Analogia médica: [comparação com contexto de saúde]
Exemplo de uso:
    [linha de código com comentário]
```
