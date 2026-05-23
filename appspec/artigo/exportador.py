# ================================================================
# EXPORTADOR DE ARTIGO — A Gráfica Científica do Sistema
# Tecnologia: WeasyPrint (Conversor HTML → PDF)
# Por que existe: Transforma os dados brutos e o conteúdo gerado
# em um documento PDF profissional com layout de duas colunas.
# Analogia médica: É como a secretaria acadêmica que formata o 
# relato de caso de um residente para publicação em uma revista médica.
# ================================================================

import os
# ↑ Manipulação de caminhos e pastas no servidor

import re
# ↑ Técnico: Regular Expressions (Expressões Regulares) — é uma ferramenta do Python para procurar "fórmulas de texto" (como encontrar todas as palavras que começam com 'A').
# ↑ Clínico: Ferramenta de busca avançada para encontrar as lacunas (placeholders) no laudo.

import base64
# ↑ Técnico: Pega uma imagem (que é um arquivo de computador) e transforma em um texto gigante, assim o PDF consegue guardar a imagem dentro dele mesmo.
# ↑ Clínico: Converte imagens em texto para que fiquem embutidas no PDF.

import datetime
# ↑ Técnico: Módulo padrão do Python para manipulação de objetos temporais.

from pathlib import Path
# ↑ Técnico: Fornece classes para manipular caminhos no sistema de arquivos com semântica apropriada para cada OS (Windows/POSIX).




# -----------------------------------------------------------
#  Paths
# -----------------------------------------------------------

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "templates", "artigo_base.html"
)


# -----------------------------------------------------------
#  Verificacao do WeasyPrint
# -----------------------------------------------------------

def verificar_weasyprint():
    """Verifica se WeasyPrint esta instalado."""
    try:
        import weasyprint
        return True
    except ImportError:
        raise ImportError(
            "WeasyPrint nao instalado. Execute:\n"
            "  pip install weasyprint"
        )


# -----------------------------------------------------------
#  Funcao principal
# -----------------------------------------------------------

# ================================================================
# exportar_pdf — O Processo de Impressão Final
# Técnico: Esta função lê um arquivo HTML (que é como a página de um site), troca as partes em 
# branco pelos textos reais do artigo e usa a ferramenta WeasyPrint para salvar tudo como PDF.
# Clínico: É o momento de imprimir e carimbar o laudo oficial.
# ================================================================
def exportar_pdf(article_data: dict = None,
                 output_path: str = None) -> str:
    """
    Gera o PDF do artigo usando WeasyPrint.
    """
    verificar_weasyprint()
    from weasyprint import HTML
    # ↑ Técnico: O WeasyPrint é um "leitor de sites" que entende as cores e posições e "tira uma foto" em formato PDF.



    if article_data is None:
        raise RuntimeError(
            "article_data nao fornecido e nao encontrado no VSM. "
            "Execute montador.montar_article_data() primeiro."
        )

    # Output padrao com data
    if output_path is None:
        data = datetime.date.today().strftime("%Y-%m-%d")
        output_path = f"outputs/APPSPEC_artigo_{data}.pdf"

    # Criar diretorio outputs/ se nao existir
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Ler template
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(
            f"Template nao encontrado: {TEMPLATE_PATH}. "
            "Copie artigo_base.html para artigo/templates/."
        )

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_str = f.read()

    # --- Substituir variaveis simples ---
    for key in ["title", "authors", "context", "abstract", "keywords",
                "footer_left", "footer_right"]:
        html_str = html_str.replace(f"{{{{{key}}}}}", article_data.get(key, ""))

    # --- Montar blocos de figuras ---
    figs_html = {}
    for fid, fig in article_data.get("figures", {}).items():
        figs_html[fid] = _fig_block(fid, fig)

    # --- Montar blocos de tabelas ---
    tbls_html = {}
    for tid, tbl in article_data.get("tables", {}).items():
        tbls_html[tid] = _tbl_block(tid, tbl)

    # --- Montar seções do artigo ---
    sections_html = ""
    for sec in article_data.get("sections", []):
        sections_html += f'<h2 class="sec-title">{sec["title"]}</h2>\n'
        body = sec.get("content", "")
        
        # Resolver placeholders {{fig:X}} e {{table:X}}
        # Técnico: Roda a função que procura as tags do tipo {{fig:1}} no texto e 
        # as substitui pela imagem real antes de gerar o PDF.
        # Clínico: O escritor gera o texto com marcas. O exportador troca essas marcas pela imagem real.
        body = _resolve_placeholders(body, figs_html, tbls_html)
        sections_html += body + "\n"


    # Figuras/tabelas nao inseridas inline vao ao final
    for fid, fh in list(figs_html.items()):
        if fh not in sections_html:
            sections_html += fh + "\n"

    html_str = html_str.replace("{{sections}}", sections_html)

    # --- Referencias ---
    refs_html = "".join(
        f'<p class="ref">{r}</p>' for r in article_data.get("references", [])
    )
    html_str = html_str.replace("{{references}}", refs_html)

    # --- Sanitizar HTML para evitar bugs do WeasyPrint ---
    html_str = _sanitizar_html(html_str)

    # --- Salvar HTML intermediario ---
    html_debug = output_path.replace(".pdf", ".html") if output_path else "outputs/debug.html"
    _debug_dir = os.path.dirname(html_debug)
    if _debug_dir:
        os.makedirs(_debug_dir, exist_ok=True)
    with open(html_debug, "w", encoding="utf-8") as fdbg:
        fdbg.write(html_str)

    # --- Gerar PDF ---
    try:
        HTML(string=html_str, base_url="/").write_pdf(output_path)
    except AssertionError:
        raise RuntimeError(
            "WeasyPrint nao conseguiu renderizar o PDF.\n"
            "Causa provavel: secoes muito curtas para o layout de duas colunas.\n"
            "Solucao: verifique se o escritor.py gerou conteudo completo em todas "
            "as secoes (abstract, metodos, resultados, discussao, conclusao).\n"
            "O arquivo HTML foi salvo em: " + html_debug
        )

    pdf_path = os.path.abspath(output_path)


    return pdf_path


# -----------------------------------------------------------
#  Funcoes auxiliares do renderizador
#  (adaptadas de skills/scientific-article-layout/SKILL.md)
# -----------------------------------------------------------

def _strip_titulo_duplicado(body: str) -> str:
    """
    Remove título de seção que o LLM insere no início do conteúdo.
    O exportador já adiciona o título via sec["title"] — o LLM não deve repetir.
    Remove padrões como: <h2>3. RESULTADOS</h2>, <h2>3 RESULTADOS</h2>, etc.
    """
    import re
    body = re.sub(r'^\s*<h[12][^>]*>[^<]{1,60}</h[12]>\s*', '', body, flags=re.IGNORECASE)
    return body


def _img_src(path: str) -> str:
    """Converte path de imagem para data URI base64."""
    # Por que: O WeasyPrint às vezes tem dificuldade em achar arquivos no disco.
    # Transformar a imagem em texto (Base64) garante que ela apareça no PDF.
    p = Path(path)
    if not p.exists():
        return path 
    ext = p.suffix.lower().lstrip(".")
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:image/png;base64,{b64}"



def _fig_block(fid: str, fig: dict) -> str:
    """Monta bloco HTML de uma figura."""
    img_src = _img_src(fig["path"])
    span_cls = "figure-span" if fig.get("span") else "figure-col"
    w = fig.get("width", "100%")
    return (
        f'<figure class="{span_cls}">'
        f'<img src="{img_src}" style="width:{w}"/>'
        f'<figcaption>{fig["caption"]}</figcaption></figure>'
    )


def _tbl_block(tid: str, tbl: dict) -> str:
    """Monta bloco HTML de uma tabela."""
    span_cls = "table-span" if tbl.get("span") else "table-col"
    cap = tbl.get("caption", "")
    return (
        f'<div class="{span_cls} table-block">'
        f'<p class="table-caption">{cap}</p>'
        f'{tbl["html"]}</div>'
    )


def _resolve_placeholders(text: str, figs: dict, tbls: dict) -> str:
    """Substitui {{fig:ID}} e {{table:ID}} pelos blocos HTML."""
    def replacer(m):
        kind, fid = m.group(1), m.group(2)
        if kind == "fig":
            return figs.pop(fid, "")  # figura ausente: silencioso
        return tbls.pop(fid, "")  # tabela ausente: silencioso
    return re.sub(r"\{\{(fig|table):(\w+)\}\}", replacer, text)


def _strip_secao_duplicada(text: str, titulo: str) -> str:
    """Remove título de seção que o LLM eventualmente inclui no conteúdo."""
    import re
    # Remove <h2> no início do conteúdo (LLM repete o título)
    text = re.sub(r'^\s*<h[12][^>]*>.*?</h[12]>\s*', '', text, flags=re.IGNORECASE|re.DOTALL)
    return text


def _sanitizar_html(html_str: str) -> str:
    """Sanitiza HTML para evitar crash do WeasyPrint com elementos vazios."""
    # Remover tags inline vazias que causam IndexError no column layout
    # Ex: <strong></strong>, <em></em>, <span></span>
    html_str = re.sub(r'<(strong|em|span|a|b|i|u|code)\s*>\s*</\1>', '', html_str)
    # Remover <p> vazios
    html_str = re.sub(r'<p\s*>\s*</p>', '', html_str)
    # Remover <li> vazios
    html_str = re.sub(r'<li\s*>\s*</li>', '', html_str)
    # Remover <ul>/<ol> vazios
    html_str = re.sub(r'<(ul|ol)\s*>\s*</\1>', '', html_str)
    # Garantir que <br> é self-closing
    html_str = re.sub(r'<br\s*/?>', '<br/>', html_str)
    return html_str


# -----------------------------------------------------------
#  FUNCAO DE TESTE
# -----------------------------------------------------------

def testar_exportador():
    """
    Testa o exportador com article_data simulado.
    """
    print("=" * 50)
    print("  TESTE DO EXPORTADOR (artigo/exportador.py)")
    print("=" * 50)

    # Teste 1: WeasyPrint instalado (pode falhar no Windows sem GTK)
    weasyprint_ok = False
    try:
        verificar_weasyprint()
        import weasyprint
        weasyprint_ok = True
        print("  [OK] WeasyPrint disponivel")
    except (ImportError, OSError) as e:
        msg = str(e)[:80]
        print(f"  [AVISO] WeasyPrint indisponivel: {msg}")
        print("          No Windows: instale GTK3 runtime")
        print("          Testando logica sem gerar PDF...")

    # Teste 2: Template existe
    assert os.path.exists(TEMPLATE_PATH), \
        f"Template nao encontrado: {TEMPLATE_PATH}"
    print(f"  [OK] Template encontrado: {os.path.basename(TEMPLATE_PATH)}")

    # Teste 3: Montar article_data
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.dirname(script_dir)
    sys.path.insert(0, project_path)

    from artigo.leitor import ler_sistema
    from artigo.montador import montar_article_data

    report = ler_sistema(project_path)
    secoes_teste = {
        "abstract": "<p>Resumo teste do APPSPEC.</p>",
        "introducao": "<p>Introducao fixa teste.</p>",
        "metodos": "<p>Metodos com {{table:tab1}} para teste.</p>",
        "resultados": "<p>Resultados com {{fig:fig1}} para teste.</p>",
        "discussao": "<p>Discussao teste.</p>",
        "conclusao": "<p>Conclusao teste.</p>",
    }
    article_data = montar_article_data(report, secoes_teste)
    print(f"  [OK] article_data montado ({len(article_data)} chaves)")

    # Teste 4: Verificar funcoes auxiliares (sem WeasyPrint)
    test_text = "Ver {{fig:fig1}} e {{table:tab1}} aqui."
    figs_test = {"fig1": "<figure>FIG1</figure>"}
    tbls_test = {"tab1": "<div>TAB1</div>"}
    resolved = _resolve_placeholders(test_text, figs_test, tbls_test)
    assert "<figure>FIG1</figure>" in resolved, "Placeholder fig nao resolvido"
    assert "<div>TAB1</div>" in resolved, "Placeholder table nao resolvido"
    print(f"  [OK] _resolve_placeholders: fig e table substituidos")

    # Teste 5: Gerar PDF (somente se WeasyPrint funcionar)
    if weasyprint_ok:
        output_test = os.path.join(project_path, "outputs", "teste_exportador.pdf")
        pdf_path = exportar_pdf(article_data, output_test)
        assert os.path.exists(pdf_path), f"PDF nao gerado: {pdf_path}"
        tamanho = os.path.getsize(pdf_path)
        print(f"  [OK] PDF gerado: {pdf_path}")
        print(f"  [OK] Tamanho: {tamanho / 1024:.1f} KB")
        os.remove(pdf_path)
        print(f"  [OK] Arquivo de teste removido")
    else:
        print(f"  [SKIP] Geracao de PDF pulada (WeasyPrint sem GTK)")


    print()
    print("  [OK] exportador.py testado com sucesso")
    print("=" * 50)


if __name__ == "__main__":
    testar_exportador()
