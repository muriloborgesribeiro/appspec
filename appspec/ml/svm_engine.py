# ================================================================
# MOTOR SVM — O "Cirurgião Preciso"
# Técnico: O Support Vector Machine (SVM) é um algoritmo que tenta criar 
# uma "linha divisória" matemática para separar os dados. Ele usa fórmulas 
# (kernels) para conseguir separar até mesmo dados que estão muito misturados.
# Clínico: O SVM atua como um cirurgião minucioso que desenha a "linha de corte" 
# mais segura possível entre casos que precisam de cirurgia e casos que não precisam.
# ================================================================

import numpy as np
import pandas as pd
import joblib
import os
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score

# Referencia do algoritmo SVM (SPEC-00 Convencao 1: DOI obrigatorio)
# DOI: 10.1007/BF00994018 -- Cortes & Vapnik, 1995
REFERENCIA_SVM = (
    "Cortes, C. & Vapnik, V. (1995). Support-vector networks. "
    "Machine Learning, 20(3), 273-297. DOI:10.1007/BF00994018"
)

# Labels para as classes
LABELS_CLASSE = {
    0: "Sem Apendicite",
    1: "Apendicite",
}

# Disclaimer clinico obrigatorio (SPEC-00 Convencao 5)
DISCLAIMER_SVM = (
    "AVISO: Este resultado e gerado por um modelo de Machine Learning (SVM) "
    "treinado no dataset Regensburg (Marcinkevics et al., 2023). "
    "NAO substitui avaliacao medica presencial. "
    "Sistema exclusivamente didatico -- disciplina de Agentes Inteligentes (UFG)."
)


def treinar_svm(X: pd.DataFrame, y: pd.Series, kernel: str = None) -> dict:
    """
    Treina o modelo SVM. Se kernel nao fornecido, busca melhor kernel por cross-validation.

    Interface publica:
      INPUT:  X (DataFrame), y (Series), kernel (str, opcional)
      OUTPUT: {
          "modelo": SVC,
          "kernel": str,
          "C": float,
          "acuracia_treino": float,
          "resultados_cv": dict,
      }

    Tecnologia: sklearn.svm.SVC (ensinada na disciplina)
    Referencia: Cortes & Vapnik (1995). DOI:10.1007/BF00994018
    """
    # Combinacoes de hiperparametros a testar
    if kernel is not None:
        candidatos = [{"kernel": kernel, "C": 1.0}]
    else:
        candidatos = [
            {"kernel": "rbf",    "C": 0.1},
            {"kernel": "rbf",    "C": 1.0},
            {"kernel": "rbf",    "C": 10.0},
            {"kernel": "linear", "C": 0.1},
            {"kernel": "linear", "C": 1.0},
            {"kernel": "linear", "C": 10.0},
        ]

    n_amostras = len(X)
    melhor_config = candidatos[0]
    melhor_acuracia = 0.0
    resultados_cv = {}

    for cfg in candidatos:
        # Técnico: Criando o modelo SVM. O parâmetro probability=True faz o algoritmo 
        # calcular não apenas quem está doente, mas também a chance percentual disso.
        # Clínico: Testando diferentes "linhas de corte" na base histórica.
        modelo_teste = SVC(
            kernel=cfg["kernel"],
            C=cfg["C"],
            probability=True,   # Habilitar predict_proba via Platt scaling
            random_state=42,
        )
        # Cross-validation com cv=5
        cv_folds = min(5, n_amostras)
        scores = cross_val_score(modelo_teste, X, y, cv=cv_folds, scoring='accuracy')
        acuracia_media = scores.mean()

        chave = f"{cfg['kernel']}_C{cfg['C']}"
        resultados_cv[chave] = {
            'kernel': cfg['kernel'],
            'C': cfg['C'],
            'acuracia_media': float(acuracia_media),
            'desvio_padrao': float(scores.std()),
            'scores': scores.tolist(),
        }
        if acuracia_media > melhor_acuracia:
            melhor_acuracia = acuracia_media
            melhor_config = cfg

    # Treinar modelo final com a melhor configuracao
    modelo_final = SVC(
        kernel=melhor_config["kernel"],
        C=melhor_config["C"],
        probability=True,
        random_state=42,
    )
    modelo_final.fit(X, y)

    acuracia_treino = float(modelo_final.score(X, y))

    return {
        "modelo": modelo_final,
        "kernel": melhor_config["kernel"],
        "C": melhor_config["C"],
        "acuracia_treino": acuracia_treino,
        "resultados_cv": resultados_cv,
    }


def predizer(dados: dict, modelo_path: str) -> dict:
    """
    Faz predicao usando o modelo SVM serializado.

    Features opcionais: substituidas pela mediana do treino (imputer.joblib).

    Interface publica:
      INPUT:  dados (dict com as features), modelo_path (str)
      OUTPUT: {
          "classe_predita": int,
          "label_predita": str,
          "probabilidade_apendicite": float,
          "probabilidade_percentual": str,
          "kernel": str,
          "C": float,
          "acuracia_modelo": float,
          "confianca": str,
          "algoritmo": str,
          "referencia_algoritmo": str,
          "disclaimer": str,
          "features_imputadas": list,
      }

    Tecnologia: sklearn.svm.SVC
    Referencia: Cortes & Vapnik (1995). DOI:10.1007/BF00994018
    """
    if not os.path.exists(modelo_path):
        return {
            "erro": f"Modelo SVM nao treinado. Execute setup.py. Path: {modelo_path}",
        }

    try:
        dados_modelo = joblib.load(modelo_path)
    except Exception as e:
        return {
            "erro": f"Erro ao carregar modelo SVM: {e}",
        }

    modelo = dados_modelo['modelo']
    acuracia = dados_modelo.get('acuracia_teste', 0.0)
    features_ordem = dados_modelo['features']

    # --- Carregar imputer para features opcionais ---
    modelo_dir = os.path.dirname(modelo_path)
    imputer_path = os.path.join(modelo_dir, 'imputer.joblib')
    medianas_opcionais = {}
    features_opcionais = []
    if os.path.exists(imputer_path):
        try:
            imputer_dados = joblib.load(imputer_path)
            medianas_opcionais = imputer_dados.get('medianas_opcionais', {})
            features_opcionais = imputer_dados.get('features_opcionais', [])
        except Exception:
            pass

    # --- Carregar scaler (MinMaxScaler do treino) ---
    scaler_path = os.path.join(modelo_dir, 'knn_scaler.joblib')
    scaler = None
    if os.path.exists(scaler_path):
        try:
            scaler = joblib.load(scaler_path)
        except Exception:
            pass

    # --- Montar array de entrada com tratamento de opcionais ---
    features_imputadas = []
    valores = []
    for f in features_ordem:
        if f in dados and dados[f] is not None and dados[f] != '':
            try:
                valores.append(float(dados[f]))
            except (ValueError, TypeError):
                if f in features_opcionais and f in medianas_opcionais:
                    valores.append(medianas_opcionais[f])
                    features_imputadas.append(f)
                else:
                    return {
                        "erro": f"Valor invalido para feature obrigatoria '{f}': {dados[f]}",
                    }
        elif f in features_opcionais and f in medianas_opcionais:
            valores.append(medianas_opcionais[f])
            features_imputadas.append(f)
        else:
            return {
                "erro": f"Feature obrigatoria ausente: '{f}'. Features esperadas: {features_ordem}",
            }

    X_input = pd.DataFrame([valores], columns=features_ordem)

    # --- Normalizar com o mesmo scaler usado no treino ---
    # Técnico: Aplica exatamente a mesma escala (0 a 1) que foi usada no dia do treino, 
    # garantindo que o novo paciente não seja tratado com proporções erradas.
    if scaler is not None:
        X_input = pd.DataFrame(
            scaler.transform(X_input),
            columns=features_ordem,
        )

    # Predicao
    probabilidades = modelo.predict_proba(X_input)[0]
    # ↑ Técnico: Pega as porcentagens calculadas pelo modelo (ex: 80% doente, 20% saudável).
    # ↑ Clínico: Confiança do "cirurgião" baseada em quão longe o paciente está da linha de corte.

    prob_apendicite = float(probabilidades[1])

    # --- Decisao de classe ---
    # Usa limiar padrao 0.5 (sklearn default).
    # O limiar otimo de Youden e exibido na pagina de avaliacao
    # como ferramenta pedagogica, mas NAO e aplicado na inferencia
    # porque priorizamos sensibilidade em triagem de apendicite.
    classe_predita = int(modelo.predict(X_input)[0])

    # Logica de confianca
    confianca = _calcular_confianca(prob_apendicite)

    return {
        "classe_predita": classe_predita,
        "label_predita": LABELS_CLASSE.get(classe_predita, f"Classe {classe_predita}"),
        "probabilidade_apendicite": prob_apendicite,
        "probabilidade_percentual": f"{prob_apendicite:.1%}",
        "kernel": dados_modelo.get('kernel', '?'),
        "C": dados_modelo.get('C', 1.0),
        "acuracia_modelo": float(acuracia),
        "confianca": confianca,
        "limiar_decisao": 0.5,
        "algoritmo": "SVM -- sklearn.svm.SVC",
        "referencia_algoritmo": REFERENCIA_SVM,
        "disclaimer": DISCLAIMER_SVM,
        "features_imputadas": features_imputadas,
    }


def _calcular_confianca(probabilidade: float) -> str:
    """
    Determina o nivel de confianca do resultado.
      probabilidade >= 0.75 -> "Alta"
      probabilidade >= 0.60 -> "Media"
      probabilidade <  0.60 -> "Baixa -- resultado inconclusivo"
    """
    prob_max = max(probabilidade, 1.0 - probabilidade)
    if prob_max >= 0.75:
        return "Alta"
    elif prob_max >= 0.60:
        return "Media"
    else:
        return "Baixa -- resultado inconclusivo"


# -----------------------------------------------------------
#  FUNCAO DE TESTE
# -----------------------------------------------------------

def testar_svm():
    """
    Testa o motor SVM com o modelo serializado.
    """
    print("=" * 50)
    print("  TESTE DO MOTOR SVM")
    print("=" * 50)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modelo_path = os.path.join(BASE_DIR, 'ml', 'modelos', 'svm_model.joblib')

    # Teste 1: Modelo existe
    assert os.path.exists(modelo_path), f"Modelo nao encontrado em: {modelo_path}"
    print(f"  [OK] Modelo encontrado: {modelo_path}")

    # Teste 2: Carregar modelo
    dados_modelo = joblib.load(modelo_path)
    assert 'modelo' in dados_modelo, "Chave 'modelo' ausente no joblib"
    assert 'kernel' in dados_modelo, "Chave 'kernel' ausente no joblib"
    assert 'features' in dados_modelo, "Chave 'features' ausente no joblib"
    assert 'acuracia_teste' in dados_modelo, "Chave 'acuracia_teste' ausente no joblib"
    print(f"  [OK] Modelo carregado: kernel={dados_modelo['kernel']}, C={dados_modelo['C']}")
    print(f"  [OK] Features: {dados_modelo['features']}")
    print(f"  [OK] Acuracia treino: {dados_modelo['acuracia_treino']:.1%}")
    print(f"  [OK] Acuracia teste: {dados_modelo['acuracia_teste']:.1%}")

    # Teste 3: Predicao com dados sinteticos
    features = dados_modelo['features']
    dados_teste = {f: 0.5 for f in features}
    resultado = predizer(dados_teste, modelo_path)

    assert "erro" not in resultado, f"Predicao falhou: {resultado.get('erro')}"
    assert resultado["classe_predita"] in [0, 1], f"Classe invalida: {resultado['classe_predita']}"
    assert 0.0 <= resultado["probabilidade_apendicite"] <= 1.0, "Probabilidade fora de [0,1]"
    assert resultado["disclaimer"], "Disclaimer ausente"
    assert resultado["referencia_algoritmo"], "Referencia do algoritmo ausente"
    assert resultado["confianca"] in ["Alta", "Media", "Baixa -- resultado inconclusivo"]

    print(f"  [OK] Predicao (dados medios): classe={resultado['classe_predita']}, "
          f"prob={resultado['probabilidade_percentual']}, confianca={resultado['confianca']}")
    print(f"  [OK] Disclaimer presente")
    print(f"  [OK] Referencia DOI presente")

    print()
    print("  TODOS OS TESTES PASSARAM!")
    print("=" * 50)


if __name__ == "__main__":
    testar_svm()
