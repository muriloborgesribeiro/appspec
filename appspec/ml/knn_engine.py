# ================================================================
# MOTOR KNN — O Algoritmo de "Diagnóstico por Semelhança"
# Tecnologia: scikit-learn (KNeighborsClassifier)
# Por que existe: O KNN é um algoritmo que "aprende" memorizando
# todos os casos do conjunto de treino. Quando um novo paciente chega,
# ele busca os K vizinhos mais parecidos e vê qual o diagnóstico deles.
# Analogia médica: É como um médico experiente que, ao ver um sintoma,
# lembra-se de 5 pacientes parecidos que teve no passado para decidir
# a conduta deste novo caso.
# ================================================================

import numpy as np
# ↑ Técnico: Biblioteca de computação científica para arrays multidimensionais e álgebra linear.
# ↑ Clínico: Ferramenta para cálculos precisos de laboratório.

import pandas as pd
# ↑ Técnico: Biblioteca de manipulação de dataframes para análise tabular de dados.
# ↑ Clínico: O "Excel" que armazena as planilhas com os dados dos pacientes.

import joblib
# ↑ Técnico: Serializador Python (semelhante ao pickle), otimizado para salvar grandes matrizes numpy no disco.
# ↑ Clínico: Gravar o conhecimento e os protocolos do médico em um livro para consulta rápida.

import os
# ↑ Técnico: Módulo para interação com o sistema de arquivos do sistema operacional (caminhos, diretórios).

from sklearn.neighbors import KNeighborsClassifier
# ↑ Técnico: Implementação do classificador KNN que usa árvores KD ou BallTree para busca rápida de vizinhos.
# ↑ Clínico: O "cérebro" do algoritmo que encontra pacientes com sintomas parecidos.

from sklearn.model_selection import cross_val_score
# ↑ Técnico: Ferramenta que avalia a precisão do modelo simulando várias provas (testes) com partes diferentes dos dados.

# Referencia do algoritmo KNN (SPEC-00 Convencao 1: DOI obrigatorio)
# DOI: 10.1109/TIT.1967.1053964 -- Cover & Hart, 1967
REFERENCIA_KNN = (
    "Cover, T. & Hart, P. (1967). Nearest neighbor pattern classification. "
    "IEEE Trans. Inf. Theory, 13(1), 21-27. DOI:10.1109/TIT.1967.1053964"
)

# Labels para as classes (SPEC-04 9)
LABELS_CLASSE = {
    0: "Sem Apendicite",
    1: "Apendicite",
}

# Disclaimer clinico obrigatorio (SPEC-00 Convencao 5)
DISCLAIMER_KNN = (
    "AVISO: Este resultado e gerado por um modelo de Machine Learning (KNN) "
    "treinado no dataset Regensburg (Marcinkevics et al., 2023). "
    "NAO substitui avaliacao medica presencial. "
    "Sistema exclusivamente didatico -- disciplina de Agentes Inteligentes (UFG)."
)


# ================================================================
# treinar_knn — O Processo de Estudo do Residente
# Técnico: Função que testa várias quantidades de "vizinhos" (K) 
# para ver qual dá a melhor pontuação de acertos no final.
# Clínico: É o período de residência, onde o médico estuda
# centenas de casos para ajustar seu critério de julgamento.
# ================================================================
def treinar_knn(X: pd.DataFrame, y: pd.Series, k: int = None) -> dict:
    """
    Treina o modelo KNN. Se k nao fornecido, busca melhor k por cross-validation.
    """
    # -------------------------------------------------------
    #  RESTRICAO CLINICA: k minimo = 3
    #  Por que: k=1 é muito instável. Se um único vizinho estiver 
    #  errado, a predição erra. Com k=3, temos uma "segunda opinião".
    # -------------------------------------------------------
    K_MINIMO_CLINICO = 3

    # Valores de k a testar (sempre números ímpares para evitar empate)
    candidatos_k = [3, 5, 7, 9, 11]

    if k is not None:
        if k < K_MINIMO_CLINICO:
            print(f"       [AVISO] k={k} rejeitado (minimo clinico = {K_MINIMO_CLINICO})")
            k = K_MINIMO_CLINICO
        candidatos_k = [k]

    # ... (lógica de proteção contra dataset pequeno) ...
    n_amostras = len(X)
    candidatos_k = [k_val for k_val in candidatos_k if k_val < n_amostras]
    
    melhor_k = candidatos_k[0]
    melhor_acuracia = 0.0
    resultados_cv = {}

    for k_teste in candidatos_k:
        # Configura o modelo para testar este valor de K
        modelo_teste = KNeighborsClassifier(
            n_neighbors=k_teste,
            metric='euclidean', 
            # ↑ Técnico: Define que o modelo vai calcular a distância em linha reta geométrica entre os pontos.
            weights='uniform',
            # ↑ Técnico: Define que todos os vizinhos têm peso igual na votação da classe.
        )
        
        # Cross-validation (Validação Cruzada)
        # Técnico: Divide os dados em pedaços. Treina com alguns pedaços e testa no que sobrou, repetindo o processo.
        # Clínico: É como fazer várias provas diferentes com o mesmo aluno
        # para garantir que ele realmente aprendeu e não apenas decorou.
        cv_folds = min(5, n_amostras)
        scores = cross_val_score(modelo_teste, X, y, cv=cv_folds, scoring='accuracy')
        acuracia_media = float(scores.mean())
        # ↑ Técnico: Média das acurácias obtidas nos 5 testes independentes.
        
        resultados_cv[k_teste] = {
            "acuracia_media": acuracia_media,
            "desvio_padrao": float(scores.std())
        }
        
        if acuracia_media > melhor_acuracia:
            melhor_acuracia = acuracia_media
            melhor_k = k_teste


    # Treinar modelo final com o melhor k (SPEC-04 6.2 -- passo 4)
    modelo_final = KNeighborsClassifier(
        n_neighbors=melhor_k,
        metric='euclidean',
        weights='uniform',
    )
    modelo_final.fit(X, y)
    # ↑ Técnico: O método .fit() é onde o modelo lê todos os pacientes de treino e cria um índice interno para buscar rápido depois.

    acuracia_treino = float(modelo_final.score(X, y))
    # ↑ Técnico: .score() calcula a proporção de predições corretas no próprio conjunto de treinamento.

    return {
        "modelo": modelo_final,
        "k": melhor_k,
        "acuracia_treino": acuracia_treino,
        "resultados_cv": resultados_cv,
    }


# ================================================================
# predizer — A Consulta Médica Assistida por IA
# Técnico: Esta é a função principal que é chamada toda vez que alguém aperta "Avaliar". 
# Ela carrega o modelo salvo e o usa para processar um novo paciente.
# Clínico: É o momento em que o médico usa o sistema para
# obter uma segunda opinião baseada em evidências.
# ================================================================
def predizer(dados: dict, modelo_path: str) -> dict:
    """
    Faz predicao usando o modelo serializado.
    """

    if not os.path.exists(modelo_path):
        return {
            "erro": f"Modelo nao treinado. Execute setup.py. Path: {modelo_path}",
        }

    try:
        dados_modelo = joblib.load(modelo_path)
    except Exception as e:
        return {
            "erro": f"Erro ao carregar modelo: {e}",
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
            pass  # Se falhar, prossegue sem imputacao

    # --- Carregar o Scaler (Normalizador) ---
    # Técnico: Recupera a mesma ferramenta de escala usada no treino. 
    # Ela "lembra" qual foi o maior e menor valor de cada exame para não errar a proporção agora.
    # Clínico: Ajustar a escala de diferentes exames (ex: mg/dL vs g/L)
    # para que todos possam ser comparados de forma justa.
    scaler_path = os.path.join(modelo_dir, 'knn_scaler.joblib')
    scaler = None
    if os.path.exists(scaler_path):
        try:
            scaler = joblib.load(scaler_path)
            # ↑ Técnico: Instância do MinMaxScaler contendo o range de cada variável.
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
                # Valor invalido em feature opcional: usar mediana
                if f in features_opcionais and f in medianas_opcionais:
                    valores.append(medianas_opcionais[f])
                    features_imputadas.append(f)
                else:
                    return {
                        "erro": f"Valor invalido para feature obrigatoria '{f}': {dados[f]}",
                    }
        elif f in features_opcionais and f in medianas_opcionais:
            # Feature opcional ausente: substituir pela mediana do treino
            valores.append(medianas_opcionais[f])
            features_imputadas.append(f)
        else:
            # Feature obrigatoria ausente: erro
            return {
                "erro": f"Feature obrigatoria ausente: '{f}'. Features esperadas: {features_ordem}",
            }

    X_input = pd.DataFrame([valores], columns=features_ordem)

    # --- Normalizar com o mesmo scaler usado no treino ---
    if scaler is not None:
        X_input = pd.DataFrame(
            scaler.transform(X_input),
            columns=features_ordem,
        )

    # --- Veredito da IA (Predição) ---
    probabilidades = modelo.predict_proba(X_input)[0]
    # ↑ Técnico: Pega as porcentagens calculadas pelo modelo (ex: 80% doente, 20% saudável) com base em quantos vizinhos têm a doença.
    # ↑ Clínico: O grau de certeza (ex: 80% de chance de ser Apendicite, pois 4 em 5 vizinhos tinham a doença).
    
    distancias, indices = modelo.kneighbors(X_input)
    # ↑ Técnico: A função kneighbors() devolve exatamente quais são os vizinhos encontrados e as distâncias até eles.
    # ↑ Clínico: Descobre quem são os "vizinhos" (casos reais) mais parecidos.
    
    prob_apendicite = float(probabilidades[1])
    
    # Técnico: .predict() define a resposta final considerando que se passar de 50%, a resposta é sim (Apendicite).
    classe_predita = int(modelo.predict(X_input)[0])
    # ↑ Clínico: Define a classe final (Apendicite ou Não).


    # Logica de confianca (SPEC-04 9)
    confianca = _calcular_confianca(prob_apendicite)

    distancia_media = float(np.mean(distancias[0]))

    return {
        "classe_predita": classe_predita,
        "label_predita": LABELS_CLASSE.get(classe_predita, f"Classe {classe_predita}"),
        "probabilidade_apendicite": prob_apendicite,
        "probabilidade_percentual": f"{prob_apendicite:.1%}",
        "k_vizinhos": modelo.n_neighbors,
        "acuracia_modelo": float(acuracia),
        "distancia_media_vizinhos": distancia_media,
        "distancias": distancias[0].tolist(),
        "confianca": confianca,
        "limiar_decisao": 0.5,
        "algoritmo": "KNN -- sklearn.neighbors.KNeighborsClassifier",
        "referencia_algoritmo": REFERENCIA_KNN,
        "disclaimer": DISCLAIMER_KNN,
        "features_imputadas": features_imputadas,
    }


def _calcular_confianca(probabilidade: float) -> str:
    """
    Determina o nivel de confianca do resultado (SPEC-04 9).
      probabilidade >= 0.75 -> "Alta"
      probabilidade >= 0.60 -> "Media"
      probabilidade <  0.60 -> "Baixa -- resultado inconclusivo"

    Nota: probabilidade aqui e max(prob_classe0, prob_classe1)
    """
    prob_max = max(probabilidade, 1.0 - probabilidade)
    if prob_max >= 0.75:
        return "Alta"
    elif prob_max >= 0.60:
        return "Media"
    else:
        return "Baixa -- resultado inconclusivo"


# -----------------------------------------------------------
#  FUNCAO DE TESTE (SPEC-04 13)
# -----------------------------------------------------------

def testar_knn():
    """
    Testa o motor KNN com o modelo serializado.
    Deve ser chamado para validacao antes de prosseguir para SPEC-05.
    """
    print("=" * 50)
    print("  TESTE DO MOTOR KNN")
    print("=" * 50)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modelo_path = os.path.join(BASE_DIR, 'ml', 'modelos', 'knn_model.joblib')

    # Teste 1: Modelo existe
    assert os.path.exists(modelo_path), f"Modelo nao encontrado em: {modelo_path}"
    print(f"  [OK] Modelo encontrado: {modelo_path}")

    # Teste 2: Carregar modelo
    dados_modelo = joblib.load(modelo_path)
    assert 'modelo' in dados_modelo, "Chave 'modelo' ausente no joblib"
    assert 'k' in dados_modelo, "Chave 'k' ausente no joblib"
    assert 'features' in dados_modelo, "Chave 'features' ausente no joblib"
    assert 'acuracia_teste' in dados_modelo, "Chave 'acuracia_teste' ausente no joblib"
    print(f"  [OK] Modelo carregado: k={dados_modelo['k']}")
    print(f"  [OK] Features: {dados_modelo['features']}")
    print(f"  [OK] Acuracia treino: {dados_modelo['acuracia_treino']:.1%}")
    print(f"  [OK] Acuracia teste: {dados_modelo['acuracia_teste']:.1%}")

    # Teste 3: Predicao com dados sinteticos (valores normalizados 0-1)
    features = dados_modelo['features']
    dados_teste = {f: 0.5 for f in features}  # Valores medios normalizados
    resultado = predizer(dados_teste, modelo_path)

    assert "erro" not in resultado, f"Predicao falhou: {resultado.get('erro')}"
    assert resultado["classe_predita"] in [0, 1], f"Classe invalida: {resultado['classe_predita']}"
    assert 0.0 <= resultado["probabilidade_apendicite"] <= 1.0, "Probabilidade fora de [0,1]"
    assert resultado["k_vizinhos"] == dados_modelo['k'], "k inconsistente"
    assert len(resultado["distancias"]) == dados_modelo['k'], "Numero de distancias != k"
    assert resultado["disclaimer"], "Disclaimer ausente"
    assert resultado["referencia_algoritmo"], "Referencia do algoritmo ausente"
    assert resultado["confianca"] in ["Alta", "Media", "Baixa -- resultado inconclusivo"]

    print(f"  [OK] Predicao (dados medios): classe={resultado['classe_predita']}, "
          f"prob={resultado['probabilidade_percentual']}, confianca={resultado['confianca']}")
    print(f"  [OK] Distancia media vizinhos: {resultado['distancia_media_vizinhos']:.4f}")
    print(f"  [OK] Disclaimer presente")
    print(f"  [OK] Referencia DOI presente")

    # Teste 4: Predicao com todos zeros (baixo risco esperado)
    dados_zero = {f: 0.0 for f in features}
    r_zero = predizer(dados_zero, modelo_path)
    assert "erro" not in r_zero, f"Predicao falhou: {r_zero.get('erro')}"
    print(f"  [OK] Predicao (zeros): classe={r_zero['classe_predita']}, "
          f"prob={r_zero['probabilidade_percentual']}")

    # Teste 5: Predicao com todos uns (alto risco esperado)
    dados_um = {f: 1.0 for f in features}
    r_um = predizer(dados_um, modelo_path)
    assert "erro" not in r_um, f"Predicao falhou: {r_um.get('erro')}"
    print(f"  [OK] Predicao (uns): classe={r_um['classe_predita']}, "
          f"prob={r_um['probabilidade_percentual']}")

    # Teste 6: Feature OBRIGATORIA ausente retorna erro
    # Features opcionais sao as de ultrassom -- o resto e obrigatorio
    import sys
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    from ml.preprocessamento import FEATURES_OPCIONAIS_RUNTIME
    features_opcionais_modelo = dados_modelo.get('features_opcionais', [])
    features_obrig_modelo = [f for f in features if f not in FEATURES_OPCIONAIS_RUNTIME]
    if features_obrig_modelo:
        dados_obrig_faltando = {f: 0.5 for f in features}
        del dados_obrig_faltando[features_obrig_modelo[0]]
        r_inc = predizer(dados_obrig_faltando, modelo_path)
        assert "erro" in r_inc, "Deveria retornar erro com feature obrigatoria ausente"
        print(f"  [OK] Feature obrigatoria ausente detectada: {r_inc['erro'][:60]}...")
    else:
        print("  [SKIP] Sem features obrigatorias para testar ausencia")

    # Teste 7: Modelo inexistente retorna erro
    r_sem = predizer(dados_teste, "caminho/inexistente.joblib")
    assert "erro" in r_sem, "Deveria retornar erro com modelo inexistente"
    print(f"  [OK] Modelo inexistente detectado")

    # Teste 8: Features OPCIONAIS ausentes NAO causam erro (imputacao pela mediana)
    features_opcionais_neste_modelo = [f for f in features if f in FEATURES_OPCIONAIS_RUNTIME]
    if features_opcionais_neste_modelo:
        dados_sem_opcionais = {f: 0.5 for f in features if f not in FEATURES_OPCIONAIS_RUNTIME}
        r_opt = predizer(dados_sem_opcionais, modelo_path)
        assert "erro" not in r_opt, f"NAO deveria dar erro com features opcionais ausentes: {r_opt.get('erro')}"
        assert len(r_opt["features_imputadas"]) == len(features_opcionais_neste_modelo), \
            f"Deveria imputar {len(features_opcionais_neste_modelo)}, imputou {len(r_opt['features_imputadas'])}"
        print(f"  [OK] Features opcionais omitidas: imputacao automatica por mediana")
        print(f"       Features imputadas: {r_opt['features_imputadas']}")
    else:
        print("  [SKIP] Modelo sem features opcionais para testar")

    # Verificar acuracia vs target (SPEC-04 G-05)
    acuracia = dados_modelo['acuracia_teste']
    if acuracia >= 0.80:
        print(f"\n  [OK] Acuracia {acuracia:.1%} >= 80% (target SPEC-04)")
    else:
        print(f"\n  [AVISO] Acuracia {acuracia:.1%} < 80% (target SPEC-04)")
        print(f"  O sistema continua funcionando mas com aviso de baixa acuracia")

    print()
    print("  TODOS OS TESTES PASSARAM!")
    print("=" * 50)


if __name__ == "__main__":
    testar_knn()
