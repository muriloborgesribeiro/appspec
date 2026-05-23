# ============================================================
#  artigo/montador.py
#  APPSPEC -- Montador do article_data para o exportador
#  Modulo: artigo (ferramenta de desenvolvimento)
#  Contrato: SPEC-09 6.4 / P-03
#
#  Recebe system_report (do leitor) e secoes (do escritor)
#  e monta o dict article_data no formato esperado pelo
#  template WeasyPrint (scientific-article-layout).
# ============================================================

import os
import datetime



# -----------------------------------------------------------
#  Constantes de texto (sem numeros — apenas strings)
# -----------------------------------------------------------

def _fmt(v):
    """Formata percentual com vírgula decimal (PT-BR)."""
    return f"{v*100:.1f}".replace(".", ",") + "%"


def _fmt_raw(num, den):
    """Calcula percentual da fração bruta — evita truncamento do JSON."""
    if den == 0: return "—"
    return f"{num/den*100:.1f}".replace(".", ",") + "%"


AUTORES_PADRAO = (
    "Francisco Neri · Anahi Philbois · Murilo Borges Ribeiro<br/>"
    "Instituto de Informática · Universidade Federal de Goiás (UFG)"
)

TITULO = (
    "APPSPEC: Sistema de Apoio ao Diagnóstico de Apendicite Combinando "
    "Escore de Alvarado, K-Nearest Neighbors e Support Vector Machine — "
    "Abordagem Pedagógica para Sistemas Clínicos Inteligentes"
)

CONTEXTO = (
    "Trabalho de Conclusão · Disciplina de Frameworks · "
    "Prof. Ronaldo Martins da Costa"
)

PALAVRAS_CHAVE = (
    "Sistemas Clínicos Inteligentes · K-Nearest Neighbors · "
    "Support Vector Machine · Escore de Alvarado · Django · "
    "Apoio ao Diagnóstico · Apendicite"
)

REFERENCIAS = [
    "[1] Alvarado A. A practical score for the early diagnosis of acute appendicitis. "
    "Ann Emerg Med. 1986;15:557–64. DOI:10.1016/S0196-0644(86)80468-2",

    "[2] Bai S et al. Alvarado Score for Appendicitis in Children: Systematic Review "
    "and Meta-Analysis. J Pediatr Surg. 2023.",

    "[3] Marcinkevics R et al. Regensburg Pediatric Appendicitis [Dataset]. "
    "UCI ML Repository; 2023. DOI:10.5281/zenodo.7669442",

    "[4] Pedregosa F et al. Scikit-learn: Machine Learning in Python. "
    "JMLR. 2011;12:2825–30.",

    "[5] Ohle R et al. The Alvarado score for predicting acute appendicitis: "
    "a systematic review. BMC Med. 2011;9:139. DOI:10.1186/1741-7015-9-139",

    "[6] Cover T, Hart P. Nearest neighbor pattern classification. "
    "IEEE Trans Inf Theory. 1967;13:21–7. DOI:10.1109/TIT.1967.1053964",

    "[7] Cortes C, Vapnik V. Support-vector networks. Machine Learning. "
    "1995;20(3):273–297. DOI:10.1007/BF00994018",

    "[8] Gollapalli M et al. Appendicitis Diagnosis: Ensemble ML and XAI. "
    "Big Data Cogn Comput. 2024.",

    "[9] Uddin S et al. Comparative performance of KNN variants for disease "
    "prediction. Sci Rep. 2022.",

    "[10] Kaufman S et al. Leakage in Data Mining. KDD. 2012. DOI:10.1145/2020408.2020496",

    "[11] Panitz LM, Prata DN, Rodrigues W. Análise do desempenho dos hospitais "
    "públicos e privados que atendem ao SUS. Cad Saúde Pública. 2024;40(9):"
    "e00156023. DOI:10.1590/0102-311XPT156023",

    "[12] Futoma J, Simons M, Panch T, et al. The myth of generalisability in clinical AI: "
    "a route to robust medicine. Lancet Digit Health. 2020;2(9):e489-e492. "
    "DOI:10.1016/S2589-7500(20)30186-4",
]


# -----------------------------------------------------------
#  Funcao principal
# -----------------------------------------------------------

def montar_article_data(system_report: dict = None,
                        secoes: dict = None,
                        autores: str = None,
                        ano: int = None) -> dict:
    """
    Monta o dict article_data no formato do scientific-article-layout.

    Interface publica conforme SPEC-09 6.4 / P-03:
      INPUT:  system_report — dict do leitor.py (ou VSM)
              secoes        — dict do escritor.py (ou VSM)
              autores       — str com autores (ou AUTORES_PADRAO)
              ano           — int com ano (ou ano atual)
      OUTPUT: article_data — dict completo para o exportador/WeasyPrint
    """

    if system_report is None:
        raise RuntimeError(
            "system_report nao fornecido e nao encontrado no VSM. "
            "Execute leitor.ler_sistema() primeiro."
        )
    if secoes is None:
        raise RuntimeError(
            "secoes nao fornecido e nao encontrado no VSM. "
            "Execute escritor.escrever_secoes() primeiro."
        )

    if autores is None:
        autores = AUTORES_PADRAO
    if ano is None:
        ano = datetime.datetime.now().year

    # Extrair blocos do system_report
    ak = system_report["avaliacao_knn"]
    asvm = system_report["avaliacao_svm"]
    aalv = system_report["avaliacao_alvarado"]
    mk = system_report["modelo_knn"]
    configs = system_report["configs"]
    figuras = system_report["figuras"]

    # --- Montar Tabela 1 ---
    tabela_html = _montar_tabela(ak, asvm, aalv, mk, configs)

    # --- Montar figuras ---
    figures = {}
    if figuras.get("fig1"):
        figures["fig1"] = {
            "path": figuras["fig1"],
            "caption": (
                f"Figura 1. Matriz de Confusão do KNN no conjunto de teste "
                f"(N={ak['total']}). Diagonal (acertos): {ak['vn']} pacientes "
                f"sem apendicite + {ak['vp']} com apendicite = "
                f"{ak['vn'] + ak['vp']} corretos ({_fmt(ak['acuracia'])}). "
                f"Erros: {ak['fp']} falsos positivos e {ak['fn']} falsos "
                f"negativos."
            ),
            "width": "60%",
            "span": False,
        }
    if figuras.get("fig2"):
        figures["fig2"] = {
            "path": figuras["fig2"],
            "caption": (
                f"Figura 2. Matriz de Confusão do SVM "
                f"(kernel={asvm.get('kernel','linear')}, C={asvm.get('C',1.0)}, "
                f"N={asvm['total']}). "
                f"VP={asvm['vp']}, FP={asvm['fp']}, FN={asvm['fn']}, VN={asvm['vn']}. "
                f"Acurácia {_fmt_raw(asvm['vp']+asvm['vn'], asvm['total'])}, sensibilidade {_fmt_raw(asvm['vp'], asvm['vp']+asvm['fn'])}, "
                f"especificidade {_fmt_raw(asvm['vn'], asvm['vn']+asvm['fp'])}."
            ),
            "width": "60%",
            "span": False,
        }
    if figuras.get("fig3"):
        figures["fig3"] = {
            "path": figuras["fig3"],
            "span": True,
            "width": "98%",
            "caption": (
                f"Figura 3. Interface do APPSPEC exibindo resultado simultâneo para um paciente "
                f"com todos os critérios de Alvarado positivos (escore 10/10). Da esquerda para "
                f"direita: Escore de Alvarado (regra clínica determinística), KNN (probabilidade calculada, "
                f"k={mk['k']} vizinhos) e SVM (probabilidade alta, kernel linear). "
                f"Nota: Os percentuais em destaque nos painéis referem-se à probabilidade de apendicite para este caso específico, "
                f"não devendo ser confundidos com a acurácia global do modelo reportada na Tabela 1."
            ),
        }
    if figuras.get("fig4"):
        figures["fig4"] = {
            "path": figuras["fig4"],
            "caption": (
                "Figura 4. Curvas ROC (Receiver Operating Characteristic) comparativas "
                "entre KNN, SVM e Regra Clínica de Alvarado."
            ),
            "width": "85%",
            "span": False,
        }
    if figuras.get("fig5"):
        figures["fig5"] = {
            "path": figuras["fig5"],
            "caption": (
                "Figura 5. Curvas Precision-Recall comparativas "
                "entre KNN, SVM e Regra Clínica de Alvarado."
            ),
            "width": "85%",
            "span": False,
        }

    # --- Montar article_data ---
    article_data = {
        # Cabecalho
        "title": TITULO,
        "authors": autores,
        "context": f"{CONTEXTO} · {ano}",

        # Resumo
        "abstract": secoes["abstract"],
        "keywords": PALAVRAS_CHAVE,

        # Secoes
        "sections": [
            {
                "title": "1. INTRODUÇÃO",
                "content": secoes["introducao"],
            },
            {
                "title": "2. MATERIAIS E MÉTODOS",
                "content": secoes["metodos"],
            },
            {
                "title": "3. RESULTADOS",
                "content": secoes["resultados"],
            },
            {
                "title": "4. DISCUSSÃO",
                "content": secoes["discussao"],
            },
            {
                "title": "5. CONCLUSÃO",
                "content": secoes["conclusao"],
            },
        ],

        # Figuras e tabelas
        "figures": figures,
        "tables": {
            "tab1": {
                "caption": (
                    f"Tabela 1. Comparação de desempenho no conjunto de teste "
                    f"(N={ak['total']}, prevalência de apendicite ~{int(ak['vp']+ak['fn'])}/{ak['total']}). "
                    f"†Data leakage confirmado. "
                    f"Nota: A Config E foi testada preliminarmente (acurácia 69,5%, k=11), "
                    f"sendo inferior à Config F."
                ),
                "html": tabela_html,
                "span": True,
            },
        },

        # Referencias
        "references": REFERENCIAS,

        # Rodape
        "footer_left": f"Disciplina · Frameworks · UFG · {ano}",
        "footer_right": "APPSPEC · Apoio ao Diagnóstico",
    }


    return article_data


# -----------------------------------------------------------
#  Funcao auxiliar — Tabela 1
# -----------------------------------------------------------

def _montar_tabela(ak, asvm, aalv, mk, configs) -> str:
    """
    Monta a Tabela 1 em HTML conforme P-03:
    1. Alvarado Score (corte ≥5)
    2. KNN Config E
    3. KNN Config F*
    4. SVM
    5. Config D† (data leakage)
    """
    cfg_e = configs.get("E", {})
    cfg_f = configs.get("F", {})

    # Config E: pegar metricas de comparacao_configs (nao tem VP/FP/FN/VN detalhado)
    # Usar apenas acuracia, que e o que o JSON tem para E
    cfg_e_acc = cfg_e.get("acuracia_teste", 0)
    cfg_e_k = cfg_e.get("k", "?")

    linhas = [
        # Alvarado
        _linha_tabela(
            f"Alvarado Score (corte ≥5)",
            aalv['acuracia'], aalv['sensibilidade'], aalv['especificidade'],
            aalv.get('vpp', 0), aalv.get('vpn', 0),
        ),
        # Config F (avaliacao_knn completa)
        _linha_tabela(
            f"KNN Config F (Tabular, k={mk['k']})",
            ak['acuracia'], ak['sensibilidade'], ak['especificidade'],
            ak['vpp'], ak['vpn'],
        ),
        # SVM
        _linha_tabela_raw(
            f"SVM ({asvm.get('kernel','linear')}, C={asvm.get('C',1.0)})",
            asvm['vp']+asvm['vn'], asvm['total'],           # acc: frações brutas
            asvm['vp'], asvm['vp']+asvm['fn'],              # sen
            asvm['vn'], asvm['vn']+asvm['fp'],              # esp: 38/47 → 80,9%
            asvm['vp'], asvm['vp']+asvm['fp'],              # vpp
            asvm['vn'], asvm['vn']+asvm['fn'],              # vpn
        ),
        # Config D (data leakage — valor textual fixo)
        '<tr class="leakage-row">'
        '<td>Config D (descartada)†</td>'
        '<td>95,6%</td>'
        '<td>—</td><td>—</td><td>—</td><td>—</td>'
        '</tr>',
    ]

    return (
        '<table >'
        '<thead><tr>'
        '<th>Modelo / Config</th>'
        '<th>Acurácia</th>'
        '<th>Sensib.</th>'
        '<th>Especif.</th>'
        '<th>VPP</th>'
        '<th>VPN</th>'
        '</tr></thead>'
        '<tbody>'
        + "\n".join(linhas) +
        '</tbody></table>'
    )


def _linha_tabela(nome, acc, sens, espec, vpp, vpn) -> str:
    """Linha completa da tabela com todas as metricas."""
    return (
        f'<tr>'
        f'<td>{nome}</td>'
        f'<td>{_fmt(acc)}</td>'
        f'<td>{_fmt(sens)}</td>'
        f'<td>{_fmt(espec)}</td>'
        f'<td>{_fmt(vpp)}</td>'
        f'<td>{_fmt(vpn)}</td>'
        f'</tr>'
    )


def _linha_tabela_raw(nome, acc_n, acc_d, sen_n, sen_d, esp_n, esp_d,
                      vpp_n, vpp_d, vpn_n, vpn_d) -> str:
    """Linha da tabela calculada de frações brutas — evita truncamento JSON."""
    return (
        f'<tr>'
        f'<td>{nome}</td>'
        f'<td>{_fmt_raw(acc_n, acc_d)}</td>'
        f'<td>{_fmt_raw(sen_n, sen_d)}</td>'
        f'<td>{_fmt_raw(esp_n, esp_d)}</td>'
        f'<td>{_fmt_raw(vpp_n, vpp_d)}</td>'
        f'<td>{_fmt_raw(vpn_n, vpn_d)}</td>'
        f'</tr>'
    )


def _linha_tabela_simples(nome, acc) -> str:
    """Linha da tabela com apenas acuracia (configs sem avaliacao completa)."""
    return (
        f'<tr>'
        f'<td>{nome}</td>'
        f'<td>{_fmt(acc)}</td>'
        f'<td>—</td><td>—</td><td>—</td><td>—</td>'
        f'</tr>'
    )


# -----------------------------------------------------------
#  FUNCAO DE TESTE
# -----------------------------------------------------------

def testar_montador():
    """
    Testa o montador com dados reais do leitor e secoes simuladas.
    """
    print("=" * 50)
    print("  TESTE DO MONTADOR (artigo/montador.py)")
    print("=" * 50)

    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.dirname(script_dir)
    sys.path.insert(0, project_path)

    from artigo.leitor import ler_sistema
    report = ler_sistema(project_path)
    print(f"  [OK] system_report carregado")

    # Secoes simuladas (para testar sem API)
    secoes_teste = {
        "abstract": "<p>Resumo do artigo APPSPEC...</p>",
        "introducao": "<p>Introdução fixa do v8...</p>",
        "metodos": "<p>Materiais e métodos...</p>",
        "resultados": "<p>Resultados com {{fig:fig1}} e {{table:tab1}}...</p>",
        "discussao": "<p>Discussão dos resultados...</p>",
        "conclusao": "<p>Conclusão e próximos passos...</p>",
    }

    # Montar
    article_data = montar_article_data(report, secoes_teste)
    print(f"  [OK] article_data montado")

    # Verificacoes
    assert article_data["title"], "Titulo ausente"
    print(f"  [OK] title: {article_data['title'][:60]}...")

    assert article_data["authors"], "Autores ausentes"
    print(f"  [OK] authors: presente")

    assert len(article_data["sections"]) == 5, \
        f"Esperado 5 secoes, obteve {len(article_data['sections'])}"
    for sec in article_data["sections"]:
        assert sec["title"], "Secao sem titulo"
        assert sec["content"], "Secao sem conteudo"
    print(f"  [OK] sections: {len(article_data['sections'])} secoes")

    assert "tab1" in article_data["tables"], "Tabela tab1 ausente"
    tab_html = article_data["tables"]["tab1"]["html"]
    assert "Alvarado" in tab_html, "Alvarado ausente na tabela"
    assert "Config D" in tab_html, "Config D ausente na tabela"
    assert "SVM" in tab_html, "SVM ausente na tabela"
    print(f"  [OK] tab1: tabela comparativa montada ({len(tab_html)} chars)")

    n_figuras = len(article_data["figures"])
    print(f"  [OK] figures: {n_figuras} figura(s)")

    assert len(article_data["references"]) >= 9, \
        f"Esperado >=9 refs, obteve {len(article_data['references'])}"
    print(f"  [OK] references: {len(article_data['references'])} itens")

    assert article_data["footer_left"], "Footer left ausente"
    assert article_data["footer_right"], "Footer right ausente"
    print(f"  [OK] footer: presente")


    print()
    print("  [OK] montador.py testado com sucesso")
    print("=" * 50)


if __name__ == "__main__":
    testar_montador()
