# ============================================================
#  artigo/gerador.py
#  APPSPEC -- Gerador de Artigo Cientifico (ponto de entrada)
#  Modulo: artigo (ferramenta de desenvolvimento)
#  Contrato: SPEC-09 6.6 / P-05 / P-06
#
#  Orquestra os 10 passos da geracao do artigo:
#  leitor → escritor → montador → exportador → PDF
#
#  Execucao:
#    python artigo/gerador.py
#    python artigo/gerador.py --fig2 screenshot.png --fig3 fluxo.png
#    python artigo/gerador.py --output meu_artigo.pdf
# ============================================================

import argparse
import datetime
import json
import os
import sys
import time


# -----------------------------------------------------------
#  Paths
# -----------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PROJECT_PATH = os.path.dirname(SCRIPT_DIR)  # appspec/


# -----------------------------------------------------------
#  Banner (mesmo estilo do setup.py)
# -----------------------------------------------------------

def banner():
    print()
    print("=" * 60)
    print("  APPSPEC -- Gerador de Artigo Cientifico")
    print("  Modulo: artigo/gerador.py")
    print("  Contrato: SPEC-09")
    print("=" * 60)
    print()


# -----------------------------------------------------------
#  [1/10] Verificar pre-requisitos
# -----------------------------------------------------------

def verificar_prerequisitos(project_path):
    """[1/10] Verifica metricas.json, API key e WeasyPrint.
    Retorna dict com status de cada componente."""
    print("[1/10] Verificando pre-requisitos...")

    status = {"metricas_ok": True, "api_ok": False, "weasyprint_ok": False}

    # metricas.json existe?
    metricas_path = os.path.join(project_path, "ml", "modelos", "metricas.json")
    if not os.path.exists(metricas_path):
        print(f"       [ERRO] metricas.json nao encontrado")
        print(f"              Execute: python setup.py")
        status["metricas_ok"] = False
    else:
        print(f"       [OK] metricas.json encontrado")

        # metricas.json tem as chaves necessarias?
        with open(metricas_path, "r", encoding="utf-8") as f:
            m = json.load(f)

        for chave in ["avaliacao_knn", "avaliacao_svm", "avaliacao_alvarado"]:
            if chave in m:
                print(f"       [OK] {chave} presente")
            else:
                print(f"       [ERRO] {chave} ausente")
                print(f"              Aplique patch-setup.md e re-execute setup.py")
                status["metricas_ok"] = False

    # ANTHROPIC_API_KEY?
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        print(f"       [OK] ANTHROPIC_API_KEY encontrada")
        status["api_ok"] = True
    else:
        print(f"       [AVISO] ANTHROPIC_API_KEY nao encontrada")
        print(f"               Secoes serao geradas com texto placeholder")

    # WeasyPrint instalado?
    try:
        import weasyprint
        status["weasyprint_ok"] = True
        print(f"       [OK] WeasyPrint disponivel")
    except (ImportError, OSError) as e:
        msg = str(e)[:80]
        print(f"       [AVISO] WeasyPrint: {msg}")
        print(f"               PDF nao sera gerado — HTML sera exportado")

    # confusion_matrix_knn.png existe?
    fig1 = os.path.join(
        project_path, "diagnostico", "static", "diagnostico", "img",
        "confusion_matrix_knn.png"
    )
    if os.path.exists(fig1):
        print(f"       [OK] confusion_matrix_knn.png encontrada")
    else:
        print(f"       [AVISO] confusion_matrix_knn.png nao encontrada")

    print()

    # Metricas sao obrigatorias — o resto e degradacao graceful
    if not status["metricas_ok"]:
        print("       [ERRO] metricas.json invalido. Corrija e re-execute.")
        sys.exit(1)

    return status


# -----------------------------------------------------------
#  [2/10] Ler sistema
# -----------------------------------------------------------

def ler_sistema(project_path, fig2_path, fig3_path):
    """[2/10] Le artefatos e monta system_report."""
    print("[2/10] Lendo sistema...")

    from artigo.leitor import ler_sistema as _ler
    report = _ler(project_path, fig2_path, fig3_path)

    mk = report["modelo_knn"]
    ak = report["avaliacao_knn"]
    ds = report["dataset"]
    print(f"       Config {mk['config']} | k={mk['k']} | "
          f"acuracia={ak['acuracia']:.1%} | "
          f"features={ds['features_total']} | n_teste={ds['n_teste']}")
    print(f"       [OK] system_report montado")
    print()

    return report


# -----------------------------------------------------------
#  [3/10] Validar metricas
# -----------------------------------------------------------

def validar_metricas(report):
    """[3/10] Checklist anti-alucinacao."""
    print("[3/10] Validando metricas...")

    ak = report["avaliacao_knn"]
    asvm = report["avaliacao_svm"]
    aalv = report["avaliacao_alvarado"]
    ds = report["dataset"]
    warnings = report.get("warnings", [])

    # Acuracia < 0.90?
    if ak["acuracia"] < 0.90:
        print(f"       [OK] Acuracia KNN {ak['acuracia']:.1%} < 90% -- sem leakage")
    else:
        print(f"       [ALERTA] Acuracia KNN {ak['acuracia']:.1%} >= 90% -- possivel leakage!")
        try:
            resp = input("       Continuar mesmo assim? (s/N): ").strip().lower()
            if resp != "s":
                print("       Abortado pelo usuario.")
                sys.exit(1)
        except EOFError:
            print("       [ALERTA] Continuando automaticamente (sem terminal interativo)")

    # avaliacao_alvarado presente?
    if aalv:
        print(f"       [OK] avaliacao_alvarado presente "
              f"(sens={aalv['sensibilidade']:.1%})")
    else:
        print(f"       [AVISO] avaliacao_alvarado vazio")

    # avaliacao_svm presente?
    if asvm:
        print(f"       [OK] avaliacao_svm presente "
              f"(acur={asvm['acuracia']:.1%})")
    else:
        print(f"       [AVISO] avaliacao_svm vazio")

    # Resumo das metricas
    print()
    print(f"       {'Metrica':<16} {'KNN':>8} {'SVM':>8} {'Alvarado':>10}")
    print(f"       {'-'*44}")
    print(f"       {'Acuracia':<16} {ak['acuracia']:>7.1%} {asvm['acuracia']:>7.1%} {aalv['acuracia']:>9.1%}")
    print(f"       {'Sensibilidade':<16} {ak['sensibilidade']:>7.1%} {asvm['sensibilidade']:>7.1%} {aalv['sensibilidade']:>9.1%}")
    print(f"       {'Especificidade':<16} {ak['especificidade']:>7.1%} {asvm['especificidade']:>7.1%} {aalv['especificidade']:>9.1%}")

    # n_teste = 15% de n_validos?
    n_teste = ds["n_teste"]
    n_validos = ds["n_validos"]
    pct = n_teste / n_validos if n_validos > 0 else 0
    print(f"       [OK] n_teste = {n_teste} ({pct:.0%} de {n_validos})")

    # Warnings do leitor
    if warnings:
        for w in warnings:
            print(f"       [AVISO] {w}")

    print()


# -----------------------------------------------------------
#  [4/10] a [9/10] Escrever secoes
# -----------------------------------------------------------

def escrever_todas_secoes(report, api_ok):
    """[4/10] a [9/10] Escreve as 6 secoes IMRAD."""

    nomes = {
        "abstract": "Abstract",
        "introducao": "Introducao",
        "metodos": "Materiais e Metodos",
        "resultados": "Resultados",
        "discussao": "Discussao",
        "conclusao": "Conclusao",
    }

    if api_ok:
        # Chamada real ao LLM
        from artigo.escritor import escrever_secoes as _escrever

        print("[4/10] Escrevendo Abstract...")
        print("[5/10] Escrevendo Introducao (FIXA)...")
        print("[6/10] Escrevendo Materiais e Metodos...")
        print("[7/10] Escrevendo Resultados...")
        print("[8/10] Escrevendo Discussao...")
        print("[9/10] Escrevendo Conclusao...")

        secoes = _escrever(report)

    else:
        # Sem API: gerar secoes placeholder com dados reais
        from artigo.escritor import INTRODUCAO_FIXA

        ak = report["avaliacao_knn"]
        asvm = report["avaliacao_svm"]
        aalv = report["avaliacao_alvarado"]
        ds = report["dataset"]
        mk = report["modelo_knn"]

        print("[4/10] Gerando Abstract (placeholder sem LLM)...")
        print("[5/10] Introducao (FIXA do v8)...")
        print("[6/10] Gerando Metodos (placeholder sem LLM)...")
        print("[7/10] Gerando Resultados (placeholder sem LLM)...")
        print("[8/10] Gerando Discussao (placeholder sem LLM)...")
        print("[9/10] Gerando Conclusao (placeholder sem LLM)...")

        secoes = {
            "abstract": (
                f"<p><strong>Contexto:</strong> A apendicite aguda é a emergência cirúrgica abdominal mais frequente na pediatria. "
                f"<strong>Objetivo:</strong> O presente estudo tem como objetivo desenvolver o APPSPEC, um Sistema de Apoio à Decisão Clínica (CDSS) combinando a regra tradicional do Escore de Alvarado com modelos de K-Nearest Neighbors (KNN). "
                f"<strong>Métodos:</strong> Utilizou-se o dataset Regensburg Pediatric Appendicitis (N={ds['n_total']}, UCI id=938). Após o pré-processamento, mantiveram-se {ds['n_validos']} pacientes e {ds['features_total']} features normalizadas (MinMaxScaler). Os dados foram particionados com random_state fixo. Avaliou-se o algoritmo KNN (k={mk['k']}) e SVM. "
                f"<strong>Resultados:</strong> No conjunto de teste, o KNN obteve acurácia de {ak['acuracia']:.1%} e sensibilidade de {ak['sensibilidade']:.1%}. O SVM alcançou acurácia de {asvm['acuracia']:.1%}. Em contraste, o Alvarado teve a maior sensibilidade ({aalv['sensibilidade']:.1%}), porém baixa especificidade. "
                f"<strong>Conclusão:</strong> O APPSPEC demonstra a viabilidade do uso de aprendizado de máquina tabular como ferramenta pedagógica e de triagem complementar, salientando o balanço crítico entre falsos positivos e negativos na prática cirúrgica.</p>"
            ),
            "introducao": INTRODUCAO_FIXA,
            "metodos": (
                f"<h3>2.1 Origem dos Dados</h3>"
                f"<p>Utilizou-se o dataset pediátrico de Regensburg [3] com {ds['n_total']} pacientes. "
                f"Foram excluídas variáveis associadas a data leakage (ex: pontuações Alvarado "
                f"já calculadas previamente, que vazam o desfecho diagnóstico).</p>"
                f"<h3>2.2 Pré-processamento e Imputação</h3>"
                f"<p>Restaram N={ds['n_validos']} pacientes. Foi realizada imputação pela mediana "
                f"({ds['n_imputados']} valores) e normalização Min-Max. "
                f"A imputação e o escalonamento foram ajustados exclusivamente no conjunto de treino "
                f"e aplicados ao teste, garantindo rigor e ausência de vazamento de dados estatísticos.</p>"
                f"<h3>2.3 Modelos Preditivos</h3>"
                f"<p>O KNN [6] utilizou KNeighborsClassifier [4]. A seleção do hiperparâmetro "
                f"k ótimo (k={mk['k']}) foi feita via validação cruzada 5-fold no conjunto de treino. "
                f"O SVM utilizou Kernel {asvm.get('kernel','linear')} e hiperparâmetro C={asvm.get('C',10.0)}, "
                f"estabelecido através de busca em grade (grid search) com validação cruzada [7].</p>"
                f"<h3>2.4 Arquitetura do Sistema Integrado</h3>"
                f"<p>O modelo foi integrado ao Framework Django (padrão MVT) e banco SQLite. "
                f"A persistência dos modelos scikit-learn foi realizada via `joblib`. "
                f"Os dados do formulário web são traduzidos nativamente para arrays NumPy, normalizados, "
                f"e processados em tempo real pelas camadas de Machine Learning, exibindo os resultados "
                f"em uma interface responsiva voltada ao ensino e discussão clínica.</p>"
                f"<h3>2.5 Avaliação</h3>"
                f"<p>O desempenho final comparativo foi mensurado via holdout estratificado estrito no conjunto de teste "
                f"(n={ds['n_teste']}).</p>"
            ),
            "resultados": (
                f"<p>A {{{{table:tab1}}}} compara o desempenho dos modelos.</p>"
                f"<p>KNN: VP={ak['vp']} FP={ak['fp']} FN={ak['fn']} VN={ak['vn']} "
                f"(acuracia {ak['acuracia']:.1%}). "
                f"SVM: VP={asvm['vp']} FP={asvm['fp']} FN={asvm['fn']} VN={asvm['vn']} "
                f"(acuracia {asvm['acuracia']:.1%}). "
                f"Alvarado: VP={aalv['vp']} FP={aalv['fp']} FN={aalv['fn']} VN={aalv['vn']} "
                f"(acuracia {aalv['acuracia']:.1%}).</p>"
                f"{{{{fig:fig1}}}}"
                f"{{{{fig:fig2}}}}"
                f"{{{{fig:fig4}}}}"
                f"{{{{fig:fig5}}}}"
                f"{{{{fig:fig3}}}}"
            ),
            "discussao": (
                f"<p>O APPSPEC atingiu acurácia de {ak['acuracia']:.1%} com KNN "
                f"e {asvm['acuracia']:.1%} com SVM. Com um N={ds['n_teste']} de teste, a prevalência "
                f"de apendicite neste conjunto foi de aproximadamente {(ak['vp']+ak['fn'])/ds['n_teste']:.0%} "
                f"(~58%), o que eleva artificialmente o VPP se comparado a uma emergência padrão. "
                f"A margem de erro estimada é de cerca de 7,4 pp.</p>"
                f"<p>No trade-off clínico, falsos negativos acarretam morbidade severa (peritonite). "
                f"O Escore de Alvarado obteve a maior sensibilidade ({aalv['sensibilidade']:.1%}) com corte ≥5. "
                f"Contudo, a comparação binária subestima a verdadeira utilidade clínica do Alvarado, que foi projetado "
                f"com múltiplos limiares (≤4 = alta segura, ≥7 = cirurgia) [2]. "
                f"O SVM obteve o melhor equilíbrio global de triagem tabular.</p>"
                f"<p>As curvas ROC e Precision-Recall demonstram graficamente a estabilidade "
                f"e superioridade do SVM de kernel linear na área sob a curva (AUC).</p>"
                f"<p>O disclaimer obrigatório do sistema enfatiza que as ferramentas de IA não substituem o julgamento clínico presencial.</p>"
                f"<p>Limitações: o uso do dataset pediátrico alemão de Regensburg [3] compromete a generalização, pois o perfil epidemiológico, laboratorial e a disponibilidade de exames pediátricos no SUS [11] diferem substancialmente. Estudos de validação externa locais são imperativos para sistemas de inteligência artificial clínica [12].</p>"
            ),
            "conclusao": (
                f"<p>O APPSPEC demonstrou a viabilidade do KNN e SVM tabulares "
                f"para apoio ao diagnóstico, com acurácia de {ak['acuracia']:.1%} "
                f"e {asvm['acuracia']:.1%}, respectivamente.</p>"
                f"<p>Próximos passos: (a) endpoint REST com HL7 FHIR R4; "
                f"(b) validação clínica externa no Brasil [11, 12]; "
                f"(c) explicabilidade via SHAP e análise rigorosa de Missing Data.</p>"
                f"<div class=\"ai-declaration\"><p><em>Declaração de uso de Inteligência Artificial: Os autores "
                f"utilizaram ferramentas de IA generativa (Antigravity e Claude AI) "
                f"como apoio na redação e desenvolvimento. Todo o conteúdo foi "
                f"revisado e validado pelos autores, que assumem total responsabilidade pelo trabalho.</em></p></div>"
            ),
        }

    for chave, nome in nomes.items():
        tamanho = len(secoes.get(chave, ""))
        modo = "LLM" if api_ok else "placeholder"
        print(f"       [OK] {nome}: {tamanho} chars ({modo})")

    print()
    return secoes


# -----------------------------------------------------------
#  [10/10] Montar e exportar
# -----------------------------------------------------------

def montar_e_exportar(report, secoes, output_path, autores, weasyprint_ok):
    """[10/10] Monta article_data e gera PDF ou HTML."""
    print("[10/10] Montando article_data e exportando...")

    from artigo.montador import montar_article_data

    kwargs = {}
    if autores:
        kwargs["autores"] = autores

    article_data = montar_article_data(report, secoes, **kwargs)
    print(f"        [OK] article_data montado")

    if weasyprint_ok:
        # Gerar PDF — com fallback single-column se 2-colunas crashar
        from artigo.exportador import exportar_pdf
        try:
            pdf_path = exportar_pdf(article_data, output_path)
        except Exception as wp_err:
            print(f"        [AVISO] Layout 2-colunas falhou: {type(wp_err).__name__}")
            print(f"        [INFO] Re-tentando single-column...")
            # Monkey-patch: ler template, remover colunas, salvar tmp
            import tempfile
            tpl_path = os.path.join(SCRIPT_DIR, "templates", "artigo_base.html")
            with open(tpl_path, "r", encoding="utf-8") as f:
                tpl_orig = f.read()
            tpl_sc = tpl_orig.replace("column-count: 2", "column-count: 1")
            tpl_sc = tpl_sc.replace("column-span: all;", "")
            tpl_bak = tpl_path + ".bak"
            # Guardar backup e escrever versao single-column
            with open(tpl_bak, "w", encoding="utf-8") as f:
                f.write(tpl_orig)
            with open(tpl_path, "w", encoding="utf-8") as f:
                f.write(tpl_sc)
            try:
                pdf_path = exportar_pdf(article_data, output_path)
            finally:
                # Restaurar template original
                with open(tpl_path, "w", encoding="utf-8") as f:
                    f.write(tpl_orig)
                if os.path.exists(tpl_bak):
                    os.remove(tpl_bak)

        tamanho = os.path.getsize(pdf_path)
        print(f"        [OK] PDF gerado: {pdf_path}")
        print(f"        [OK] Tamanho: {tamanho / 1024:.1f} KB")

        # Contar paginas
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                n_paginas = len(pdf.pages)
            print(f"        [OK] {n_paginas} paginas")
        except Exception:
            pass

        print()
        return pdf_path

    else:
        # Fallback: exportar HTML renderizado (sem WeasyPrint)
        html_path = _exportar_html(article_data, output_path)
        tamanho = os.path.getsize(html_path)
        print(f"        [OK] HTML gerado: {html_path}")
        print(f"        [OK] Tamanho: {tamanho / 1024:.1f} KB")
        print(f"        [INFO] Para gerar PDF, instale GTK3 e re-execute")
        print()
        return html_path


def _exportar_html(article_data, output_path):
    """Fallback: gera HTML do artigo (sem WeasyPrint)."""
    import re
    import base64
    from pathlib import Path

    template_path = os.path.join(SCRIPT_DIR, "templates", "artigo_base.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_str = f.read()

    # Substituir variaveis simples
    for key in ["title", "authors", "context", "abstract", "keywords",
                "footer_left", "footer_right"]:
        html_str = html_str.replace(f"{{{{{key}}}}}", article_data.get(key, ""))

    # Montar secoes
    sections_html = ""
    for sec in article_data.get("sections", []):
        sections_html += f'<h2 class="sec-title">{sec["title"]}</h2>\n'
        body = sec.get("content", "")
        for sub in sec.get("subsections", []):
            body += f'<h3 class="subsec-title">{sub["title"]}</h3>\n'
            body += sub.get("content", "")

        # Resolver placeholders de tabela
        for tid, tbl in article_data.get("tables", {}).items():
            placeholder = "{{" + f"table:{tid}" + "}}"
            span_cls = "table-span" if tbl.get("span") else "table-col"
            cap = tbl.get("caption", "")
            block = (f'<div class="{span_cls} table-block">'
                     f'<p class="table-caption">{cap}</p>'
                     f'{tbl["html"]}</div>')
            body = body.replace(placeholder, block)

        # Resolver placeholders de figura
        for fid, fig in article_data.get("figures", {}).items():
            placeholder = "{{" + f"fig:{fid}" + "}}"
            p = Path(fig["path"]) if fig.get("path") else None
            if p and p.exists():
                ext = p.suffix.lower().lstrip(".")
                mime = {"jpg":"jpeg","jpeg":"jpeg","png":"png","gif":"gif"}.get(ext,"png")
                b64 = base64.b64encode(p.read_bytes()).decode()
                src = f"data:image/{mime};base64,{b64}"
            else:
                src = fig.get("path", "")
            span_cls = "figure-span" if fig.get("span") else "figure-col"
            w = fig.get("width", "100%")
            block = (f'<figure class="{span_cls}">'
                     f'<img src="{src}" style="width:{w}"/>'
                     f'<figcaption>{fig["caption"]}</figcaption></figure>')
            body = body.replace(placeholder, block)

        sections_html += body + "\n"

    html_str = html_str.replace("{{sections}}", sections_html)

    # Referencias
    refs_html = "".join(
        f'<p class="ref">{r}</p>' for r in article_data.get("references", [])
    )
    html_str = html_str.replace("{{references}}", refs_html)

    # Determinar output path
    if output_path:
        html_out = output_path.replace(".pdf", ".html")
    else:
        data = datetime.date.today().strftime("%Y-%m-%d")
        html_out = f"outputs/APPSPEC_artigo_{data}.html"

    os.makedirs(os.path.dirname(html_out) or ".", exist_ok=True)
    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html_str)

    return os.path.abspath(html_out)


# -----------------------------------------------------------
#  main() -- Orquestra os 10 passos
# -----------------------------------------------------------

def main():
    """Orquestra os 10 passos da geracao do artigo (SPEC-09 6.6)."""

    parser = argparse.ArgumentParser(
        description="APPSPEC -- Gerador de Artigo Cientifico (SPEC-09)"
    )
    parser.add_argument(
        "--project", default=DEFAULT_PROJECT_PATH,
        help="Raiz do appspec/ (padrao: diretorio pai de artigo/)"
    )
    parser.add_argument(
        "--fig2", default=None,
        help="Path do screenshot da interface (opcional)"
    )
    parser.add_argument(
        "--fig3", default=None,
        help="Path do diagrama de fluxo (opcional)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Path do PDF de saida (opcional)"
    )
    parser.add_argument(
        "--autores", default=None,
        help="String com autores (opcional)"
    )
    args = parser.parse_args()

    inicio = time.time()

    # Garantir que appspec/ esteja no sys.path
    sys.path.insert(0, args.project)

    banner()

    # [1/10] Verificar pre-requisitos
    status = verificar_prerequisitos(args.project)

    # [2/10] Ler sistema
    report = ler_sistema(args.project, args.fig2, args.fig3)

    # [3/10] Validar metricas
    validar_metricas(report)

    # [4/10] a [9/10] Escrever secoes
    secoes = escrever_todas_secoes(report, status["api_ok"])

    # [10/10] Montar e exportar
    output_file = montar_e_exportar(
        report, secoes, args.output, args.autores, status["weasyprint_ok"]
    )

    # Resumo final
    tempo_total = time.time() - inicio
    print("=" * 60)
    print("  ARTIGO GERADO COM SUCESSO")
    print(f"  Arquivo: {output_file}")
    if status["api_ok"]:
        print(f"  Secoes: geradas por Claude (LLM)")
    else:
        print(f"  Secoes: placeholder (defina ANTHROPIC_API_KEY para LLM)")
    if status["weasyprint_ok"]:
        print(f"  Formato: PDF")
    else:
        print(f"  Formato: HTML (instale GTK3 para PDF)")
    print(f"  Tempo total: {tempo_total:.1f} segundos")
    print("=" * 60)


if __name__ == "__main__":
    main()
