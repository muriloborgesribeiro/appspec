---
name: documentador-ml-dados
description: >
  Skill especializada em documentar as 10 páginas de dados e ML do bdpratico
  com screenshots reais do sistema, código anotado linha a linha, e explicação
  dos gráficos. Sabe a cadeia completa Django para cada tela, como o banco foi
  construído, como cada gráfico Plotly foi gerado, e o que cada métrica ML
  significa clinicamente.
---

# As 10 Páginas — URLs e Dados

| Página | URL | Tema |
|---|---|---|
| pagina9  | /pagina9 | Exportar CSV |
| pagina10 | /pagina10 | Importar CSV |
| pagina11 | /pagina11 | Upload TXT exames |
| pagina12 | /pagina12 | Gráfico batimento cardíaco |
| ia_import | /exemplo02/ia_import | Upload dataset ML |
| ia_import_list | /exemplo02/ia_import_list | Listar dataset |
| ia_knn_treino | /exemplo02/ia_knn_treino | Treinar KNN |
| ia_knn_matriz | /exemplo02/ia_knn_matriz | Matriz de Confusão |
| ia_knn_roc | /exemplo02/ia_knn_roc | Curva ROC |
| ia_knn_recall | /exemplo02/ia_knn_recall | Precision-Recall |

# Cadeia Django para Página com Gráfico
URL → View → Banco → go.Figure() → plot("div") → contexto → {{ grafico|safe }} → Browser
