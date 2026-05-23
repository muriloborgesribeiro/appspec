# ============================================================
#  diagnostico/context_processors.py
#  APPSPEC -- Injecao de contexto pedagogico em TODAS as views
#  Tecnologia: Django Context Processor
#  Contrato: SPEC-07 6.5
# ============================================================

from ml.pedagogico import (
    obter_contexto_pagina,
    CONTEXTO_PEDAGOGICO,
    DISCLAIMER_GLOBAL,
    PAINEL_POR_PAGINA,
    ANTI_ALUCINACAO,
    carregar_metricas_modelo,
)


def contexto_pedagogico(request):
    """
    Injeta contexto pedagogico em TODOS os templates automaticamente.
    Tecnologia: Django Context Processor.

    Registrado em settings.py TEMPLATES.OPTIONS.context_processors.
    """
    # Determinar pagina atual pela URL name
    pagina_atual = ""
    if request.resolver_match:
        pagina_atual = request.resolver_match.url_name or ""

    # Obter painel especifico desta pagina
    painel = PAINEL_POR_PAGINA.get(pagina_atual, PAINEL_POR_PAGINA.get("index", {}))

    # Carregar metricas do modelo
    metricas = carregar_metricas_modelo()

    # Tecnologias usadas (para badges no template)
    # Cada uma com explicação do papel NESTE projeto específico
    tecnologias_usadas = [
        {
            "nome": "Django 4.2",
            "cor": "primary",
            "papel": (
                "É o 'esqueleto' do sistema web. "
                "Recebe os dados do formulário, chama os motores de análise "
                "(Alvarado e KNN) e monta a página de resultado. "
                "Também salva cada avaliação no banco de dados SQLite."
            ),
            "arquivo": "diagnostico/views.py",
        },
        {
            "nome": "KNN (scikit-learn)",
            "cor": "success",
            "papel": (
                "É o algoritmo de Machine Learning que compara "
                "os dados do paciente com 782 casos reais "
                "e encontra os mais parecidos (vizinhos) para estimar "
                "a probabilidade de apendicite. Treinado com scikit-learn."
            ),
            "arquivo": "ml/knn_engine.py",
        },
        {
            "nome": "SVM (scikit-learn)",
            "cor": "dark",
            "papel": (
                "Support Vector Machine — algoritmo que busca a "
                "fronteira ótima de separação entre classes. "
                "Usa kernel para projetar dados em dimensão superior. "
                "Comparado ao KNN na tela de resultados."
            ),
            "arquivo": "ml/svm_engine.py",
        },
        {
            "nome": "Orange3",
            "cor": "warning",
            "papel": (
                "Ferramenta visual de análise de dados. "
                "Usada para validar o modelo KNN de forma interativa — "
                "o workflow .ows permite visualizar a árvore de decisão "
                "e a matriz de confusão sem escrever código."
            ),
            "arquivo": "orange/validacao_knn.ows",
        },
        {
            "nome": "pandas",
            "cor": "info",
            "papel": (
                "Biblioteca para manipulação de dados em tabelas. "
                "Usada para carregar os 782 pacientes do dataset, "
                "limpar dados faltantes (NaN), converter categorias "
                "(ex: 'yes'→1, 'no'→0) e preparar tudo para o KNN."
            ),
            "arquivo": "ml/preprocessamento.py",
        },
        {
            "nome": "joblib",
            "cor": "secondary",
            "papel": (
                "Salva o modelo KNN treinado em disco (.joblib). "
                "Sem isso, seria preciso re-treinar o modelo toda vez "
                "que o servidor reinicia. O joblib 'congela' o modelo "
                "para uso imediato."
            ),
            "arquivo": "ml/modelos/knn_model.joblib",
        },
        {
            "nome": "Matriz de Confusão",
            "cor": "danger",
            "papel": (
                "Tabela 2×2 que mostra onde o modelo acerta e erra. "
                "VP = acertou apendicite, VN = acertou saudável, "
                "FP = alarme falso, FN = doente não detectado (o pior). "
                "Gerada com sklearn.metrics."
            ),
            "arquivo": "ml/avaliador.py",
        },
        {
            "nome": "Curva ROC / Precision-Recall",
            "cor": "dark",
            "papel": (
                "Curvas que avaliam o modelo em todos os limiares de decisão "
                "possíveis. A ROC mede poder discriminatório (AUC-ROC); "
                "a PR é mais rigorosa com classes desbalanceadas (AP). "
                "O ponto ótimo de Youden é calculado mas não aplicado "
                "para preservar sensibilidade clínica."
            ),
            "arquivo": "ml/avaliador.py",
        },
    ]

    return {
        # Contexto global
        "disciplina": CONTEXTO_PEDAGOGICO["disciplina"],
        "professor": CONTEXTO_PEDAGOGICO["professor"],
        "instituicao": CONTEXTO_PEDAGOGICO["instituicao"],
        "versao_sistema": CONTEXTO_PEDAGOGICO["versao_sistema"],
        "tecnologias_usadas": tecnologias_usadas,
        "dataset_nome": CONTEXTO_PEDAGOGICO["dataset"],

        # Painel lateral
        "painel": painel,
        "pagina_atual": pagina_atual,

        # Disclaimer
        "disclaimer_global": DISCLAIMER_GLOBAL,

        # Metricas do modelo
        "metricas_modelo": metricas,
        "modelo_treinado": metricas.get("modelo_disponivel", False),
        "acuracia_modelo": round(metricas.get("acuracia_teste", 0) * 100, 1),
        "k_modelo": metricas.get("k_otimo", "N/A"),
    }
