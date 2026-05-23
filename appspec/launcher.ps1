# ============================================================
#  launcher.ps1 -- Lancador a Prova de Falhas do APPSPEC
#  Executa TUDO que for necessario para abrir o sistema
#  e mostra feedback didatico ao usuario em tela dedicada.
# ============================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

# --- Paths ---
# launcher.ps1 esta dentro de appspec/, entao PSScriptRoot = appspec dir
$SCRIPT_DIR = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$APPSPEC_DIR   = $SCRIPT_DIR
$PROJECT_ROOT  = Split-Path -Parent $APPSPEC_DIR
# Fallback: se .venv nao esta no parent, tenta o parent do parent
if (-not (Test-Path "$PROJECT_ROOT\.venv")) {
    $altRoot = Split-Path -Parent $PROJECT_ROOT
    if (Test-Path "$altRoot\.venv") { $PROJECT_ROOT = $altRoot }
}
$VENV_PYTHON   = Join-Path $PROJECT_ROOT ".venv\Scripts\python.exe"
$MANAGE_PY     = Join-Path $APPSPEC_DIR  "manage.py"
$SETUP_PY      = Join-Path $APPSPEC_DIR  "setup.py"
$LOG_FILE      = Join-Path $APPSPEC_DIR  "launcher_log.txt"
$PORT          = 8000
$URL           = "http://localhost:$PORT"

# --- Log helpers ---
$logEntries = [System.Collections.ArrayList]::new()

function Log($icon, $msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "[$ts] $icon $msg"
    Write-Host $line
    [void]$logEntries.Add($line)
}

function Log-OK($msg)    { Log "[OK]" $msg }
function Log-WARN($msg)  { Log "[!!]" $msg }
function Log-ERR($msg)   { Log "[ERRO]" $msg }
function Log-STEP($msg)  { Log ">>>" $msg }

# ============================================================
#  STEP 1: Verificar estrutura do projeto
# ============================================================
Log-STEP "Verificando estrutura do projeto APPSPEC..."

if (-not (Test-Path $APPSPEC_DIR)) {
    Log-ERR "Diretorio appspec nao encontrado em: $APPSPEC_DIR"
    Log-ERR "Verifique se o atalho aponta para o local correto."
    pause; exit 1
}
Log-OK "Diretorio do projeto encontrado: $PROJECT_ROOT"

# ============================================================
#  STEP 2: Verificar ambiente virtual
# ============================================================
Log-STEP "Verificando ambiente virtual Python (.venv)..."

if (-not (Test-Path $VENV_PYTHON)) {
    Log-WARN "Ambiente virtual nao encontrado. Criando .venv..."
    try {
        & python -m venv (Join-Path $PROJECT_ROOT ".venv")
        Log-OK "Ambiente virtual criado com sucesso."
    } catch {
        Log-ERR "Falha ao criar ambiente virtual: $_"
        pause; exit 1
    }
}

$pyVersion = & $VENV_PYTHON --version 2>&1
Log-OK "Ambiente virtual ativo: $pyVersion"

# ============================================================
#  STEP 3: Verificar dependencias (pip)
# ============================================================
Log-STEP "Verificando dependencias do projeto..."

$reqFile = Join-Path $APPSPEC_DIR "requirements.txt"
if (Test-Path $reqFile) {
    $pipCheck = & $VENV_PYTHON -m pip check 2>&1
    $missingDeps = & $VENV_PYTHON -c "
import sys
deps = ['sklearn','pandas','django','joblib','numpy','matplotlib','seaborn']
missing = []
for d in deps:
    try: __import__(d)
    except ImportError: missing.append(d)
print(','.join(missing) if missing else 'OK')
" 2>&1

    if ($missingDeps -ne "OK" -and $missingDeps -ne "") {
        Log-WARN "Dependencias faltando: $missingDeps"
        Log-STEP "Instalando dependencias automaticamente..."
        & $VENV_PYTHON -m pip install -r $reqFile --quiet 2>&1 | Out-Null
        Log-OK "Dependencias instaladas."
    } else {
        Log-OK "Todas as dependencias estao instaladas."
    }
} else {
    Log-WARN "requirements.txt nao encontrado -- pulando verificacao."
}

# ============================================================
#  STEP 4: Verificar se setup.py ja foi executado
# ============================================================
Log-STEP "Verificando se o modelo ML ja foi treinado..."

$modelPath = Join-Path $APPSPEC_DIR "ml\modelos\knn_model.joblib"
if (-not (Test-Path $modelPath)) {
    Log-WARN "Modelo KNN nao encontrado. Executando setup.py (primeira vez)..."
    Log-STEP "Isso pode levar alguns segundos. Aguarde..."
    Push-Location $APPSPEC_DIR
    & $VENV_PYTHON $SETUP_PY 2>&1 | ForEach-Object { Write-Host "  $_" }
    Pop-Location
    if (Test-Path $modelPath) {
        Log-OK "Setup concluido -- modelo treinado com sucesso!"
    } else {
        Log-ERR "Setup falhou -- modelo nao foi gerado."
        pause; exit 1
    }
} else {
    Log-OK "Modelo KNN ja treinado (ml/modelos/knn_model.joblib)"
}

# ============================================================
#  STEP 5: Liberar porta 8000
# ============================================================
Log-STEP "Verificando porta $PORT..."

$portInUse = netstat -ano 2>$null | Select-String "LISTENING" | Select-String ":$PORT "
if ($portInUse) {
    Log-WARN "Porta $PORT ocupada. Liberando..."
    $pids = $portInUse | ForEach-Object {
        ($_ -replace '\s+', ' ').Trim().Split(' ')[-1]
    } | Sort-Object -Unique
    foreach ($procId in $pids) {
        if ($procId -match '^\d+$' -and [int]$procId -gt 0) {
            try {
                Stop-Process -Id ([int]$procId) -Force -ErrorAction SilentlyContinue
                Log-OK "Processo antigo (PID $procId) encerrado."
            } catch {
                Log-WARN "Nao foi possivel encerrar PID $procId (pode ja ter saido)."
            }
        }
    }
    Start-Sleep -Seconds 1
} else {
    Log-OK "Porta $PORT disponivel."
}

# ============================================================
#  STEP 6: Migracoes Django
# ============================================================
$dbPath = Join-Path $APPSPEC_DIR "db.sqlite3"
if (-not (Test-Path $dbPath)) {
    Log-STEP "Criando banco de dados Django (primeira execucao)..."
    Push-Location $APPSPEC_DIR
    $migrateOut = & $VENV_PYTHON $MANAGE_PY migrate --run-syncdb 2>&1
    Pop-Location
    Log-OK "Banco de dados Django criado."
} else {
    Log-OK "Banco de dados Django ja existe."
}

# ============================================================
#  STEP 7: Iniciar servidor Django
# ============================================================
Log-STEP "Iniciando servidor Django em $URL..."

$serverJob = Start-Process -FilePath $VENV_PYTHON `
    -ArgumentList "$MANAGE_PY runserver $PORT --noreload" `
    -WorkingDirectory $APPSPEC_DIR `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 2

# Verificar se o servidor subiu (rapido: 8 tentativas x 0.5s = 4s max)
$serverOK = $false
for ($i = 0; $i -lt 8; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri $URL -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            $serverOK = $true
            break
        }
    } catch { Start-Sleep -Milliseconds 500 }
}

if ($serverOK) {
    Log-OK "Servidor Django iniciado com sucesso! (PID: $($serverJob.Id))"
} else {
    # Servidor ainda nao respondeu, tentar mais uma vez com mais tempo
    Start-Sleep -Seconds 2
    try {
        Invoke-WebRequest -Uri $URL -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop | Out-Null
        $serverOK = $true
        Log-OK "Servidor Django iniciado! (PID: $($serverJob.Id))"
    } catch {
        Log-WARN "Servidor ainda iniciando... abrindo navegador mesmo assim."
    }
}

# ============================================================
#  STEP 8: Gerar splash screen e abrir navegador
# ============================================================
# Salvar log para que a view Django possa ler
Set-Content -Path $LOG_FILE -Value ($logEntries -join "`n") -Encoding UTF8

# Abrir a tela de inicializacao no navegador padrao
$initUrl = "$URL/inicializacao/"
Start-Process $initUrl
Log-OK "Tela de inicializacao aberta no navegador."
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  APPSPEC esta rodando em: $URL" -ForegroundColor Green
Write-Host "  A tela de inicializacao foi aberta no navegador." -ForegroundColor Yellow
Write-Host "  Clique em 'Entrar no Sistema APPSPEC' para acessar." -ForegroundColor Yellow
Write-Host "  Feche esta janela para encerrar o servidor." -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Manter janela aberta para que o servidor continue
Write-Host "Pressione Ctrl+C ou feche esta janela para encerrar o servidor." -ForegroundColor DarkGray
try {
    Wait-Process -Id $serverJob.Id -ErrorAction Stop
} catch {
    Write-Host "Servidor encerrado." -ForegroundColor Yellow
}

