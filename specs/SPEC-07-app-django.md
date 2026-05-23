# Spec: APPSPEC-07 — App Django

**Versão:** 1.0  
**Status:** Aprovada  
**Autor:** Neri  
**Data:** 2026-04-26  
**Depende de:** SPEC-00, SPEC-01, SPEC-06

---

## 1. Resumo

Define e implementa a aplicação Django completa: `models.py` (banco de dados), `forms.py` (validação de entrada), `views.py` (lógica de cada página), `urls.py` (rotas) e `context_processors.py` (injeção do contexto pedagógico em todas as páginas). Django é a tecnologia central ensinada na disciplina e deve ser visível em cada aspecto desta implementação.

---

## 2. Contexto e Motivação

**Problema:** Django foi ensinado na disciplina como framework web para servir modelos de ML. O sistema deve demonstrar essa integração explicitamente — Models, Views, Templates e Forms devem estar todos presentes e funcionando.

**Por que agora:** Depende de SPEC-06 (contexto pedagógico a injetar) e seus módulos ml/ já definidos.

---

## 3. Goals

- [ ] G-01: Models Django para persistir avaliações (SQLite via Django ORM)
- [ ] G-02: Forms Django com validação clínica de range para todos os campos
- [ ] G-03: Views para todas as 6 páginas do sistema
- [ ] G-04: URLs nomeadas para todas as rotas
- [ ] G-05: Context processor injetando painel pedagógico em todas as páginas

| Métrica | Baseline | Target | Prazo |
|---|---|---|---|
| Views implementadas | 0 | 6 | SPEC-07 |
| Models com campos validados | 0 | 2 | SPEC-07 |
| URLs nomeadas | 0 | 6 | SPEC-07 |
| Context processor ativo | não | sim | SPEC-07 |

---

## 4. Non-Goals

- NG-01: **NÃO** tem autenticação ou login de usuários
- NG-02: **NÃO** usa Django REST Framework — apenas views HTML clássicas
- NG-03: **NÃO** tem API JSON pública
- NG-04: **NÃO** usa banco externo — SQLite Django padrão

---

## 5. Usuários e Personas

**Primário:** Browser do usuário — acessa localhost:8000  
**Secundário:** Antigravity — gera este código a partir desta spec

---

## 6. Requisitos Funcionais

### 6.1 Models (diagnostico/models.py)

```python
class Avaliacao(models.Model):
    """
    Registra cada avaliação clínica realizada.
    Tecnologia: Django ORM + SQLite — ensinado na disciplina.
    """
    # Dados clínicos de entrada
    dor_migratoria         = models.BooleanField()
    anorexia               = models.BooleanField()
    nauseas_vomitos        = models.BooleanField()
    dor_fid                = models.BooleanField()
    descompressao_dolorosa = models.BooleanField()
    temperatura            = models.FloatField()
    leucocitos             = models.IntegerField()
    neutrofilia            = models.BooleanField()

    # Resultados calculados
    score_alvarado         = models.IntegerField()
    classificacao_alvarado = models.CharField(max_length=20)
    predicao_knn           = models.IntegerField()          # 0 ou 1
    probabilidade_knn      = models.FloatField()
    confianca_knn          = models.CharField(max_length=20)

    # Metadados
    criado_em              = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avaliação Clínica"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Avaliação #{self.pk} — Alvarado: {self.score_alvarado} | KNN: {self.predicao_knn}"
```

### 6.2 Forms (diagnostico/forms.py)

```python
class DadosClinicosForm(forms.Form):
    """
    Formulário clínico com validação de range.
    Tecnologia: Django Forms — ensinado na disciplina.
    Mecanismo anti-alucinação #8: validação estrita de entrada.
    """
    dor_migratoria         = forms.BooleanField(required=False,
        label="Dor migratória para FID",
        help_text="Referência: Alvarado, 1986. DOI:10.1016/S0196-0644(86)80468-2")

    anorexia               = forms.BooleanField(required=False,
        label="Anorexia")

    nauseas_vomitos        = forms.BooleanField(required=False,
        label="Náuseas ou vômitos")

    dor_fid                = forms.BooleanField(required=False,
        label="Dor à palpação em FID (2 pontos)")

    descompressao_dolorosa = forms.BooleanField(required=False,
        label="Descompressão dolorosa (sinal de Blumberg)")

    temperatura            = forms.FloatField(
        label="Temperatura (°C)",
        min_value=35.0, max_value=42.0,
        help_text="Faixa fisiológica: 35.0 – 42.0 °C")

    leucocitos             = forms.IntegerField(
        label="Leucócitos (/mm³)",
        min_value=1000, max_value=50000,
        help_text="Faixa fisiológica: 1.000 – 50.000 /mm³")

    neutrofilia            = forms.BooleanField(required=False,
        label="Neutrofilia (desvio à esquerda no leucograma)")
```

### 6.3 Views (diagnostico/views.py)

```python
# VIEW 1: Página inicial — formulário
def index(request):
    # GET: exibe formulário
    # POST: valida e redireciona para avaliar()
    # Tecnologia visível: Django View + Django Form

# VIEW 2: Processamento e resultado
def avaliar(request):
    # Valida formulário
    # Chama ml.alvarado.calcular_alvarado(dados)
    # Chama ml.knn_engine.predizer(dados, modelo_path)
    # Persiste Avaliacao no banco via Django ORM
    # Renderiza resultado.html
    # Tecnologia visível: Django ORM + scikit-learn KNN

# VIEW 3: Métricas do modelo
def avaliacao_modelo(request):
    # Carrega métricas pré-calculadas do setup
    # Exibe matriz de confusão, sensibilidade, especificidade
    # Tecnologia visível: sklearn.metrics, matplotlib

# VIEW 4: Como funciona
def como_funciona(request):
    # Renderiza página estática pedagógica
    # Tecnologia visível: Django Template com contexto dinâmico

# VIEW 5: Documentação
def documentacao(request):
    # Renderiza documentação completa
    # Inclui referências DOI clicáveis

# VIEW 6: Histórico de avaliações
def historico(request):
    # Lista últimas 20 avaliações do banco
    # Tecnologia visível: Django ORM queryset
    avaliacoes = Avaliacao.objects.all()[:20]
```

### 6.4 URLs (diagnostico/urls.py)

```python
urlpatterns = [
    path('',                  views.index,           name='index'),
    path('avaliar/',          views.avaliar,          name='avaliar'),
    path('avaliacao-modelo/', views.avaliacao_modelo, name='avaliacao_modelo'),
    path('como-funciona/',    views.como_funciona,    name='como_funciona'),
    path('documentacao/',     views.documentacao,     name='documentacao'),
    path('historico/',        views.historico,        name='historico'),
]
```

### 6.5 Context Processor (diagnostico/context_processors.py)

```python
def contexto_pedagogico(request):
    """
    Injeta contexto pedagógico em TODOS os templates automaticamente.
    Tecnologia: Django Context Processor.
    """
    from django.conf import settings
    import os, json

    # Carrega métricas do modelo se disponíveis
    metricas_path = os.path.join(settings.BASE_DIR, 'ml', 'modelos', 'metricas.json')
    metricas = json.load(open(metricas_path)) if os.path.exists(metricas_path) else {}

    return {
        "disciplina": "Agentes Inteligentes",
        "professor": "Prof. Ronaldo Martins da Costa",
        "instituicao": "UFG — Instituto de Informática",
        "tecnologias_usadas": [
            {"nome": "Django 4.2",        "aula": "Aula 5", "cor": "primary"},
            {"nome": "KNN scikit-learn",  "aula": "Aula 5", "cor": "success"},
            {"nome": "Orange3",           "aula": "Aula 5", "cor": "warning"},
            {"nome": "pandas",            "aula": "Aula 5", "cor": "info"},
            {"nome": "joblib",            "aula": "Aula 5", "cor": "secondary"},
            {"nome": "Matriz Confusão",   "aula": "Aula 5", "cor": "danger"},
        ],
        "acuracia_modelo": metricas.get("acuracia_teste", "N/A"),
        "k_modelo": metricas.get("k", "N/A"),
        "dataset_nome": "Regensburg Pediatric Appendicitis",
        "modelo_treinado": os.path.exists(
            os.path.join(settings.BASE_DIR, 'ml', 'modelos', 'knn_model.joblib')
        ),
        "pagina_atual": request.resolver_match.url_name if request.resolver_match else "",
    }
```

### 6.6 Fluxo Principal (Happy Path)

```
1. Usuário acessa localhost:8000 → views.index() → index.html
2. Preenche formulário → POST → views.avaliar()
3. forms.DadosClinicosForm valida dados
4. ml.alvarado.calcular_alvarado(dados) → resultado_alvarado
5. ml.knn_engine.predizer(dados) → resultado_knn
6. Avaliacao.objects.create(**dados, **resultados) → salvo no SQLite
7. render(request, 'resultado.html', context) → exibe resultado
```

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|---|---|---|---|
| RNF-01 | Tempo de resposta da view avaliar() | < 500ms | KNN local é rápido |
| RNF-02 | Context processor em todas as views | 100% | Registrado em settings.py |
| RNF-03 | Erros de validação com mensagem clara | Sempre | Django Form errors em português |

---

## 8. Design e Interface

N/A — detalhado em SPEC-08.

---

## 9. Modelo de Dados

Conforme models.py acima. Migrações geradas automaticamente pelo setup.py via `manage.py migrate`.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|---|---|---|
| ml/alvarado.py (SPEC-03) | Obrigatória em views.py | view avaliar() falha |
| ml/knn_engine.py (SPEC-04) | Obrigatória em views.py | view avaliar() falha |
| ml/avaliador.py (SPEC-05) | Obrigatória em avaliacao_modelo() | Métricas não exibidas |
| SPEC-06 (contexto pedagógico) | Obrigatória no context_processor | Painel lateral vazio |
| knn_model.joblib | Obrigatória em runtime | view avaliar() retorna erro controlado |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---|---|---|
| Formulário inválido | Temperatura 50°C | Exibe erro de validação no campo, não avança |
| KNN não treinado | knn_model.joblib ausente | Exibe card "Modelo não disponível — execute setup.py" |
| Erro em ml/alvarado.py | AssertionError | View captura, exibe mensagem amigável, loga stack trace |
| Banco corrompido | SQLite locked | Captura DatabaseError, exibe "Erro de banco — reinicie o servidor" |
| POST sem dados | Form vazio enviado | Django Form retorna all errors, re-exibe formulário |

---

## 12. Segurança e Privacidade

- CSRF protection ativo (Django padrão) — `{% csrf_token %}` em todos os formulários
- DEBUG=True apenas em desenvolvimento — não expor em produção real
- Nenhum dado sensível em logs

---

## 13. Plano de Rollout

Gerado em SPEC-07. Testado com `python manage.py runserver` após setup.py concluído.

---

## 14. Open Questions

Nenhuma — todas as interfaces definidas nas specs anteriores.
