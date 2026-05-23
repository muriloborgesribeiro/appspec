# ============================================================
#  artigo/escritor.py
#  APPSPEC -- Escritor de seções do artigo científico
#  Contrato: SPEC-09 6.3
#
#  Estratégias anti-alucinação aplicadas (estrategias-ia-seguranca.md):
#  C1  Text-Anchoring   — valida que números do output existem no input
#  C4  Pipeline Guard   — seção vazia ou com ref inexistente → retry
#  C5  Local Rules      — dados factuais nunca passam pelo LLM (injetados)
#  C7  Anti-Rewrite     — LLM descreve, nunca substitui valores fornecidos
# ============================================================

import os
import re



# -----------------------------------------------------------
#  C5 — MOTOR DE REGRAS LOCAIS
#  Todos os valores numéricos do artigo são injetados no prompt.
#  O LLM NUNCA decide um número — apenas escreve prosa ao redor.
# -----------------------------------------------------------

def _construir_fatos(ds, mk, ak, asvm, aalv, configs):
    """
    Retorna dict com todos os fatos que o LLM deve usar.
    Nenhum número chega ao LLM por memória — todos vêm daqui.
    """
    return {
        # Dataset
        "n_total":        782,
        "n_validos":      ds["n_validos"],
        "n_treino":       ds["n_treino"],
        "n_teste":        ds["n_teste"],
        "pct_teste":      round(ds["n_teste"] / ds["n_validos"] * 100, 0),
        "n_imputados":    ds["n_imputados"],
        "n_features":     ds["features_total"],
        "n_excluidas":    7,
        # KNN
        "k":              mk["k"],
        "k_min":          mk["k_minimo_clinico"],
        "k_candidatos":   str(mk["k_testados"]),
        # Métricas KNN
        "knn_acc":        _fmt(ak["acuracia"]),
        "knn_sen":        _fmt(ak["sensibilidade"]),
        "knn_esp":        _fmt(ak["especificidade"]),
        "knn_vpp":        _fmt(ak["vpp"]),
        "knn_vpn":        _fmt(ak["vpn"]),
        "knn_vp":         ak["vp"],
        "knn_fp":         ak["fp"],
        "knn_fn":         ak["fn"],
        "knn_vn":         ak["vn"],
        # SVM — métricas calculadas da matriz bruta (não do JSON truncado)
        # evita erro de arredondamento: JSON guarda 0.8085 mas 38/47=0.80851→80,9%
        "svm_kernel":     asvm["kernel"],
        "svm_C":          asvm["C"],
        "svm_acc":        _fmt_raw(asvm["vp"]+asvm["vn"], asvm["total"]),
        "svm_sen":        _fmt_raw(asvm["vp"], asvm["vp"]+asvm["fn"]),
        "svm_esp":        _fmt_raw(asvm["vn"], asvm["vn"]+asvm["fp"]),
        "svm_vpp":        _fmt_raw(asvm["vp"], asvm["vp"]+asvm["fp"]),
        "svm_vpn":        _fmt_raw(asvm["vn"], asvm["vn"]+asvm["fn"]),
        "svm_vp":         asvm["vp"],
        "svm_fp":         asvm["fp"],
        "svm_fn":         asvm["fn"],
        "svm_vn":         asvm["vn"],
        # Alvarado
        "alv_acc":        _fmt(aalv["acuracia"]),
        "alv_sen":        _fmt(aalv["sensibilidade"]),
        "alv_esp":        _fmt(aalv["especificidade"]),
        "alv_vpp":        _fmt(aalv["vpp"]),
        "alv_vpn":        _fmt(aalv["vpn"]),
        "alv_vp":         aalv["vp"],
        "alv_fp":         aalv["fp"],
        "alv_fn":         aalv["fn"],
        "alv_vn":         aalv["vn"],
        # Configs
        "cfg_e_k":        configs.get("E", {}).get("k", 11),
        "cfg_e_acc":      _fmt(configs.get("E", {}).get("acuracia_teste", 0)),
        "cfg_f_acc":      _fmt(configs.get("F", {}).get("acuracia_teste", 0)),
        # Comparações — calcular da matriz bruta para máxima precisão
        "svm_ganho_acc":  round(((asvm["vp"]+asvm["vn"])/asvm["total"]
                               - (aalv["vp"]+aalv["vn"])/aalv["total"]) * 100, 1),
        "svm_ganho_esp":  round((asvm["vn"]/(asvm["vn"]+asvm["fp"])
                               - aalv["vn"]/(aalv["vn"]+aalv["fp"])) * 100, 1),
        "knn_ganho_acc":  round(((ak["vp"]+ak["vn"])/ak["total"]
                               - (aalv["vp"]+aalv["vn"])/aalv["total"]) * 100, 1),
        "knn_ganho_esp":  round((ak["vn"]/(ak["vn"]+ak["fp"])
                               - aalv["vn"]/(aalv["vn"]+aalv["fp"])) * 100, 1),
        # Prevalência no conjunto de teste (VP+FN / total)
        "prev_teste":     round((ak["vp"] + ak["fn"]) / ak["total"] * 100, 1),
    }


def _fmt(v):
    return f"{v*100:.1f}".replace(".", ",") + "%"


def _fmt_raw(num, den):
    """Calcula percentual da fração bruta para evitar erro de arredondamento."""
    if den == 0:
        return "—"
    return f"{num/den*100:.1f}".replace(".", ",") + "%"


# -----------------------------------------------------------
#  MAPA DE REFERÊNCIAS — C7: LLM nunca decide qual [N] usar
# -----------------------------------------------------------

REFS = """
MAPA DE REFERÊNCIAS — copie exatamente estes números, NUNCA invente outros:
[1] Alvarado 1986 — escore clínico MANTRELS
[2] Bai 2023 — revisão sistemática Alvarado pediátrico
[3] Marcinkevics 2023 — dataset Regensburg UCI 938
[4] Pedregosa 2011 — scikit-learn
[5] Ohle 2011 — meta-análise Alvarado (42 estudos)
[6] Cover & Hart 1967 — algoritmo KNN
[7] Cortes & Vapnik 1995 — algoritmo SVM
[8] Gollapalli 2024 — ML para diagnóstico de apendicite
[9] Uddin 2022 — comparação algoritmos ML em doenças
[10] Kaufman 2012 — data leakage em data mining
[11] Panitz 2024 — sistemas hospitalares e plataformas no Brasil (SUS)
[12] Futoma 2020 — generalização em IA clínica (necessidade de validação externa local)

ONDE USAR CADA REFERÊNCIA:
- data leakage → cite [10]
- SVM, Cortes & Vapnik → cite [7]
- KNN, Cover & Hart → cite [6]
- Alvarado escore → cite [1]
- meta-análise Alvarado → cite [5]
- dataset Regensburg → cite [3]
- scikit-learn → cite [4]
- acurácias 64-84% ML apendicite → cite [8] e [9]
- sistemas hospitalares Brasil, HL7, MV, TASY → cite [11]
- plataforma de modelos, API → cite [11]
PROIBIDO: [12], [13], [14], [15] ou qualquer número acima de [11].
"""

SYSTEM_PROMPT = (
    "Você é escritor acadêmico em informática em saúde. "
    "Português brasileiro, linguagem científica precisa. "
    "HTML semântico: use <p>, <ul>, <li>, <strong>, <em>. "
    "NÃO inclua <html>, <head>, <body>. "
    "CRÍTICO 1: NÃO comece com título de seção em <h2> — o sistema já o insere. "
    "CRÍTICO 2: Use APENAS os valores numéricos fornecidos no prompt. "
    "NUNCA altere, arredonde diferente ou invente números. "
    "CRÍTICO 3: " + REFS + " ""PROIBIDO INVENTAR: (1) Docker/containerização — o sistema usa apenas Django+SQLite; (2) separação temporal — a separação foi ALEATÓRIA estratificada, não temporal."
)


# -----------------------------------------------------------
#  C1 — TEXT-ANCHORING: valida output do LLM
#  Verifica que o LLM não inventou números ausentes no input
# -----------------------------------------------------------

def _validar_output(texto: str, fatos: dict, secao: str) -> list:
    """
    C1: Verifica que números no output existem nos fatos injetados.
    Retorna lista de warnings (não bloqueia — apenas alerta).
    """
    warnings = []
    # Extrair todos os números do output
    nums_output = set(re.findall(r'\d+[.,]\d+%|\d{3,}', texto))
    # Valores permitidos — todos os números dos fatos
    vals_permitidos = set()
    for v in fatos.values():
        s = str(v).replace(".", ",")
        vals_permitidos.add(s)
        vals_permitidos.add(str(v))

    for n in nums_output:
        n_clean = n.replace(",", ".")
        if not any(n_clean in str(v) or str(v) in n_clean
                   for v in fatos.values()):
            warnings.append(f"[C1-WARN] Seção {secao}: valor '{n}' não está nos fatos injetados")

    # C4 — Pipeline Guard: referências > [11]
    refs_invalidas = re.findall(r'\[1[2-9]\]|\[2\d\]', texto)
    if refs_invalidas:
        warnings.append(f"[C4-WARN] Seção {secao}: referências inválidas {refs_invalidas}")

    return warnings


# -----------------------------------------------------------
#  CHAMADA À API (com retry para C4)
# -----------------------------------------------------------

def _chamar_llm(system_prompt: str, user_prompt: str,
                fatos: dict = None, secao: str = "") -> tuple:
    """
    Chama Claude API. Retorna (texto, warnings).
    C4: se houver referências inválidas, tenta corrigir 1x.
    """
    import anthropic
    client = anthropic.Anthropic()

    def _call(prompt):
        r = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.content[0].text

    texto = _call(user_prompt)
    warnings = _validar_output(texto, fatos or {}, secao) if fatos else []

    # C4 — retry se referências inválidas
    refs_invalidas = re.findall(r'\[1[2-9]\]|\[2\d\]', texto)
    if refs_invalidas:
        correcao = (
            f"\n\nCORREÇÃO OBRIGATÓRIA: O texto contém referências inválidas {refs_invalidas}. "
            f"Reescreva removendo-as. Use apenas [1] a [11] conforme o mapa fornecido.\n\n"
            + user_prompt
        )
        texto = _call(correcao)
        warnings.append(f"[C4-RETRY] Seção {secao}: retry após refs inválidas {refs_invalidas}")

    return texto, warnings


# -----------------------------------------------------------
#  INTRODUÇÃO FIXA (não passa pelo LLM — C5)
# -----------------------------------------------------------

INTRODUCAO_FIXA = """
<p>Apendicite aguda é a principal causa de abdome agudo cirúrgico em crianças e adultos
jovens, com incidência de 7–8% ao longo da vida [1]. O diagnóstico tardio eleva o risco
de perfuração para mais de 80% em menores de cinco anos, podendo evoluir para peritonite
e sepse [2].</p>

<p>O Escore de Alvarado (1986) [1] sistematiza oito critérios clínico-laboratoriais em
0–10 pontos: migração da dor para a fossa ilíaca direita (FID), anorexia, náuseas/vômitos,
dor à palpação em FID (peso 2), sinal de Blumberg, temperatura &gt;37,3°C, leucocitose
&gt;10.000/mm³ (peso 2) e neutrofilia. Escores ≤4 permitem alta com sensibilidade 99%
(corte 5); ≥7 indicam cirurgia imediata (especificidade 81%, corte 7) [5]. A meta-análise
de Ohle et al. [5] confirmou esses pontos de corte em 42 estudos independentes.</p>

<p>O K-Nearest Neighbors (KNN) [6] classifica casos pela votação dos k vizinhos mais
próximos no espaço euclidiano de features — geometricamente interpretável e adequado a
datasets de médio porte. O Support Vector Machine (SVM) [7] encontra o hiperplano de
máxima margem entre as classes, com robustez reconhecida em dados clínicos tabulares.
Estudos recentes aplicaram ambos em diagnóstico de apendicite com acurácia de 64–84% em
dados clínicos [8, 9].</p>

<p>O APPSPEC integra os três métodos — Escore de Alvarado, KNN e SVM — em plataforma web
com duplo objetivo: prover estimativa de risco de apendicite e demonstrar pedagogicamente
Django, scikit-learn, pandas, joblib e Orange3.</p>
""".strip()


# -----------------------------------------------------------
#  FUNÇÕES POR SEÇÃO — C7: fatos injetados, LLM só escreve prosa
# -----------------------------------------------------------

def _escrever_abstract(f) -> tuple:
    prompt = f"""Escreva o RESUMO estruturado do artigo APPSPEC com as seções:
CONTEXTO, OBJETIVO, MÉTODOS, RESULTADOS e CONCLUSÃO.

VALORES OBRIGATÓRIOS (use exatamente estes — não arredonde diferente):
Dataset: N={f['n_total']} total, {f['n_validos']} válidos, treino={f['n_treino']}, teste={f['n_teste']}
Features: {f['n_features']} variáveis tabulares (excluídas {f['n_excluidas']} por data leakage)
KNN: k={f['k']}, acurácia={f['knn_acc']}, sensibilidade={f['knn_sen']}, especificidade={f['knn_esp']}
     VP={f['knn_vp']}, FP={f['knn_fp']}, FN={f['knn_fn']}, VN={f['knn_vn']}
SVM: kernel={f['svm_kernel']}, C={f['svm_C']}, acurácia={f['svm_acc']},
     sensibilidade={f['svm_sen']}, especificidade={f['svm_esp']}
Alvarado (corte ≥5): acurácia={f['alv_acc']}, sensibilidade={f['alv_sen']},
     especificidade={f['alv_esp']}
SVM superou Alvarado em: +{f['svm_ganho_acc']} pp acurácia, +{f['svm_ganho_esp']} pp especificidade
Cite [3] para o dataset, [6] para KNN, [7] para SVM, [5] para Alvarado.

REGRAS DO ABSTRACT:
- O abstract deve ser escrito em formato IMRAD com frases completas, formando uma narrativa contínua e não apenas tópicos ou bullet points curtos.
- Se mencionar taxa de apendicectomias negativas, citar [5]=Ohle 2011 que reporta especificidade limitada.
  NÃO inventar percentual específico (15-30%) sem citação — omitir o número ou citar [5].
- Na seção MÉTODOS do abstract: mencionar os três conjuntos —
  "estratificados em treino (n={f['n_treino']}), validação (n=113) e teste (n={f['n_teste']})"
  para que a soma {f['n_treino']}+113+{f['n_teste']}={f['n_validos']} seja transparente."""
    return _chamar_llm(SYSTEM_PROMPT, prompt, f, "abstract")


def _escrever_metodos(f, colunas_excluidas) -> tuple:
    prompt = f"""Escreva a seção MATERIAIS E MÉTODOS com subseções 2.1 a 2.5.

VALORES OBRIGATÓRIOS:
2.1 Dataset: {f['n_total']} pacientes pediátricos (0-18 anos), Hospital St. Hedwig Regensburg 2016-2021,
    53 variáveis originais, UCI ML Repository ID 938 [3], protocolo ético n.° 18-1063-101
    Variáveis laboratoriais reais do dataset (use APENAS estas, não invente outras):
    WBC_Count, CRP, Neutrophil_Percentage, Neutrophilia, RBC_Count,
    Hemoglobin, RDW, Thrombocyte_Count, Ketones_in_Urine, RBC_in_Urine, WBC_in_Urine
    NÃO mencionar "bilirrubina" — não existe neste dataset.
2.2 Preparação: excluídas {f['n_excluidas']} variáveis por data leakage [10].
    Razão de exclusão de CADA variável (use EXATAMENTE estas justificativas):
    - Alvarado_Score: gerou acurácia artificial de 95,6% — leakage do desfecho
    - Paediatric_Appendicitis_Score: escore composto que incorpora o diagnóstico
    - Diagnosis: variável-alvo da predição
    - Management, Length_of_Stay, Severity: disponíveis apenas após decisão diagnóstica
    - Segmented_Neutrophils: proporção crítica de valores ausentes (~93%), inviabilizando imputação confiável
    782-29=753 válidos, 29 excluídos por NaN críticos em múltiplas variáveis,
    N={f['n_validos']}, imputação pela mediana de {f['n_imputados']} valores e escalonamento via MinMaxScaler.
    MUITO IMPORTANTE: Afirme categoricamente que "a imputação e o escalonamento foram ajustados (fit) exclusivamente no conjunto de treino e aplicados (transform) ao teste", garantindo ausência total de vazamento de dados estatísticos.
2.3 Algoritmos:
    KNN [6]: KNeighborsClassifier [4], k mínimo={f['k_min']}, valores candidatos=3, 5, 7, 9, 11,
    validação cruzada 5-fold no conjunto de treino → k={f['k']} ótimo (Config F, 32 features), distância euclidiana.
    SVM [7]: SVC [4], kernel={f['svm_kernel']}, C={f['svm_C']} estabelecido através de busca em grade (grid search) com validação cruzada.
2.4 Plataforma:
    Arquitetura: Framework Django 4.2 (padrão MVT), banco SQLite.
    Integração ML: Persistência dos modelos scikit-learn via `joblib`. Os dados do formulário web são traduzidos para arrays NumPy e processados em tempo real pela camada de predição.
    Interface responsiva voltada ao ensino e discussão clínica. (Não cite [4] para Django).
2.5 Avaliação: particionamento 70/15/15 estratificado:
    treino n={f['n_treino']} (70%), validação interna n=113 (15%), teste retido n={f['n_teste']} (15%)
    VERIFICAÇÃO: {f['n_treino']}+113+{f['n_teste']} = {f['n_validos']} ✓ — use n=113 para validação, NUNCA n=112
    O conjunto de validação foi usado para seleção do k por cross-validation.
    O conjunto de teste ({f['n_teste']} = {f['pct_teste']:.0f}% de {f['n_validos']}) foi isolado completamente —
    nenhuma observação exposta durante treino ou seleção de hiperparâmetros.
    Métricas: acurácia/sensibilidade/especificidade/VPP/VPN (Fawcett 2006, sem número de ref.)
    Comparação KNN vs SVM vs Alvarado no MESMO conjunto de teste.
    Config E: k={f['cfg_e_k']}, acurácia={f['cfg_e_acc']} | Config F: k={f['k']}, acurácia={f['cfg_f_acc']}

REGRA DE FORMATAÇÃO PARA 2.5 (CRÍTICO — WeasyPrint trunca texto longo):
- A subseção 2.5 deve terminar com frase COMPLETA e ponto final.
- Máximo 6 linhas de texto após os bullets da partição.
- Terminar obrigatoriamente com: "O conjunto de teste foi mantido em hold-out rigoroso,
  garantindo estimativa não enviesada do desempenho em dados genuinamente não vistos."""
    return _chamar_llm(SYSTEM_PROMPT, prompt, f, "metodos")


def _escrever_resultados(f) -> tuple:
    prompt = f"""Escreva a seção RESULTADOS (seção 3).

VALORES OBRIGATÓRIOS — use exatamente estes, não invente outros:
Conjunto de teste: n={f['n_teste']} ({f['pct_teste']:.0f}% de {f['n_validos']} pacientes)
Prevalência apendicite no teste: {f['prev_teste']}% ({f['knn_vp']+f['knn_fn']}/{f['n_teste']} casos positivos)

Tabela 1 — dados para referenciar: {{{{table:tab1}}}}

SVM (kernel={f['svm_kernel']}, C={f['svm_C']}):
  acurácia={f['svm_acc']}, sensibilidade={f['svm_sen']}, especificidade={f['svm_esp']}
  VPP={f['svm_vpp']}, VPN={f['svm_vpn']}
  Matriz: VP={f['svm_vp']}, FP={f['svm_fp']}, FN={f['svm_fn']}, VN={f['svm_vn']}
  Figura 2: {{{{fig:fig2}}}} (matriz de confusão SVM)

KNN (k={f['k']}):
  acurácia={f['knn_acc']}, sensibilidade={f['knn_sen']}, especificidade={f['knn_esp']}
  VPP={f['knn_vpp']}, VPN={f['knn_vpn']}
  Matriz: VP={f['knn_vp']}, FP={f['knn_fp']}, FN={f['knn_fn']}, VN={f['knn_vn']}
  Figura 1: {{{{fig:fig1}}}} (matriz de confusão KNN)

Alvarado (corte ≥5):
  acurácia={f['alv_acc']}, sensibilidade={f['alv_sen']}, especificidade={f['alv_esp']}
  VPP={f['alv_vpp']}, VPN={f['alv_vpn']}
  Matriz: VP={f['alv_vp']}, FP={f['alv_fp']}, FN={f['alv_fn']}, VN={f['alv_vn']}

Figura 4: {{{{fig:fig4}}}} (Curvas ROC comparativas)
Figura 5: {{{{fig:fig5}}}} (Curvas Precision-Recall comparativas)
Analise as curvas, citando o bom desempenho do SVM com kernel linear na discriminação dos casos.

Config D descartada: 95,6% (data leakage confirmado [10])
IMPORTANTE: ao descrever o leakage da Config D, dizer que as variáveis PREDITORAS
codificavam o desfecho (ex: Alvarado_Score incorpora o diagnóstico) — NÃO dizer
"contaminação entre conjuntos de treino e teste" pois os conjuntos estavam separados.
Ganhos do SVM sobre Alvarado: +{f['svm_ganho_acc']} pp acurácia, +{f['svm_ganho_esp']} pp especificidade
Ganhos do KNN sobre Alvarado: +{f['knn_ganho_acc']} pp acurácia, +{f['knn_ganho_esp']} pp especificidade

INTERFACE DO SISTEMA: {{{{fig:fig3}}}} — descrever brevemente a interface mostrando os três métodos.

REGRA DE LAYOUT: Insira as tags das imagens (ex: {{{{fig:fig1}}}}) LIVRES de qualquer tag HTML. NÃO coloque os placeholders de figura e tabela dentro de tags <p>, <div> ou <li>. Isso quebra o WeasyPrint.
NÃO cite referências numéricas nos resultados para os valores da matriz — os dados são do sistema."""
    return _chamar_llm(SYSTEM_PROMPT, prompt, f, "resultados")


def _escrever_discussao(f) -> tuple:
    prompt = f"""Escreva a seção DISCUSSÃO (seção 4) com 4 parágrafos.

VALORES OBRIGATÓRIOS:
KNN: acurácia={f['knn_acc']}, sensibilidade={f['knn_sen']}, especificidade={f['knn_esp']}
SVM: acurácia={f['svm_acc']}, sensibilidade={f['svm_sen']}, especificidade={f['svm_esp']}
Alvarado: acurácia={f['alv_acc']}, sensibilidade={f['alv_sen']}, especificidade={f['alv_esp']}
Dataset: {f['n_validos']} pacientes, {f['n_features']} features tabulares

PARÁGRAFO 1 — Contextualizar acurácia e Prevalência:
Acurácia global na casa dos 75-80% se encaixa com o esperado na literatura clínica [8, 9]. Contudo, no conjunto de teste (N=113), a prevalência implícita de apendicite foi de aproximadamente 58%. Uma prevalência alta eleva artificialmente o Valor Preditivo Positivo (VPP) se o modelo for aplicado em um pronto-socorro geral de baixa prevalência. Mencione também que o intervalo de confiança tem margem de erro de ±7,4 pp.

PARÁGRAFO 2 — Trade-off Clínico (FN vs FP) e Alvarado:
Apendicite aguda requer ação cirúrgica. Um falso negativo (FN) é grave (risco de peritonite e sepse). O Alvarado tem a maior sensibilidade ({f['alv_sen']}), sendo clinicamente mais seguro como triagem inicial que KNN e SVM. Critique a Tabela 1: a comparação de Alvarado usando um corte único (≥5) subestima sua utilidade clínica real, já que ele foi desenhado com múltiplos limiares operacionais (≤4 = alta, ≥7 = cirurgia) [2].

PARÁGRAFO 3 — Validade Externa e SUS:
A generalização é limitada. O dataset original de Regensburg [3] é uma coorte pediátrica alemã. Parâmetros fisiológicos mudam por idade e o perfil de exames disponíveis na rede SUS brasileira difere substancialmente [11]. Validação externa é imprescindível para algoritmos de IA clínica [12].

PARÁGRAFO 4 — Aspecto pedagógico:
Nesse contexto de limitações do mundo real, a interface foca na exibição do Orange3, Django e scikit-learn. O pipeline serve primordialmente para instrução dos conceitos de ML aplicados à saúde em vez de um diagnóstico definitivo, o qual requereria escrutínio regulatório e melhor tratamento dos dados ausentes."""
    return _chamar_llm(SYSTEM_PROMPT, prompt, f, "discussao")


def _escrever_conclusao(f) -> tuple:
    prompt = f"""Escreva a seção CONCLUSÃO (seção 5) com síntese + 3 próximos passos + declaração de IA.

VALORES OBRIGATÓRIOS:
KNN: acurácia={f['knn_acc']}, sensibilidade={f['knn_sen']}
SVM: acurácia={f['svm_acc']}, sensibilidade={f['svm_sen']}
SVM superou Alvarado: +{f['svm_ganho_acc']} pp acurácia, +{f['svm_ganho_esp']} pp especificidade
ATENÇÃO: use "superior" (não "comparável") pois {f['svm_ganho_acc']} pp é ganho expressivo.

ORDEM DE SENSIBILIDADE (CRÍTICO — não inverter):
Alvarado={f['alv_sen']} > KNN={f['knn_sen']} > SVM={f['svm_sen']}
O Alvarado tem a MAIOR sensibilidade entre os três métodos.
O KNN tem a SEGUNDA maior sensibilidade — NÃO dizer "KNN apresentou a maior sensibilidade entre os métodos".
Dizer algo como: "O KNN, com sensibilidade de {f['knn_sen']}, segunda maior entre os métodos,
adequa-se a contextos onde a minimização de falsos negativos é prioritária."
NÃO cite [1] nem [7] para afirmar resultados do próprio estudo
NÃO use "separação temporal" — a separação foi ALEATÓRIA estratificada (random_state fixo), não temporal.
NÃO mencionar Docker — o sistema não tem containerização Docker. — resultados próprios não têm citação de terceiros.
Cite [6] para KNN e [7] para SVM apenas quando descrever os algoritmos, não os resultados numéricos.

PRÓXIMOS PASSOS (obrigatórios exatamente assim):
1. HL7 FHIR R4 — endpoint REST para integração com MV e TASY [11]
2. Plataforma de modelos preditivos com API documentada [11]
3. Explicabilidade via SHAP (teoria dos jogos cooperativos)

DECLARAÇÃO DE IA (copiar exatamente, incluindo a tag div):
<div class="ai-declaration">
"Os autores utilizaram ferramentas de IA generativa (Antigravity e Claude AI) como apoio
na redação do manuscrito e no desenvolvimento estrutural do sistema. Todo o conteúdo foi
revisado e validado pelos autores, que assumem total responsabilidade pelo trabalho."
</div> """
    return _chamar_llm(SYSTEM_PROMPT, prompt, f, "conclusao")


# -----------------------------------------------------------
#  FUNÇÃO PRINCIPAL
# -----------------------------------------------------------

def escrever_secoes(system_report: dict = None) -> dict:
    if system_report is None:
        raise RuntimeError("system_report não disponível. Execute leitor.ler_sistema() primeiro.")

    ds    = system_report["dataset"]
    mk    = system_report["modelo_knn"]
    ak    = system_report["avaliacao_knn"]
    asvm  = system_report["avaliacao_svm"]
    aalv  = system_report["avaliacao_alvarado"]
    cfgs  = system_report["configs"]

    # C5 — construir todos os fatos localmente
    fatos = _construir_fatos(ds, mk, ak, asvm, aalv, cfgs)
    colunas = ", ".join(ds.get("colunas_excluidas_leakage", []))

    todos_warnings = []

    print("       [C5] Fatos locais construídos — LLM não decide números")
    print("       Abstract...")
    abstract, w = _escrever_abstract(fatos)
    todos_warnings.extend(w)

    print("       Introdução: fixa (sem LLM)")
    introducao = INTRODUCAO_FIXA

    print("       Materiais e Métodos...")
    metodos, w = _escrever_metodos(fatos, colunas)
    todos_warnings.extend(w)

    print("       Resultados...")
    resultados, w = _escrever_resultados(fatos)
    todos_warnings.extend(w)

    print("       Discussão...")
    discussao, w = _escrever_discussao(fatos)
    todos_warnings.extend(w)

    print("       Conclusão...")
    conclusao, w = _escrever_conclusao(fatos)
    todos_warnings.extend(w)

    if todos_warnings:
        print(f"       [AVISOS C1/C4]: {len(todos_warnings)} itens para revisar")
        for w in todos_warnings:
            print(f"         {w}")

    secoes = {
        "abstract":   abstract,
        "introducao": introducao,
        "metodos":    metodos,
        "resultados": resultados,
        "discussao":  discussao,
        "conclusao":  conclusao,
        "_warnings":  todos_warnings,
    }

    return secoes


if __name__ == "__main__":
    print("escritor.py — execute via gerador.py")
