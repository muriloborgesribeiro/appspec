# APPSPEC — Sistema de Apoio ao Diagnóstico de Apendicite

Objetivo
--------
Ferramenta didática para apoiar a triagem de apendicite combinando a regra clínica determinística
(Alvarado Score) e um classificador KNN treinado no dataset Regensburg (UCI id=938). O foco é
pedagógico: expor e explicar explicitamente as tecnologias ensinadas na disciplina (Django,
KNN/scikit-learn, pandas, Orange3, joblib, matriz de confusão). O sistema deve rodar 100% offline
após a execução de `python setup.py`. Todo texto clínico é hardcoded com referências DOI; o
disclaimer clínico é obrigatório nas telas de resultado.


Como executar no Linux (bash)
---------------------
1. Abrir o terminal e executar
  `./start.sh`
2. Abrir no navegador: `http://localhost:8000`

Como executar no Windows (powershell)
---------------------
1. Abrir o powershell e executar
  `.\start.ps1`
2. Abrir no navegador: `http://localhost:8000`

Como executar passo a passo
---------------------
1. Opcional: Criar e ativar o ambiente virtual
2. Instalar dependências
  `pip install -r requirements.txt`
3. Executar o setup e gerar os artefatos:
   `python setup.py`
4. Iniciar o servidor Django:
   `python manage.py runserver`


Principais requisitos
---------------------
- `setup.py` único: download do dataset (ucimlrepo com fallback para `data/regensburg_raw.csv`),
  pré-processamento, treino do KNN, serialização do modelo (`ml/modelos/knn_model.joblib`),
  geração da matriz de confusão (.png), geração do workflow Orange3 (.ows) e execução de
  `manage.py migrate`.
- Motor determinístico Alvarado em `ml/alvarado.py`: 8 critérios implementados, retorno
  estruturado com `score` (0–10), classificação (baixo/moderado/alto) e detalhamento por critério
  com DOI. `assert 0 <= score <= 10` para validação de bounds.
- Motor KNN em `ml/knn_engine.py`: treino com scikit-learn, cross-validation para k ∈ {3,5,7,9,11},
  serialização com joblib, e função `predizer()` que devolve metadados pedagógicos (k usado,
  acurácia, distâncias dos vizinhos, probabilidade por classe, confiança).
- Módulo de avaliação `ml/avaliador.py`: calcula VP/FP/FN/VN, acurácia, sensibilidade,
  especificidade, VPP, VPN; gera imagem PNG da matriz de confusão e o `.ows` para Orange3.
- App Django `diagnostico/`: modelos (`Avaliacao`), forms (validações de range), views
  (index, avaliar, avaliacao_modelo, como_funciona, documentacao, historico), urls e context
  processor para injetar o painel pedagógico em todas as páginas.
- Interface: Django Templates + Bootstrap 5 com painel pedagógico lateral fixo e tela de
  resultado dual (Alvarado vs KNN). Disclaimer clínico visível e fixo.

Integrações e dependências
--------------------------
- Obrigatórias (runtime/setup): Python 3.11, scikit-learn, pandas, numpy, joblib, Django 4.2,
  matplotlib, seaborn.
- Necessárias apenas no primeiro run (download): ucimlrepo (fallback para CSV local se
  indisponível).
- Opcionais: Orange3 (apenas para abrir o `.ows`; o sistema deve gerar o `.ows` quando disponível).

Artefatos gerados
-----------------
- `data/regensburg_raw.csv` — dataset bruto (baixado ou fallback local).
- `data/regensburg_processed.csv` — dataset pré-processado.
- `ml/modelos/knn_model.joblib` — modelo serializado.
- `ml/modelos/knn_scaler.joblib` (se aplicável) — scaler usado na normalização.
- `ml/modelos/metricas.json` — resumo de métricas geradas no setup.
- `diagnostico/static/diagnostico/img/confusion_matrix.png` — imagem da matriz.
- `orange/validacao_knn.ows` — workflow Orange3 (opcional).

Estrutura de pastas
-------------------------------
- `setup.py`
- `manage.py`
- `diagnostico/` (Django app: models, views, forms, urls, templates, static)
- `ml/` (alvarado.py, knn_engine.py, avaliador.py, preprocessamento.py, modelos/)
- `data/` (raw e processed)
- `orange/` (validacao_knn.ows)
- `docs/` (referencias_clinicas.md)

Mecanismos de segurança pedagógica (anti-alucinação)
--------------------------------------------------
- Texto clínico hardcoded com DOI; nada gerado por LLM.
- Disclaimer obrigatório e não ocultável em telas de resultado.
- Validações estritas em `forms.py` (ex.: temperatura 35.0–42.0, leucócitos 1000–50000).
- Indicação de confiança do KNN: se probabilidade < 0.60, exibe aviso de resultado inconclusivo.
- Não coletar dados identificáveis; banco SQLite local sem exposição de rede.

Documentação
---------------------
Consulte specs/ para a especificação e definições detalhadas por componente.

