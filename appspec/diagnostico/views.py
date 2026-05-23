# ================================================================
# AS VIEWS — O Médico Plantonista do Sistema
# Por que existe: As views são o coração lógico da aplicação. 
# Elas recebem o pedido do paciente (usuário), analisam os dados, 
# consultam os especialistas (IA e Alvarado) e decidem o que 
# mostrar na tela (o laudo final).
# Analogia médica: É como o médico plantonista que recebe a ficha 
# de triagem, realiza o raciocínio clínico e prescreve o laudo.
# ================================================================

import logging
# ↑ Sistema de registro de eventos (log) para auditoria técnica

import traceback
# ↑ Serve para: Rastrear a origem exata de um erro no código

from django.shortcuts import render, redirect
# ↑ render() → Gera a página HTML final combinando código e dados
# ↑ redirect() → Encaminha o usuário para outra página (outra sala)

from django.http import HttpResponse
# ↑ Resposta básica de texto (sem usar template HTML)

from .forms import DadosClinicosForm
# ↑ Importa o "formulário de entrada" (ficha de admissão)

from .models import Avaliacao
# ↑ Importa o "modelo de prontuário" (tabela do banco de dados)

logger = logging.getLogger(__name__)
# ↑ Inicializa o auditor de eventos para esta ala do sistema



# ================================================================
# index — A Sala de Triagem (Página Inicial)
# Por que existe: É a porta de entrada onde o formulário é entregue 
# ao usuário para preenchimento.
# Recebe: request (pedido de acesso)
# Retorna: A página index.html com o formulário em branco
# O que ver na tela: O formulário com campos de dor, temperatura, etc.
# ================================================================
def index(request):
    """Exibe o formulario de dados clinicos."""
    form = DadosClinicosForm()
    # ↑ Cria uma instância vazia da "ficha de admissão"
    
    return render(request, 'diagnostico/index.html', {
        'form': form,
    })
    # ↑ Envia a ficha para ser desenhada na tela pelo template index.html



# ================================================================
# avaliar — O Centro de Diagnóstico (Processamento)
# Técnico: A "view" é uma função de controle. Ela recebe as informações que 
# o usuário digitou no navegador, confere se está tudo certo, faz cálculos 
# ou chama a IA, e por fim decide qual tela mostrar em seguida.
# Clínico: É a junta médica analisando os exames laboratoriais. Recebe 
# os dados preenchidos, valida se estão corretos e chama os especialistas (IA e Alvarado).
# Recebe: request.POST (os dados submetidos pelo formulário)
# Retorna: HttpResponse via renderização de template com os dicionários de contexto populados.
# ================================================================
def avaliar(request):
    """
    Valida formulario, calcula Alvarado e KNN,
    persiste no banco e exibe resultado.
    """
    if request.method != 'POST':
        # ↑ Técnico: Confere se o usuário chegou aqui clicando no botão "Enviar" do formulário (método POST).
        return redirect('diagnostico:index')

    form = DadosClinicosForm(request.POST)
    # ↑ Técnico: Pega todos os textos preenchidos na tela e entrega para o verificador de erros (o Formulário).
    
    if not form.is_valid():
        # ↑ Técnico: Aciona a verificação automática do Django para ver se o paciente digitou letras onde deveria ser número, por exemplo.
        # ↑ Clínico: Verificar se o paciente preencheu a ficha corretamente ou deixou algo em branco.
        return render(request, 'diagnostico/index.html', {'form': form})

    dados = form.cleaned_data
    # ↑ Técnico: Devolve um dicionário organizado apenas com dados seguros e já convertidos (ex: o texto "37.5" já virou o número 37.5).

    # --- Cálculo do Alvarado Score (Protocolo Clínico Clássico) ---
    from ml.alvarado import calcular_alvarado
    try:
        resultado_alvarado = calcular_alvarado(dados)
        # ↑ Executa o cálculo baseado em pontuação fixa (0 a 10)
        # ↑ É o método tradicional usado por médicos há décadas
    except Exception as e:
        logger.error(f"Erro no Alvarado: {traceback.format_exc()}")
        return render(request, 'diagnostico/erro.html', {
            'erro': 'Erro ao calcular Alvarado Score',
            'detalhe': str(e),
        })


    # --- Diagnóstico por Inteligência Artificial: KNN ---
    # Analogia: O "Médico Experiente" que busca casos semelhantes no passado.
    resultado_knn = None
    try:
        from ml.knn_engine import predizer
        import os
        from django.conf import settings

        modelo_path = os.path.join(
            settings.BASE_DIR, 'ml', 'modelos', 'knn_model.joblib'
        )
        if os.path.exists(modelo_path):
            # Mapear campos do formulario para as variáveis que a IA entende
            dados_knn = {
                'Migratory_Pain': int(dados.get('dor_migratoria', False)),
                'Loss_of_Appetite': int(dados.get('anorexia', False)),
                'Nausea': int(dados.get('nauseas_vomitos', False)),
                'Lower_Right_Abd_Pain': int(dados.get('dor_fid', False)),
                'Contralateral_Rebound_Tenderness': int(
                    dados.get('descompressao_dolorosa', False)),
                'Body_Temperature': float(dados['temperatura']),
                
                # CONVERSÃO CRÍTICA DE UNIDADE: 
                # Técnico: Se o usuário digitar 15000 leucócitos, precisamos dividir por 1000 
                # porque a IA foi ensinada usando valores como "15.0".
                # Clínico: O médico digita 15.000 (mm³), mas a IA foi treinada com 15.0. 
                # Sem a conversão, a predição colapsa.
                'WBC_Count': float(dados['leucocitos']) / 1000.0,
                
                'Neutrophilia': int(dados.get('neutrofilia', False)),
            }

            resultado_knn = predizer(dados_knn, modelo_path)
            # ↑ Técnico: Envia os dados arrumados para o motor KNN fazer o cálculo final.
            # ↑ Clínico: O algoritmo KNN compara este paciente com 1000+ casos reais de Regensburg.
            
            if resultado_knn and 'erro' in resultado_knn:
                logger.warning(f"KNN retornou erro: {resultado_knn['erro']}")
                resultado_knn = None
    except Exception as e:
        logger.warning(f"KNN indisponivel: {e}")
        resultado_knn = None


    # --- Diagnóstico por Inteligência Artificial: SVM ---
    # Analogia: O "Cirurgião Preciso" que desenha uma linha clara entre saúde e doença.
    resultado_svm = None
    try:
        from ml.svm_engine import predizer as predizer_svm
        import os
        from django.conf import settings

        svm_modelo_path = os.path.join(
            settings.BASE_DIR, 'ml', 'modelos', 'svm_model.joblib'
        )
        if os.path.exists(svm_modelo_path):
            # Reutilizar o mesmo mapeamento de dados do KNN
            dados_svm = {
                'Migratory_Pain': int(dados.get('dor_migratoria', False)),
                'Loss_of_Appetite': int(dados.get('anorexia', False)),
                'Nausea': int(dados.get('nauseas_vomitos', False)),
                'Lower_Right_Abd_Pain': int(dados.get('dor_fid', False)),
                'Contralateral_Rebound_Tenderness': int(
                    dados.get('descompressao_dolorosa', False)),
                'Body_Temperature': float(dados['temperatura']),
                'WBC_Count': float(dados['leucocitos']) / 1000.0,
                'Neutrophilia': int(dados.get('neutrofilia', False)),
            }

            resultado_svm = predizer_svm(dados_svm, svm_modelo_path)
            # ↑ O algoritmo SVM busca o hiperplano (fronteira) ideal de separação
            
            if resultado_svm and 'erro' in resultado_svm:
                logger.warning(f"SVM retornou erro: {resultado_svm['erro']}")
                resultado_svm = None
    except Exception as e:
        logger.warning(f"SVM indisponivel: {e}")
        resultado_svm = None


    # --- Persistência no Banco de Dados (Prontuário Eletrônico) ---
    # Por que existe: Para que as avaliações não se percam quando o médico sai da sala.
    try:
        avaliacao = Avaliacao.objects.create(
            # ↑ .objects.create() = Comando do Django para INSERT no SQL
            # ↑ Equivalente SQL: INSERT INTO diagnostico_avaliacao (campos...) VALUES (valores...)
            dor_migratoria=dados.get('dor_migratoria', False),
            anorexia=dados.get('anorexia', False),
            nauseas_vomitos=dados.get('nauseas_vomitos', False),
            dor_fid=dados.get('dor_fid', False),
            descompressao_dolorosa=dados.get('descompressao_dolorosa', False),
            temperatura=dados['temperatura'],
            leucocitos=dados['leucocitos'],
            neutrofilia=dados.get('neutrofilia', False),
            score_alvarado=resultado_alvarado['score'],
            classificacao_alvarado=resultado_alvarado['classificacao'],
            predicao_knn=resultado_knn['classe_predita'] if resultado_knn else None,
            probabilidade_knn=resultado_knn['probabilidade_apendicite'] if resultado_knn else None,
            confianca_knn=resultado_knn.get('confianca', '') if resultado_knn else '',
            predicao_svm=resultado_svm['classe_predita'] if resultado_svm else None,
            probabilidade_svm=resultado_svm['probabilidade_apendicite'] if resultado_svm else None,
            confianca_svm=resultado_svm.get('confianca', '') if resultado_svm else '',
        )
    except Exception as e:
        logger.error(f"Erro ao salvar avaliacao: {e}")
        avaliacao = None

    return render(request, 'diagnostico/resultado.html', {
        'alvarado': resultado_alvarado,
        'knn': resultado_knn,
        'svm': resultado_svm,
        'avaliacao': avaliacao,
        'dados': dados,
    })
    # ↑ Renderiza o "Laudo Final" (resultado.html) com todos os pareceres



# ================================================================
# avaliacao_modelo — Auditoria de Desempenho
# Por que existe: Para que o aluno veja a precisão real da IA.
# Analogia médica: É como a Comissão de Ética e Qualidade do Hospital,
# que analisa a taxa de acerto de cada diagnóstico feito pelos residentes.
# ================================================================
def avaliacao_modelo(request):
    """Exibe metricas pre-calculadas dos modelos KNN e SVM."""
    from ml.pedagogico import carregar_metricas_modelo
    import joblib
    import os
    from django.conf import settings

    metricas = carregar_metricas_modelo()
    # ↑ Carrega os dados pedagógicos (textos explicativos)


    # Carregar metricas do SVM para comparação
    metricas_svm = {}
    svm_path = os.path.join(settings.BASE_DIR, 'ml', 'modelos', 'svm_model.joblib')
    if os.path.exists(svm_path):
        try:
            dados_svm = joblib.load(svm_path)
            metricas_svm = {
                'kernel': dados_svm.get('kernel', 'linear'),
                'C': dados_svm.get('C', 10.0),
                'acuracia_teste': dados_svm.get('acuracia_teste', 0),
                'acuracia_teste_pct': f"{dados_svm.get('acuracia_teste', 0):.1%}",
                'acuracia_treino': dados_svm.get('acuracia_treino', 0),
                'acuracia_treino_pct': f"{dados_svm.get('acuracia_treino', 0):.1%}",
            }
        except Exception:
            pass

    # Computar métricas comparativas a partir das matrizes de confusão
    # Para KNN: usar os dados do modelo treinado
    metricas_knn_sens = ""
    metricas_knn_espec = ""
    metricas_knn_vpp = ""
    metricas_knn_vpn = ""
    metricas_svm_sens = ""
    metricas_svm_espec = ""
    metricas_svm_vpp = ""
    metricas_svm_vpn = ""

    try:
        from ml.preprocessamento import carregar_e_processar
        from ml.avaliador import avaliar_modelo as _avaliar
        import numpy as np

        raw_path = os.path.join(settings.BASE_DIR, 'data', 'regensburg_raw.csv')
        knn_path = os.path.join(settings.BASE_DIR, 'ml', 'modelos', 'knn_model.joblib')

        if os.path.exists(raw_path) and os.path.exists(knn_path) and os.path.exists(svm_path):
            dados = carregar_e_processar(raw_path, config="F")
            y_real = dados['y_test']

            # KNN metrics
            dados_knn = joblib.load(knn_path)
            y_pred_knn = dados_knn['modelo'].predict(dados['X_test'])
            m_knn = _avaliar(y_real, y_pred_knn)
            metricas_knn_sens = f"{m_knn['sensibilidade']:.1%}"
            metricas_knn_espec = f"{m_knn['especificidade']:.1%}"
            metricas_knn_vpp = f"{m_knn['vpp']:.1%}"
            metricas_knn_vpn = f"{m_knn['vpn']:.1%}"

            # SVM metrics
            dados_svm_model = joblib.load(svm_path)
            y_pred_svm = dados_svm_model['modelo'].predict(dados['X_test'])
            m_svm = _avaliar(y_real, y_pred_svm)
            metricas_svm_sens = f"{m_svm['sensibilidade']:.1%}"
            metricas_svm_espec = f"{m_svm['especificidade']:.1%}"
            metricas_svm_vpp = f"{m_svm['vpp']:.1%}"
            metricas_svm_vpn = f"{m_svm['vpn']:.1%}"
    except Exception as e:
        logger.warning(f"Erro ao computar metricas comparativas: {e}")

    # Carregar dados das curvas ROC/PR do metricas.json
    curvas_roc_pr = {}
    try:
        import json
        metricas_json_path = os.path.join(settings.BASE_DIR, 'ml', 'modelos', 'metricas.json')
        if os.path.exists(metricas_json_path):
            with open(metricas_json_path, 'r', encoding='utf-8') as f:
                metricas_json = json.load(f)
            curvas_roc_pr = metricas_json.get('curvas_roc_pr', {})
    except Exception as e:
        logger.warning(f"Erro ao carregar curvas ROC/PR: {e}")

    return render(request, 'diagnostico/avaliacao.html', {
        'metricas': metricas,
        'metricas_svm': metricas_svm,
        'metricas_knn_sens': metricas_knn_sens,
        'metricas_knn_espec': metricas_knn_espec,
        'metricas_knn_vpp': metricas_knn_vpp,
        'metricas_knn_vpn': metricas_knn_vpn,
        'metricas_svm_sens': metricas_svm_sens,
        'metricas_svm_espec': metricas_svm_espec,
        'metricas_svm_vpp': metricas_svm_vpp,
        'metricas_svm_vpn': metricas_svm_vpn,
        'curvas_roc_pr': curvas_roc_pr,
    })


# ================================================================
# como_funciona — A Aula Teórica
# Por que existe: Explica o que é o Alvarado e como a IA funciona.
# Analogia médica: É como a biblioteca ou sala de aula do hospital
# onde os estagiários aprendem os protocolos.
# ================================================================
def como_funciona(request):
    """Exibe pagina pedagogica 'Como Funciona'."""
    from ml.pedagogico import obter_conteudo_como_funciona
    conteudo = obter_conteudo_como_funciona()

    return render(request, 'diagnostico/como_funciona.html', {
        'conteudo': conteudo,
    })



# ================================================================
# documentacao — O Manual Científico
# Por que existe: Referências acadêmicas e bibliografia do projeto.
# ================================================================
def documentacao(request):
    """Exibe documentacao completa do sistema."""
    from ml.pedagogico import obter_conteudo_documentacao
    conteudo = obter_conteudo_documentacao()

    return render(request, 'diagnostico/documentacao.html', {
        'conteudo': conteudo,
    })



# ================================================================
# historico — O Arquivo de Prontuários
# Por que existe: Para consultar avaliações passadas.
# Analogia médica: É a sala de SAME (Serviço de Arquivo Médico).
# ================================================================
def historico(request):
    """Lista ultimas 20 avaliacoes do banco."""
    avaliacoes = Avaliacao.objects.all()[:20]
    # ↑ objects.all()[:20] = Busca os 20 registros mais recentes (via ordering no models)
    # ↑ Equivalente SQL: SELECT * FROM diagnostico_avaliacao LIMIT 20
    
    return render(request, 'diagnostico/historico.html', {
        'avaliacoes': avaliacoes,
    })



# ================================================================
# inicializacao — O Painel de Controle do Lançamento
# Por que existe: Mostra o log técnico da inicialização do sistema.
# Analogia médica: É o monitor de sinais vitais que mostra se o 
# hospital está pronto para abrir as portas.
# ================================================================
def inicializacao(request):
    """Exibe a tela de inicialização com o log do lançador."""
    import os
    from django.conf import settings

    log_path = os.path.join(settings.BASE_DIR, 'launcher_log.txt')
    log_entries = []
    has_error = False

    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                # ↑ Lê o arquivo de log gerado pelo PowerShell (launcher.ps1)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    css = ''
                    if '[OK]' in line:
                        css = 'ok'
                    elif '[!!]' in line:
                        css = 'warn'
                    elif '[ERRO]' in line:
                        css = 'err'
                        has_error = True
                    elif '>>>' in line:
                        css = 'step'
                    log_entries.append({'texto': line, 'css': css})
        except Exception:
            log_entries.append({
                'texto': 'Erro ao ler o log de inicialização.',
                'css': 'err',
            })
            has_error = True
    else:
        log_entries.append({
            'texto': 'Log de inicialização não encontrado. Execute o sistema pelo atalho do Desktop.',
            'css': 'warn',
        })

    status_class = 'warning' if has_error else 'success'
    status_msg = (
        'Sistema iniciado com avisos. Verifique o log.'
        if has_error
        else 'Sistema iniciado com sucesso!'
    )

    return render(request, 'diagnostico/inicializacao.html', {
        'log_entries': log_entries,
        'status_class': status_class,
        'status_msg': status_msg,
    })

