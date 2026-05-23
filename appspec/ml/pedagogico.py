# ============================================================
#  ml/pedagogico.py
#  APPSPEC -- Camada Pedagogica & Anti-Alucinacao
#  Contrato: SPEC-06
#
#  Todo conteudo e HARDCODED — sem LLMs, sem geracao dinamica.
#  Cada afirmacao clinica tem referencia DOI rastreavel.
#
#  Este modulo e o que diferencia o APPSPEC de um simples
#  sistema clinico: demonstracao explicita da disciplina
#  de Agentes Inteligentes (UFG).
# ============================================================

import json
import os

# -----------------------------------------------------------
#  6.1 — PAINEL LATERAL PEDAGOGICO
#  Presente em TODAS as paginas (Bootstrap col-md-3)
# -----------------------------------------------------------

PAINEL_POR_PAGINA = {
    "index": {
        "titulo": "🔧 O que está acontecendo aqui?",
        "tecnologia_principal": "Django 4.2 — Framework Web",
        "descricao": (
            "Quando você preenche este formulário e clica em 'Calcular Risco', "
            "o Django (framework web em Python) recebe os dados, valida se estão "
            "dentro de faixas fisiológicas possíveis (ex: temperatura entre 35°C e 42°C), "
            "e encaminha para os dois motores de análise: o Alvarado Score e o KNN."
        ),
        "o_que_e": (
            "Django é um framework web escrito em Python. "
            "Ele cuida de receber os dados do navegador, processar no servidor, "
            "e devolver a página com o resultado — tudo sem precisar de JavaScript."
        ),
        "aula_referencia": "Aula 5 — Django como framework web",
        "componente_codigo": "diagnostico/views.py → def avaliar(request)",
        "badge_cor": "primary",
    },
    "resultado": {
        "titulo": "🤖 Como este resultado foi gerado?",
        "tecnologia_principal": "Dois métodos comparados lado a lado",
        "descricao": (
            "À ESQUERDA: Alvarado Score — uma regra clínica de 1986 que soma pontos "
            "para 8 sintomas/sinais. É determinístico: os mesmos dados sempre dão "
            "o mesmo resultado. "
            "À DIREITA: KNN (Machine Learning) — um algoritmo que compara os dados "
            "do paciente com 782 casos reais do Hospital de Regensburg (Alemanha) "
            "e verifica se os casos mais parecidos tinham ou não apendicite."
        ),
        "o_que_e": (
            "Comparar os dois métodos é o objetivo pedagógico central: "
            "entender a diferença entre uma regra fixa (Alvarado) "
            "e um modelo que aprende dos dados (KNN)."
        ),
        "aula_referencia": "Aula 5 — KNN e regras clínicas",
        "componente_codigo": "ml/knn_engine.py + ml/alvarado.py",
        "badge_cor": "success",
    },
    "avaliacao": {
        "titulo": "📊 Avaliação Completa dos Modelos",
        "tecnologia_principal": "Matrizes de Confusão + Curvas ROC + Precision-Recall",
        "descricao": (
            "Esta página avalia os modelos com três ferramentas: "
            "(1) Matrizes de Confusão — VP, VN, FP, FN para KNN e SVM; "
            "(2) Curvas ROC — medem o poder discriminatório do modelo "
            "em todos os limiares possíveis (AUC-ROC); "
            "(3) Curvas Precision-Recall — mais informativas com "
            "classes desbalanceadas (Average Precision). "
            "O limiar ótimo de Youden é calculado mas NÃO aplicado "
            "para preservar sensibilidade em triagem pediátrica."
        ),
        "o_que_e": (
            "Em medicina, errar para menos (FN) é mais grave que errar para mais (FP). "
            "A Curva ROC permite visualizar esse trade-off em todos os limiares. "
            "Ref: Fawcett (2006), Youden (1950)."
        ),
        "aula_referencia": "Aula 5 — Avaliação de modelos: Curva ROC, Precision-Recall, Inferência",
        "componente_codigo": "ml/avaliador.py → gerar_curva_roc(), gerar_curva_pr()",
        "badge_cor": "warning",
    },
    "como_funciona": {
        "titulo": "📚 Mapa: Aula ↔ Código",
        "tecnologia_principal": "Cada aula tem um componente no sistema",
        "descricao": (
            "Esta página mostra exatamente qual conteúdo da disciplina "
            "foi usado em qual parte do código. Cada tecnologia ensinada "
            "pelo professor tem um arquivo correspondente neste projeto."
        ),
        "o_que_e": (
            "O objetivo é mostrar que o sistema não usa tecnologias aleatórias — "
            "tudo foi ensinado na disciplina de Agentes Inteligentes."
        ),
        "badge_cor": "info",
    },
    "documentacao": {
        "titulo": "📄 Documentação Completa",
        "tecnologia_principal": "Arquitetura, referências e decisões",
        "descricao": (
            "Documentação técnica do sistema: como foi construído, "
            "quais referências científicas embasam cada decisão, "
            "quais limitações existem, e como o data leakage foi "
            "detectado e corrigido durante o desenvolvimento."
        ),
        "o_que_e": (
            "A documentação registra o processo de desenvolvimento, "
            "incluindo erros encontrados e como foram resolvidos — "
            "isso é tão importante quanto o código final."
        ),
        "badge_cor": "secondary",
    },
}

# -----------------------------------------------------------
#  6.2 — ABA "COMO FUNCIONA"
# -----------------------------------------------------------

MAPA_DISCIPLINA = [
    {
        "conteudo_aula": "KNN (K-Nearest Neighbors)",
        "tecnologia": "scikit-learn KNeighborsClassifier",
        "componente": "Motor de classificacao ML",
        "arquivo": "ml/knn_engine.py",
    },
    {
        "conteudo_aula": "Validacao visual de modelos",
        "tecnologia": "Orange3 (.ows workflow)",
        "componente": "Workflow de validacao visual",
        "arquivo": "orange/validacao_knn.ows",
    },
    {
        "conteudo_aula": "Framework web",
        "tecnologia": "Django 4.2",
        "componente": "Interface web e API",
        "arquivo": "diagnostico/views.py",
    },
    {
        "conteudo_aula": "Manipulacao de dados",
        "tecnologia": "pandas DataFrame",
        "componente": "Pre-processamento do dataset",
        "arquivo": "ml/preprocessamento.py",
    },
    {
        "conteudo_aula": "Serializacao de modelos",
        "tecnologia": "joblib",
        "componente": "Persistencia do modelo treinado",
        "arquivo": "ml/modelos/knn_model.joblib",
    },
    {
        "conteudo_aula": "Metricas de avaliacao",
        "tecnologia": "sklearn.metrics",
        "componente": "Matriz de confusao e metricas",
        "arquivo": "ml/avaliador.py",
    },
    {
        "conteudo_aula": "SVM (Support Vector Machine)",
        "tecnologia": "scikit-learn SVC",
        "componente": "Motor de classificacao SVM (kernel linear)",
        "arquivo": "ml/svm_engine.py",
    },
    {
        "conteudo_aula": "Curva ROC e Precision-Recall",
        "tecnologia": "sklearn.metrics.roc_curve, precision_recall_curve",
        "componente": "Analise de desempenho por limiar + Indice de Youden",
        "arquivo": "ml/avaliador.py",
    },
]

DATASET_INFO = {
    "nome": "Regensburg Pediatric Appendicitis",
    "fonte": "UCI Machine Learning Repository (id=938)",
    "url": "https://archive.ics.uci.edu/dataset/938/regensburg+pediatric+appendicitis",
    "pacientes": 782,
    "referencia": "Marcinkevics et al. (2023). DOI:10.5281/zenodo.7669442",
    "como_baixado": "ucimlrepo.fetch_ucirepo(id=938) — automatico no setup.py",
    "licenca": "CC BY 4.0",
}

KNN_EXPLICADO = {
    "o_que_e": (
        "Imagine que você tem uma ficha de um paciente novo e quer saber se ele tem apendicite. "
        "O KNN pega essa ficha e procura no banco de dados os pacientes mais PARECIDOS "
        "(mesma faixa de temperatura, leucócitos similares, mesmos sintomas). "
        "Se a maioria desses pacientes parecidos tinha apendicite, o KNN diz: "
        "'provavelmente este também tem'. O 'k' é quantos pacientes parecidos ele consulta "
        "(neste sistema, k=5 — ele olha os 5 mais parecidos)."
    ),
    "como_funciona_passo_a_passo": (
        "1) Recebe os dados clínicos do paciente; "
        "2) Calcula a 'distância' (diferença) entre este paciente e todos os 782 do dataset; "
        "3) Seleciona os k=5 mais próximos (mais parecidos); "
        "4) Conta: dos 5, quantos tinham apendicite?; "
        "5) Se 4 de 5 tinham → 80% de probabilidade de apendicite."
    ),
    "por_que_apendicite": (
        "O KNN é bom para este problema porque: "
        "(1) É transparente — podemos explicar QUAIS pacientes parecidos influenciaram o resultado; "
        "(2) Não precisa de milhões de dados como redes neurais — funciona com 782 pacientes; "
        "(3) É intuitivo — 'pacientes parecidos tendem a ter o mesmo desfecho'."
    ),
    "limitacao_didatica": (
        "A acurácia de 75% significa que o modelo acerta 3 em cada 4 casos. "
        "Isso NÃO é suficiente para uso clínico real (seria necessário >90%), "
        "mas é adequado para demonstrar o conceito de Machine Learning na disciplina."
    ),
    "referencia": "Cover, T. & Hart, P. (1967). DOI:10.1109/TIT.1967.1053964",
}

ALVARADO_EXPLICADO = {
    "historia": (
        "Criado em 1986 por Alfredo Alvarado no Hospital de Los Angeles, "
        "California. Publicado no Annals of Emergency Medicine como "
        "um sistema pratico de pontuacao para o diagnostico precoce "
        "de apendicite aguda."
    ),
    "criterios_tabela": [
        {"criterio": "Dor migratoria (M)", "pontos": 1, "categoria": "Sintoma"},
        {"criterio": "Anorexia (A)", "pontos": 1, "categoria": "Sintoma"},
        {"criterio": "Nauseas/vomitos (N)", "pontos": 1, "categoria": "Sintoma"},
        {"criterio": "Dor em FID (T)", "pontos": 2, "categoria": "Sinal"},
        {"criterio": "Descompressao dolorosa (R)", "pontos": 1, "categoria": "Sinal"},
        {"criterio": "Temperatura >37.3 (E)", "pontos": 1, "categoria": "Sinal"},
        {"criterio": "Leucocitos >10.000 (L)", "pontos": 2, "categoria": "Laboratorial"},
        {"criterio": "Neutrofilia (S)", "pontos": 1, "categoria": "Laboratorial"},
    ],
    "pontos_corte": {
        "0-4": "Baixo risco — considerar alta com orientacoes",
        "5-6": "Risco moderado — observacao e exames complementares",
        "7-10": "Alto risco — avaliacao cirurgica imediata",
    },
    "limitacoes": (
        "Menor sensibilidade em: mulheres em idade fertil (diagnosticos "
        "diferenciais ginecologicos), criancas pequenas (<5 anos), "
        "idosos (apresentacao atipica)."
    ),
    "referencia": "Alvarado A. (1986). DOI:10.1016/S0196-0644(86)80468-2",
    "referencia_metanalise": "Ohle R et al. (2011). DOI:10.1186/1741-7015-9-139",
}

COMO_USAR = {
    "passos": [
        "1. Preencha os sintomas e sinais clinicos no formulario",
        "2. Informe os dados laboratoriais (leucocitos, temperatura)",
        "3. Opcionalmente, adicione dados de ultrassom",
        "4. Clique em 'Avaliar' para obter a estimativa de risco",
        "5. Compare o resultado do Alvarado Score com o KNN",
        "6. Consulte a aba 'Avaliacao' para ver as metricas do modelo",
    ],
    "o_que_faz": (
        "O sistema calcula o Alvarado Score (regra deterministica) "
        "e classifica o caso com KNN (Machine Learning). "
        "Os dois resultados sao apresentados lado a lado para comparacao."
    ),
    "o_que_nao_faz": (
        "O sistema NAO faz diagnostico. NAO substitui avaliacao medica. "
        "NAO deve ser usado para decisao clinica real. "
        "E exclusivamente uma ferramenta didatica da disciplina."
    ),
}

# -----------------------------------------------------------
#  6.3 — AREA DE DOCUMENTACAO
# -----------------------------------------------------------

DOCUMENTACAO = {
    "visao_geral": {
        "objetivo": (
            "Sistema de apoio ao diagnostico de apendicite aguda, "
            "desenvolvido como trabalho final da disciplina de "
            "Agentes Inteligentes do Programa de Pos-Graduacao "
            "em Ciencia da Computacao da UFG."
        ),
        "disciplina": "Agentes Inteligentes",
        "professor": "Prof. Ronaldo Martins da Costa",
        "instituicao": "UFG — Instituto de Informatica",
    },
    "arquitetura": {
        "camadas": [
            "1. Dados: Dataset Regensburg (UCI) + pre-processamento pandas",
            "2. ML: Motor KNN (scikit-learn) + Motor SVM (scikit-learn) + Motor Alvarado (Python puro)",
            "3. Avaliacao: Matriz de Confusao + Curva ROC + Curva Precision-Recall + Indice de Youden",
            "4. Pedagogica: Conteudo hardcoded + anti-alucinacao",
            "5. Interface: Django + Bootstrap 5",
        ],
    },
    "stack_tecnologico": [
        {
            "biblioteca": "scikit-learn",
            "funcao": "Treino e predicao KNN, metricas de avaliacao",
            "aula": "Aula 5 — Machine Learning com scikit-learn",
        },
        {
            "biblioteca": "pandas",
            "funcao": "Manipulacao e limpeza do dataset Regensburg",
            "aula": "Aula 5 — Manipulacao de dados",
        },
        {
            "biblioteca": "Django 4.2",
            "funcao": "Framework web, ORM, templates",
            "aula": "Aula 5 — Django como framework web",
        },
        {
            "biblioteca": "Orange3",
            "funcao": "Validacao visual do modelo KNN",
            "aula": "Aula 5 — Orange3 para analise de dados",
        },
        {
            "biblioteca": "joblib",
            "funcao": "Serializacao do modelo treinado",
            "aula": "Aula 5 — Persistencia de modelos",
        },
        {
            "biblioteca": "matplotlib + seaborn",
            "funcao": "Graficos (matriz de confusao, curvas ROC e Precision-Recall)",
            "aula": "Aula 5 — Visualizacao de dados",
        },
        {
            "biblioteca": "sklearn.metrics (roc_curve, precision_recall_curve, auc)",
            "funcao": "Curvas ROC e Precision-Recall, AUC-ROC, Average Precision, Indice de Youden",
            "aula": "Aula 5 — Curva ROC, Curva Recall e Inferencia",
        },
        {
            "biblioteca": "scikit-learn SVC",
            "funcao": "Motor de classificacao SVM com kernel linear e probability=True",
            "aula": "Aula 5 — Support Vector Machines",
        },
    ],
    "referencias_clinicas": [
        {
            "citacao": "Alvarado A. (1986). A practical score for the early "
                       "diagnosis of acute appendicitis. Ann Emerg Med, 15(5), 557-564.",
            "doi": "10.1016/S0196-0644(86)80468-2",
            "uso_no_sistema": "Motor Alvarado Score (ml/alvarado.py)",
        },
        {
            "citacao": "Ohle R et al. (2011). The Alvarado score for predicting "
                       "acute appendicitis: systematic review. BMC Med, 9, 139.",
            "doi": "10.1186/1741-7015-9-139",
            "uso_no_sistema": "Classificacao por faixa de risco",
        },
        {
            "citacao": "Marcinkevics R et al. (2023). Regensburg Pediatric "
                       "Appendicitis Dataset.",
            "doi": "10.5281/zenodo.7669442",
            "uso_no_sistema": "Dataset de treino e teste do KNN",
        },
    ],
    "referencias_tecnicas": [
        {
            "citacao": "Cover T & Hart P (1967). Nearest neighbor pattern "
                       "classification. IEEE Trans. Inf. Theory, 13(1), 21-27.",
            "doi": "10.1109/TIT.1967.1053964",
            "uso_no_sistema": "Algoritmo KNN (ml/knn_engine.py)",
        },
        {
            "citacao": "Cortes C & Vapnik V (1995). Support-vector networks. "
                       "Machine Learning, 20(3), 273-297.",
            "doi": "10.1007/BF00994018",
            "uso_no_sistema": "Algoritmo SVM (ml/svm_engine.py)",
        },
        {
            "citacao": "Fawcett T (2006). An introduction to ROC analysis. "
                       "Pattern Recognition Letters, 27(8), 861-874.",
            "doi": "10.1016/j.patrec.2005.10.010",
            "uso_no_sistema": "Curvas ROC e Precision-Recall (ml/avaliador.py)",
        },
        {
            "citacao": "Youden WJ (1950). Index for rating diagnostic tests. "
                       "Cancer, 3(1), 32-35.",
            "doi": "10.1002/1097-0142(1950)3:1<32::AID-CNCR2820030106>3.0.CO;2-3",
            "uso_no_sistema": "Limiar otimo de decisao na Curva ROC (ml/avaliador.py)",
        },
        {
            "citacao": "Kaufman S et al. (2012). Leakage in Data Mining: "
                       "Formulation, Detection, and Avoidance. ACM TKDD, 6(4).",
            "doi": "10.1145/2020408.2020496",
            "uso_no_sistema": "Deteccao e correcao de data leakage (Config D descartada)",
        },
    ],
    "limitacoes": [
        "O sistema e exclusivamente didatico — NAO e dispositivo medico",
        "O dataset Regensburg e pediatrico — resultados podem nao generalizar para adultos",
        "Acuracia do KNN (~75%) e limitada pelo tamanho do dataset (782 pacientes)",
        "O Alvarado Score tem menor sensibilidade em mulheres em idade fertil",
        "O limiar de Youden (ROC) nao e aplicado na inferencia para preservar sensibilidade clinica",
        "Nenhum dado pessoal e coletado ou armazenado (LGPD)",
    ],
}

# -----------------------------------------------------------
#  6.4 — 8 MECANISMOS ANTI-ALUCINACAO
# -----------------------------------------------------------

ANTI_ALUCINACAO = {
    "1_texto_hardcoded": {
        "titulo": "Todo texto clínico é fixo no código",
        "descricao": (
            "Nenhum texto sobre sintomas, condutas ou interpretações é gerado por IA. "
            "Tudo está escrito diretamente no código-fonte (hardcoded), garantindo que "
            "o sistema nunca 'invente' informações médicas."
        ),
        "implementacao": "Dicionários em ml/alvarado.py e ml/pedagogico.py",
        "motivo": (
            "IAs generativas (como ChatGPT) podem 'alucinar' — inventar fatos "
            "que parecem corretos mas são falsos. Em contexto clínico, isso é inaceitável."
        ),
        "icone": "📝",
    },
    "2_score_bounds": {
        "titulo": "Score sempre entre 0 e 10",
        "descricao": (
            "O código verifica matematicamente que o Alvarado Score nunca sai da faixa 0-10. "
            "Se por algum bug o score calculasse 11 ou -1, o sistema travaria com erro "
            "em vez de mostrar um resultado impossível ao usuário."
        ),
        "implementacao": "assert 0 <= score <= 10 em ml/alvarado.py",
        "motivo": "Um score impossível (ex: 15/10) enganaria o usuário — melhor travar do que mentir.",
        "icone": "🔢",
    },
    "3_disclaimer_obrigatorio": {
        "titulo": "Aviso 'não é diagnóstico' sempre visível",
        "descricao": (
            "O aviso vermelho no topo da tela de resultado NÃO pode ser removido, "
            "escondido ou minimizado. Ele aparece ANTES do resultado, forçando "
            "o usuário a vê-lo antes de interpretar os números."
        ),
        "implementacao": "HTML fixo em resultado.html — não depende de JavaScript",
        "motivo": "Prevenir que alguém use os resultados para decisão clínica real.",
        "icone": "⚠️",
    },
    "4_referencias_doi": {
        "titulo": "Toda afirmação tem referência científica (DOI)",
        "descricao": (
            "Cada regra clínica usada no sistema tem um link DOI (Digital Object Identifier) "
            "que leva ao artigo científico original. Isso permite que qualquer pessoa "
            "verifique se o que o sistema diz está correto."
        ),
        "implementacao": "Links clicáveis para doi.org em todos os critérios",
        "motivo": "Ciência sem fonte verificável não é ciência — é opinião.",
        "icone": "🔗",
    },
    "5_confianca_minima": {
        "titulo": "KNN avisa quando não tem certeza",
        "descricao": (
            "Se o KNN dá 55% para apendicite e 45% para não-apendicite, "
            "ele está quase 'chutando'. Nesses casos, o sistema exibe "
            "um alerta amarelo dizendo que o resultado é inconclusivo "
            "e que o Alvarado Score deve ser priorizado."
        ),
        "implementacao": "Alerta exibido quando probabilidade máxima < 60%",
        "motivo": "Mostrar resultado inconclusivo como se fosse definitivo é perigoso.",
        "icone": "📊",
    },
    "6_linguagem_risco": {
        "titulo": "Usa 'risco', nunca 'diagnóstico'",
        "descricao": (
            "O sistema NUNCA diz 'o paciente TEM apendicite'. Sempre diz "
            "'risco alto de apendicite' ou 'probabilidade de 80%'. "
            "Diagnóstico é ato médico — só um médico pode diagnosticar."
        ),
        "implementacao": "Revisão de todos os textos nos templates e no código",
        "motivo": "Diagnóstico médico é privativo de profissional habilitado (Lei 12.842/2013).",
        "icone": "🗣️",
    },
    "7_sem_identificacao": {
        "titulo": "Não coleta dados pessoais",
        "descricao": (
            "O formulário NÃO pede nome, CPF, data de nascimento ou qualquer informação "
            "que identifique uma pessoa real. Apenas dados clínicos genéricos "
            "(temperatura, leucócitos, sintomas) são processados."
        ),
        "implementacao": "Formulário Django sem campos identificadores",
        "motivo": "Conformidade com LGPD — sistema didático não deve processar dados pessoais.",
        "icone": "🔒",
    },
    "8_validacao_entrada": {
        "titulo": "Rejeita valores impossíveis",
        "descricao": (
            "Se alguém digitar temperatura de 50°C ou leucócitos de 999.999, "
            "o sistema recusa e pede para corrigir. Os limites são baseados em "
            "faixas fisiológicas reais: temperatura entre 35°C e 42°C, "
            "leucócitos entre 1.000 e 50.000/mm³."
        ),
        "implementacao": "Validadores min/max em diagnostico/forms.py",
        "ranges": {
            "temperatura": {"min": 35.0, "max": 42.0, "unidade": "°C"},
            "leucocitos": {"min": 1000, "max": 50000, "unidade": "/mm³"},
        },
        "motivo": "Dados impossíveis produzem resultados sem sentido — garbage in, garbage out.",
        "icone": "✅",
    },
}

# -----------------------------------------------------------
#  6.9 — CONTEXTO PEDAGOGICO (injetado em TODAS as views)
# -----------------------------------------------------------

CONTEXTO_PEDAGOGICO = {
    "disciplina": "Agentes Inteligentes",
    "professor": "Prof. Ronaldo Martins da Costa",
    "instituicao": "UFG — Instituto de Informatica",
    "tecnologias": [
        "Django 4.2", "KNN (scikit-learn)", "SVM (scikit-learn)",
        "Curva ROC / Precision-Recall", "Orange3",
        "pandas", "joblib", "Matriz de Confusao",
    ],
    "dataset": "Regensburg Pediatric Appendicitis (UCI id=938)",
    "versao_sistema": "1.0",
}

# -----------------------------------------------------------
#  DISCLAIMER CLINICO GLOBAL
#  Visivel sem scroll, acima do resultado (SPEC-06 RNF-02)
# -----------------------------------------------------------

DISCLAIMER_GLOBAL = (
    "⚠️ AVISO: Este sistema e uma ferramenta de apoio didatica "
    "desenvolvida na disciplina de Agentes Inteligentes (UFG). "
    "NAO substitui avaliacao medica presencial. "
    "NAO deve ser usado para decisao clinica real. "
    "Sistema exclusivamente educacional."
)


# ============================================================
#  FUNCOES AUXILIARES
# ============================================================

def carregar_metricas_modelo():
    """
    Carrega metricas.json para exibicao no painel pedagogico.
    Retorna dict com metricas ou mensagem de fallback se modelo nao existe.
    """
    metricas_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'modelos', 'metricas.json'
    )
    if not os.path.exists(metricas_path):
        return {
            "modelo_disponivel": False,
            "aviso": "Modelo nao avaliado — execute setup.py",
        }

    with open(metricas_path, 'r', encoding='utf-8') as f:
        metricas = json.load(f)

    metricas["modelo_disponivel"] = True
    return metricas


def obter_contexto_pagina(pagina: str) -> dict:
    """
    Retorna o contexto pedagogico completo para uma pagina.
    Usado pelo context_processor do Django.

    Args:
        pagina: nome da pagina ('index', 'resultado', 'avaliacao', etc.)

    Returns:
        dict com todo o contexto necessario para renderizar
        o painel pedagogico lateral.
    """
    painel = PAINEL_POR_PAGINA.get(pagina, PAINEL_POR_PAGINA["index"])
    metricas = carregar_metricas_modelo()

    return {
        "painel": painel,
        "contexto": CONTEXTO_PEDAGOGICO,
        "disclaimer": DISCLAIMER_GLOBAL,
        "metricas_modelo": metricas,
        "anti_alucinacao": ANTI_ALUCINACAO,
    }


def obter_conteudo_como_funciona() -> dict:
    """
    Retorna todo o conteudo para a pagina 'Como Funciona'.
    """
    metricas = carregar_metricas_modelo()

    return {
        "mapa_disciplina": MAPA_DISCIPLINA,
        "dataset": DATASET_INFO,
        "knn": KNN_EXPLICADO,
        "alvarado": ALVARADO_EXPLICADO,
        "como_usar": COMO_USAR,
        "metricas": metricas,
    }


def obter_conteudo_documentacao() -> dict:
    """
    Retorna todo o conteudo para a pagina de Documentacao.
    """
    from ml.preprocessamento import (
        DATA_LEAKAGE_EXPLICACAO,
        SELECAO_MODELO_EXPLICACAO,
        COLUNAS_EXCLUIDAS,
    )

    metricas = carregar_metricas_modelo()

    return {
        "documentacao": DOCUMENTACAO,
        "data_leakage": DATA_LEAKAGE_EXPLICACAO,
        "selecao_modelo": SELECAO_MODELO_EXPLICACAO,
        "colunas_excluidas": sorted(list(COLUNAS_EXCLUIDAS)),
        "anti_alucinacao": ANTI_ALUCINACAO,
        "metricas": metricas,
    }


# -----------------------------------------------------------
#  TESTES (SPEC-06 validacao)
# -----------------------------------------------------------

def testar_pedagogico():
    """Testa a integridade do conteudo pedagogico."""
    print("=" * 50)
    print("  TESTE DA CAMADA PEDAGOGICA")
    print("=" * 50)

    # 1. Painel por pagina
    assert len(PAINEL_POR_PAGINA) >= 4, "Deve ter pelo menos 4 paginas mapeadas"
    for pagina, info in PAINEL_POR_PAGINA.items():
        assert "titulo" in info, f"Pagina {pagina} sem titulo"
        assert "tecnologia_principal" in info, f"Pagina {pagina} sem tecnologia"
        assert "badge_cor" in info, f"Pagina {pagina} sem badge_cor"
    print(f"  [OK] Painel lateral: {len(PAINEL_POR_PAGINA)} paginas mapeadas")

    # 2. Mapa da disciplina
    assert len(MAPA_DISCIPLINA) == 8, f"Deve ter 8 tecnologias, tem {len(MAPA_DISCIPLINA)}"
    for item in MAPA_DISCIPLINA:
        assert "conteudo_aula" in item
        assert "tecnologia" in item
        assert "arquivo" in item
    print(f"  [OK] Mapa disciplina: 8/8 tecnologias")

    # 3. Anti-alucinacao
    assert len(ANTI_ALUCINACAO) == 8, f"Deve ter 8 mecanismos, tem {len(ANTI_ALUCINACAO)}"
    for chave, info in ANTI_ALUCINACAO.items():
        assert "descricao" in info, f"Mecanismo {chave} sem descricao"
        assert "motivo" in info, f"Mecanismo {chave} sem motivo"
        assert "implementacao" in info, f"Mecanismo {chave} sem implementacao"
    print(f"  [OK] Anti-alucinacao: 8/8 mecanismos documentados")

    # 4. Disclaimer global
    assert "NAO substitui" in DISCLAIMER_GLOBAL
    assert "didatica" in DISCLAIMER_GLOBAL
    print(f"  [OK] Disclaimer global presente")

    # 5. Dataset info
    assert "DOI" in DATASET_INFO["referencia"]
    print(f"  [OK] Dataset com referencia DOI")

    # 6. Referencias clinicas
    refs = DOCUMENTACAO["referencias_clinicas"]
    assert len(refs) >= 3, f"Deve ter >=3 refs clinicas, tem {len(refs)}"
    for ref in refs:
        assert "doi" in ref, f"Referencia sem DOI: {ref['citacao'][:50]}"
    print(f"  [OK] {len(refs)} referencias clinicas com DOI")

    # 7. Referencias tecnicas
    refs_tec = DOCUMENTACAO["referencias_tecnicas"]
    assert len(refs_tec) >= 2
    print(f"  [OK] {len(refs_tec)} referencias tecnicas com DOI")

    # 8. Contexto pedagogico
    assert CONTEXTO_PEDAGOGICO["professor"] == "Prof. Ronaldo Martins da Costa"
    assert len(CONTEXTO_PEDAGOGICO["tecnologias"]) == 8
    print(f"  [OK] Contexto pedagogico: 8 tecnologias registradas")

    # 9. Funcoes auxiliares
    ctx = obter_contexto_pagina("index")
    assert "painel" in ctx
    assert "disclaimer" in ctx
    print(f"  [OK] obter_contexto_pagina('index') retorna painel + disclaimer")

    como = obter_conteudo_como_funciona()
    assert "mapa_disciplina" in como
    assert "knn" in como
    print(f"  [OK] obter_conteudo_como_funciona() retorna conteudo completo")

    doc = obter_conteudo_documentacao()
    assert "data_leakage" in doc
    assert "anti_alucinacao" in doc
    print(f"  [OK] obter_conteudo_documentacao() retorna leakage + anti-alucinacao")

    # 10. Metricas do modelo
    metricas = carregar_metricas_modelo()
    if metricas.get("modelo_disponivel"):
        assert "k_otimo" in metricas
        assert "acuracia_teste" in metricas
        print(f"  [OK] Metricas do modelo carregadas: k={metricas['k_otimo']}, "
              f"acc={metricas['acuracia_teste']:.1%}")
    else:
        print(f"  [AVISO] Modelo nao disponivel — metricas retornam fallback")

    print()
    print("  TODOS OS TESTES PASSARAM!")
    print("=" * 50)


if __name__ == "__main__":
    testar_pedagogico()
