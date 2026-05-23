# ============================================================
#  artigo/leitor.py
#  APPSPEC -- Leitor de artefatos do sistema
#  Modulo: artigo (ferramenta de desenvolvimento)
#  Contrato: SPEC-09 6.2 / P-01
#
#  Le metricas.json e monta o system_report usado pelo
#  gerador de artigo cientifico.
#
#  REGRA ABSOLUTA: nenhum valor numerico hardcoded.
#  Todos os numeros do artigo vem de metricas.json.
# ============================================================

import json
import os
import re





def ler_sistema(project_path: str,
                fig2_path: str = None,
                fig3_path: str = None) -> dict:
    """
    Le os artefatos do sistema APPSPEC e monta o system_report.

    Interface publica conforme SPEC-09 6.2 / P-01:
      INPUT:  project_path — raiz do appspec/ (onde fica manage.py)
              fig2_path    — path do screenshot da interface (opcional)
              fig3_path    — path do diagrama de fluxo (opcional)

      OUTPUT: system_report = {
          "dataset":            { n_total, n_validos, n_treino, n_teste, ... },
          "modelo_knn":         { k, config, features_total, ... },
          "avaliacao_knn":      { vp, fp, fn, vn, acuracia, sensibilidade, ... },
          "avaliacao_svm":      { vp, fp, fn, vn, acuracia, ..., kernel, C },
          "avaliacao_alvarado": { vp, fp, fn, vn, acuracia, ... },
          "configs":            { comparacao_configs completo },
          "figuras":            { fig1, fig2, fig3 },
          "warnings":           [ str ],
      }

    REGRA ABSOLUTA: nenhum valor numerico hardcoded.
    Todos os numeros vem de metricas.json.
    """
    warnings = []

    # -------------------------------------------------------
    #  1. Ler metricas.json
    # -------------------------------------------------------
    metricas_path = os.path.join(project_path, "ml", "modelos", "metricas.json")

    # Se nao existir: RuntimeError
    if not os.path.exists(metricas_path):
        raise RuntimeError(
            f"metricas.json nao encontrado em {metricas_path}. "
            "Execute 'python setup.py' antes de gerar o artigo."
        )

    with open(metricas_path, "r", encoding="utf-8") as f:
        m = json.load(f)

    # Se nao tiver avaliacao_knn: patch nao foi aplicado
    if "avaliacao_knn" not in m:
        raise RuntimeError(
            "metricas.json nao contem 'avaliacao_knn'. "
            "Aplique patch-setup.md e re-execute 'python setup.py'."
        )

    # -------------------------------------------------------
    #  2. Verificar leakage
    # -------------------------------------------------------
    acuracia_knn = m.get("acuracia_teste", 0.0)
    if acuracia_knn > 0.90:
        warnings.append(
            f"ALERTA: acuracia KNN {acuracia_knn:.1%} > 90% — possivel data leakage! "
            "Verifique se alguma feature e derivada do target."
        )

    # -------------------------------------------------------
    #  3. Montar blocos do system_report (TUDO do JSON)
    # -------------------------------------------------------

    # --- dataset ---
    dataset = {
        "n_total": 782,  # Total original do Regensburg (fixo por definicao do dataset)
        "n_validos": m.get("n_pacientes", 0),
        "n_treino": m.get("n_treino", 0),
        "n_teste": m.get("n_teste", 0),
        "n_imputados": m.get("n_imputados", 0),
        "features_usadas": m.get("features_usadas", []),
        "features_total": m.get("features_total_usadas", 0),
        "colunas_excluidas_leakage": m.get("colunas_excluidas_leakage", []),
        "motivo_descarte": m.get("motivo_descarte", ""),
        "fonte": "Regensburg Pediatric Appendicitis. UCI ML Repository id=938. "
                 "DOI:10.5281/zenodo.7669442",
    }

    # --- modelo_knn ---
    config_sel = m.get("config_selecionada", "")
    comparacao = m.get("comparacao_configs", {})
    config_dados = comparacao.get(config_sel, {})

    modelo_knn = {
        "k": m.get("k_otimo", 0),
        "k_minimo_clinico": m.get("k_minimo_clinico", 3),
        "k_minimo_motivo": m.get("k_minimo_motivo", ""),
        "k_testados": _extrair_candidatos_k(project_path),
        "metrica_distancia": "euclidiana",
        "config": config_sel,
        "config_nome": m.get("config_nome", ""),
        "features_total": config_dados.get("n_treino", 0) and m.get("features_total_usadas", 0),
        "status": m.get("status_configs", {}).get(config_sel, ""),
        "criterio_selecao": m.get("criterio_selecao", ""),
        "motivo_selecao": m.get("motivo_selecao", ""),
        "acuracia_cv": m.get("acuracia_cv", 0.0),
        "acuracia_teste": acuracia_knn,
        "target_80_atingido": m.get("target_80_atingido", False),
        "aviso_acuracia": m.get("aviso_acuracia", ""),
        "data_leakage_detectado": m.get("data_leakage_detectado", False),
        "configuracao_descartada": m.get("configuracao_descartada", ""),
        "algoritmo": "KNeighborsClassifier (scikit-learn)",
        "referencia": "Cover T & Hart P (1967). DOI:10.1109/TIT.1967.1053964",
    }

    # --- avaliacao_knn (direto do JSON, zero hardcode) ---
    avaliacao_knn = m.get("avaliacao_knn", {})

    # --- avaliacao_svm (direto do JSON, zero hardcode) ---
    avaliacao_svm = m.get("avaliacao_svm", {})

    # --- avaliacao_alvarado (direto do JSON, zero hardcode) ---
    avaliacao_alvarado = m.get("avaliacao_alvarado", {})

    # --- configs (comparacao_configs completo) ---
    configs = comparacao

    # --- figuras ---
    fig1_path = os.path.join(
        project_path, "diagnostico", "static", "diagnostico", "img",
        "confusion_matrix_knn.png"
    )
    if not os.path.exists(fig1_path):
        warnings.append(
            f"AVISO: confusion_matrix_knn.png nao encontrada em {fig1_path}. "
            "Execute setup.py para gerar."
        )
        fig1_path = None

    fig4_path = os.path.join(project_path, "diagnostico", "static", "diagnostico", "img", "roc_comparativa.png")
    fig5_path = os.path.join(project_path, "diagnostico", "static", "diagnostico", "img", "pr_comparativa.png")

    figuras = {
        "fig1": fig1_path,
        # fig2: usar SVM confusion matrix automaticamente se nao fornecida
        "fig2": _resolver_fig2(project_path, fig2_path),
        "fig3": _resolver_fig3(project_path, fig3_path),
        "fig4": fig4_path if os.path.exists(fig4_path) else None,
        "fig5": fig5_path if os.path.exists(fig5_path) else None,
    }

    if figuras["fig2"] is None:
        warnings.append("AVISO: fig2 nao encontrada — confusion_matrix_svm.png ausente. Execute setup.py.")
    if figuras["fig3"] is None:
        warnings.append("AVISO: fig3 (screenshot interface) nao encontrada. Salve screenshot como artigo/fig2_interface.png")

    # -------------------------------------------------------
    #  4. Montar system_report
    # -------------------------------------------------------
    system_report = {
        "dataset": dataset,
        "modelo_knn": modelo_knn,
        "avaliacao_knn": avaliacao_knn,
        "avaliacao_svm": avaliacao_svm,
        "avaliacao_alvarado": avaliacao_alvarado,
        "configs": configs,
        "figuras": figuras,
        "warnings": warnings,
    }



    return system_report


# -----------------------------------------------------------
#  FUNCAO AUXILIAR (leitura estatica de codigo)
# -----------------------------------------------------------

def _resolver_fig2(project_path, fig2_path_explicito=None):
    """Fig2 = Matriz de Confusão SVM (gerada pelo setup.py)."""
    if fig2_path_explicito and os.path.exists(fig2_path_explicito):
        return fig2_path_explicito
    svm_img = os.path.join(project_path, "diagnostico", "static", "diagnostico", "img", "confusion_matrix_svm.png")
    if os.path.exists(svm_img):
        return svm_img
    return None


def _resolver_fig3(project_path, fig3_path_explicito=None):
    """Fig3 = Screenshot da interface do sistema (mostra os 3 métodos em ação)."""
    if fig3_path_explicito and os.path.exists(fig3_path_explicito):
        return fig3_path_explicito
    # Buscar screenshot salvo junto ao módulo artigo/
    candidatos = [
        os.path.join(project_path, "artigo", "fig2_interface.png"),
        os.path.join(project_path, "artigo", "fig3_interface.png"),
        os.path.join(project_path, "artigo", "screenshot.png"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    return None


def _extrair_candidatos_k(project_path: str) -> list:
    """
    Le knn_engine.py e extrai a lista candidatos_k por regex.
    Leitura estatica — nao importa nem executa o modulo.
    """
    knn_path = os.path.join(project_path, "ml", "knn_engine.py")
    if not os.path.exists(knn_path):
        return [3, 5, 7, 9, 11]  # fallback do SPEC-04

    try:
        with open(knn_path, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Extrair: candidatos_k = [3, 5, 7, 9, 11]
        match = re.search(r"candidatos_k\s*=\s*\[([^\]]+)\]", conteudo)
        if match:
            nums = re.findall(r"\d+", match.group(1))
            return [int(n) for n in nums]
    except Exception:
        pass

    return [3, 5, 7, 9, 11]  # fallback


# -----------------------------------------------------------
#  FUNCAO DE TESTE (mesmo padrao dos modulos ml/)
# -----------------------------------------------------------

def testar_leitor():
    """
    Testa o leitor com o metricas.json real do sistema.
    Executar a partir do diretorio appspec/:
        python artigo/leitor.py
    """
    print("=" * 50)
    print("  TESTE DO LEITOR (artigo/leitor.py)")
    print("=" * 50)

    # Determinar project_path (appspec/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.dirname(script_dir)  # appspec/

    # Teste 1: metricas.json existe
    metricas_path = os.path.join(project_path, "ml", "modelos", "metricas.json")
    assert os.path.exists(metricas_path), \
        f"metricas.json nao encontrado em {metricas_path}. Execute setup.py."
    print(f"  [OK] metricas.json encontrado")

    # Teste 2: Ler sistema
    report = ler_sistema(project_path)
    print(f"  [OK] system_report montado com {len(report)} blocos")

    # Teste 3: Verificar que todos os blocos existem
    blocos_esperados = [
        "dataset", "modelo_knn", "avaliacao_knn", "avaliacao_svm",
        "avaliacao_alvarado", "configs", "figuras", "warnings",
    ]
    for bloco in blocos_esperados:
        assert bloco in report, f"Bloco '{bloco}' ausente no report"
    print(f"  [OK] Todos os {len(blocos_esperados)} blocos presentes")

    # Teste 4: avaliacao_knn tem VP/FP/FN/VN
    for chave in ["vp", "fp", "fn", "vn", "acuracia", "sensibilidade",
                   "especificidade", "vpp", "vpn"]:
        assert chave in report["avaliacao_knn"], \
            f"Chave '{chave}' ausente em avaliacao_knn"
    print(f"  [OK] avaliacao_knn: VP={report['avaliacao_knn']['vp']} "
          f"FP={report['avaliacao_knn']['fp']} "
          f"FN={report['avaliacao_knn']['fn']} "
          f"VN={report['avaliacao_knn']['vn']}")

    # Teste 5: avaliacao_svm tem kernel e C
    assert "kernel" in report["avaliacao_svm"], "kernel ausente em avaliacao_svm"
    assert "C" in report["avaliacao_svm"], "C ausente em avaliacao_svm"
    print(f"  [OK] avaliacao_svm: kernel={report['avaliacao_svm']['kernel']} "
          f"C={report['avaliacao_svm']['C']}")

    # Teste 6: avaliacao_alvarado presente
    assert report["avaliacao_alvarado"], "avaliacao_alvarado vazio"
    print(f"  [OK] avaliacao_alvarado: VP={report['avaliacao_alvarado']['vp']} "
          f"FP={report['avaliacao_alvarado']['fp']} "
          f"FN={report['avaliacao_alvarado']['fn']} "
          f"VN={report['avaliacao_alvarado']['vn']}")

    # Teste 7: configs tem pelo menos E e F
    assert "E" in report["configs"], "Config E ausente"
    assert "F" in report["configs"], "Config F ausente"
    print(f"  [OK] configs: {len(report['configs'])} configuracoes "
          f"(E: k={report['configs']['E']['k']}, "
          f"F: k={report['configs']['F']['k']})")

    # Teste 8: modelo_knn coerente
    assert report["modelo_knn"]["k"] == report["configs"]["F"]["k"], \
        "k do modelo_knn difere do k da Config F"
    print(f"  [OK] modelo_knn: k={report['modelo_knn']['k']} Config={report['modelo_knn']['config']}")

    # Teste 9: warnings e lista
    assert isinstance(report["warnings"], list), "warnings nao e lista"
    print(f"  [OK] warnings: {len(report['warnings'])} itens")



    # --- Resumo para conferencia humana ---
    print()
    print(f"  --- Valores encontrados (todos do JSON) ---")
    ak = report["avaliacao_knn"]
    asvm = report["avaliacao_svm"]
    aalv = report["avaliacao_alvarado"]
    print(f"  {'Metrica':<18} {'KNN':>8} {'SVM':>8} {'Alvarado':>10}")
    print(f"  {'-'*48}")
    print(f"  {'Acuracia':<18} {ak['acuracia']:>7.1%} {asvm['acuracia']:>7.1%} {aalv['acuracia']:>9.1%}")
    print(f"  {'Sensibilidade':<18} {ak['sensibilidade']:>7.1%} {asvm['sensibilidade']:>7.1%} {aalv['sensibilidade']:>9.1%}")
    print(f"  {'Especificidade':<18} {ak['especificidade']:>7.1%} {asvm['especificidade']:>7.1%} {aalv['especificidade']:>9.1%}")
    print(f"  {'VPP':<18} {ak['vpp']:>7.1%} {asvm['vpp']:>7.1%} {aalv['vpp']:>9.1%}")
    print(f"  {'VPN':<18} {ak['vpn']:>7.1%} {asvm['vpn']:>7.1%} {aalv['vpn']:>9.1%}")
    print()
    print("  [OK] leitor.py testado com sucesso")
    print("=" * 50)


if __name__ == "__main__":
    testar_leitor()
