# CSS Tweaks — scientific-article-layout

## Ajustes finos no template.html

### Mudar paleta de cores
Substitua `#003366` (azul UFG) pelo hex desejado em todo o template.

### Aumentar tamanho de fonte global
No seletor `body`, altere `font-size: 9pt` para `9.5pt` ou `10pt`.

### Remover régua entre colunas
Em `.two-col`, remova ou comente `column-rule`.

### Forçar figura a não quebrar de página
Já coberto por `break-inside: avoid` na figura. Se ainda quebrar,
adicione `page-break-inside: avoid` (fallback para WeasyPrint antigo).

### Tabela com header colorido diferente
```css
thead tr { background: #8B0000; }  /* vinho */
```

### Ajustar espaço acima da primeira seção
```css
h2.sec-title:first-of-type { margin-top: 0; }
```

### Declaração de IA em destaque (caixa especial)
Adicione ao CSS:
```css
.ai-declaration {
  column-span: all;
  background: #fff8e1;
  border: 1pt solid #f9a825;
  padding: 5pt 8pt;
  margin: 8pt 0;
  font-size: 8pt;
}
```
E no content da seção:
```html
<div class="ai-declaration">
  <strong>Declaração de uso de IA generativa.</strong> ...
</div>
```
