---
name: scientific-article-layout
description: >
  Gera PDFs de artigos científicos com layout profissional de duas colunas usando WeasyPrint.
  Use esta skill sempre que o usuário quiser criar, reformatar, corrigir ou recompilar um artigo
  científico em PDF — incluindo trabalhos de conclusão, relatórios técnicos, papers acadêmicos,
  artigos no padrão UFG/ABNT, ou qualquer documento com estrutura de artigo (resumo, seções
  numeradas, tabelas, figuras com legenda). Acione também quando houver problemas de layout no
  PDF existente: espaço em branco excessivo, figuras pequenas, colunas desalinhadas, fontes
  inconsistentes, ou quando o usuário disser "o artigo ficou feio", "tem muito espaço em branco",
  "a imagem ficou pequena" ou similar.
---

# Scientific Article Layout — WeasyPrint

## Visão geral

Gera PDFs de artigos científicos com layout de duas colunas, usando **WeasyPrint** para
renderizar HTML+CSS como PDF. O fluxo é:

1. Montar um dicionário `article_data` com todo o conteúdo do artigo
2. Renderizar com o template HTML em `assets/template.html`
3. Salvar o PDF em `/mnt/user-data/outputs/`

---

## Instalação rápida

```bash
pip install weasyprint --break-system-packages 2>/dev/null | tail -3
python -c "import weasyprint; print('OK')"
```

Se `weasyprint` já estiver instalado, pule.

---

## Estrutura de dados do artigo

```python
article_data = {
    # ── Cabeçalho ──────────────────────────────────────────────────────────
    "title":    "Título Completo do Artigo",
    "authors":  "Autor A · Autor B · Instituição · Ano",
    "context":  "Trabalho de Conclusão · Disciplina X · Prof. Y · Ano",

    # ── Resumo ─────────────────────────────────────────────────────────────
    "abstract": "Texto do resumo em parágrafo único...",
    "keywords": "Palavra1 · Palavra2 · Palavra3",

    # ── Seções ─────────────────────────────────────────────────────────────
    # Cada seção é um dict com 'title' e 'content' (HTML permitido dentro)
    "sections": [
        {
            "title": "1. INTRODUÇÃO",
            "content": "<p>Parágrafo introdutório...</p>"
        },
        {
            "title": "2. MÉTODOS",
            "subsections": [
                {"title": "2.1 Dataset", "content": "<p>...</p>"},
                {"title": "2.2 Modelo",  "content": "<p>...</p>"},
            ]
        },
    ],

    # ── Figuras ────────────────────────────────────────────────────────────
    # Inseridas inline no content via placeholder {{fig:ID}}
    # ou listadas aqui para referência cruzada
    "figures": {
        "fig1": {
            "path":    "/caminho/absoluto/figura1.png",   # ou base64
            "caption": "Figura 1. Legenda da figura.",
            "width":   "100%",   # largura dentro da coluna ou span
            "span":    False,    # True = figura ocupa as DUAS colunas
        },
        "fig2": {
            "path":    "/caminho/absoluto/figura2.png",
            "caption": "Figura 2. Legenda.",
            "width":   "100%",
            "span":    True,     # screenshot largo → ocupa duas colunas
        },
    },

    # ── Tabelas ────────────────────────────────────────────────────────────
    # Inseridas inline via {{table:ID}} no content
    "tables": {
        "tab1": {
            "caption": "Tabela 1. Comparação de modelos.",
            "html":    "<table>...</table>",   # HTML completo da tabela
            "span":    False,
        }
    },

    # ── Referências ────────────────────────────────────────────────────────
    "references": [
        "[1] Autor A. Título. Journal. Ano. DOI:...",
        "[2] Autor B. Título. Journal. Ano.",
    ],

    # ── Rodapé ─────────────────────────────────────────────────────────────
    "footer_left":  "Disciplina · Instituição · Ano",
    "footer_right": "NomeDoSistema · Subtítulo",
}
```

---

## Como inserir figuras e tabelas no texto

No campo `"content"` de uma seção, use placeholders:

```html
<p>Como mostra a {{fig:fig1}}, o resultado foi...</p>
<p>A {{table:tab1}} compara os modelos.</p>
```

O renderizador substitui o placeholder pelo bloco `<figure>` ou `<div class="table-block">` completo,
respeitando `span=True/False`.

---

## Script de renderização

```python
import re
import base64
from pathlib import Path
from weasyprint import HTML, CSS

def render_article(article_data: dict, output_path: str) -> None:
    """Renderiza article_data como PDF de duas colunas com WeasyPrint."""

    template_path = Path("/tmp/scientific-article-layout/assets/template.html")
    html_str = template_path.read_text(encoding="utf-8")

    # ── Substitui variáveis simples ──────────────────────────────────────
    for key in ["title","authors","context","abstract","keywords",
                "footer_left","footer_right"]:
        html_str = html_str.replace(f"{{{{{key}}}}}", article_data.get(key,""))

    # ── Monta blocos de figuras ──────────────────────────────────────────
    def fig_block(fid, fig):
        img_src = _img_src(fig["path"])
        span_cls = "figure-span" if fig.get("span") else "figure-col"
        w = fig.get("width","100%")
        return (f'<figure class="{span_cls}">'
                f'<img src="{img_src}" style="width:{w}"/>'
                f'<figcaption>{fig["caption"]}</figcaption></figure>')

    # ── Monta blocos de tabelas ──────────────────────────────────────────
    def tbl_block(tid, tbl):
        span_cls = "table-span" if tbl.get("span") else "table-col"
        cap = tbl.get("caption","")
        return (f'<div class="{span_cls} table-block">'
                f'<p class="table-caption">{cap}</p>'
                f'{tbl["html"]}</div>')

    figs_html  = {fid: fig_block(fid, f)
                  for fid, f in article_data.get("figures",{}).items()}
    tbls_html  = {tid: tbl_block(tid, t)
                  for tid, t in article_data.get("tables",{}).items()}

    # ── Monta seções ────────────────────────────────────────────────────
    sections_html = ""
    for sec in article_data.get("sections", []):
        sections_html += f'<h2 class="sec-title">{sec["title"]}</h2>\n'
        body = sec.get("content","")
        for sub in sec.get("subsections",[]):
            body += f'<h3 class="subsec-title">{sub["title"]}</h3>\n'
            body += sub.get("content","")
        # resolve placeholders dentro do conteúdo da seção
        body = _resolve_placeholders(body, figs_html, tbls_html)
        sections_html += body + "\n"

    # figuras/tabelas que não foram inseridas inline vão ao final
    for fid, fh in figs_html.items():
        if f"{{{{fig:{fid}}}}}" not in sections_html and fh not in sections_html:
            sections_html += fh + "\n"

    html_str = html_str.replace("{{sections}}", sections_html)

    # ── Referências ─────────────────────────────────────────────────────
    refs_html = "".join(f'<p class="ref">{r}</p>' for r in article_data.get("references",[]))
    html_str = html_str.replace("{{references}}", refs_html)

    HTML(string=html_str, base_url="/").write_pdf(output_path)
    print(f"✅  PDF gerado: {output_path}")


def _img_src(path: str) -> str:
    """Converte path de imagem para data URI base64."""
    p = Path(path)
    if not p.exists():
        return path  # assume que é URL ou data URI
    ext = p.suffix.lower().lstrip(".")
    mime = {"jpg":"jpeg","jpeg":"jpeg","png":"png","gif":"gif","svg":"svg+xml"}.get(ext,"png")
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:image/{mime};base64,{b64}"


def _resolve_placeholders(text: str, figs: dict, tbls: dict) -> str:
    def replacer(m):
        kind, fid = m.group(1), m.group(2)
        if kind == "fig":
            return figs.pop(fid, f"[Figura {fid} não encontrada]")
        return tbls.pop(fid, f"[Tabela {fid} não encontrada]")
    return re.sub(r"\{\{(fig|table):(\w+)\}\}", replacer, text)
```

---

## Decisões de layout

| Situação | Decisão |
|---|---|
| Screenshot de sistema (largo) | `span: True` — ocupa 2 colunas |
| Matriz de confusão / gráfico | `span: False` — dentro de 1 coluna |
| Tabela com ≤4 colunas | `span: False` |
| Tabela com ≥5 colunas | `span: True` |
| Espaço em branco excessivo | Verificar se há `<br>` ou `Spacer` desnecessário no content |
| Figura pequena | Checar `width` no dict; aumentar para `"100%"` ou `"90%"` |

---

## Checklist de qualidade antes de gerar

- [ ] Todas as figuras com `path` apontando para arquivo existente
- [ ] Screenshots de sistema com `span: True`
- [ ] Placeholders `{{fig:X}}` e `{{table:X}}` inseridos no `content` correto
- [ ] `footer_left` e `footer_right` preenchidos
- [ ] Referências em lista

---

## Referências adicionais

- `references/css-tweaks.md` — ajustes finos de CSS (fontes, espaçamentos, cores)
- `assets/template.html` — template HTML base (editar apenas para customizações estruturais)
