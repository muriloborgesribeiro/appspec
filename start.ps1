# Detecta Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PYTHON_CMD = "python"
}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PYTHON_CMD = "python3"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PYTHON_CMD = "py"
}
else {
    Write-Host "Python não foi encontrado no sistema."
    exit 1
}

Write-Host "Usando interpretador: $PYTHON_CMD"

# Verifica ambiente virtual
if (Test-Path "venv") {
    $VENV_PATH = "venv"
}
elseif (Test-Path ".venv") {
    $VENV_PATH = ".venv"
}
else {
    Write-Host "Ambiente virtual não encontrado. Criando venv..."

    & $PYTHON_CMD -m venv venv

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao criar ambiente virtual"
        exit 1
    }

    $VENV_PATH = "venv"
}

# Script de ativação
$ACTIVATE_SCRIPT = "$VENV_PATH\Scripts\Activate.ps1"

if (!(Test-Path $ACTIVATE_SCRIPT)) {
    Write-Host "Script de ativação não encontrado."
    exit 1
}

# Ativa venv
& $ACTIVATE_SCRIPT

# Atualiza pip
python -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao atualizar pip"
    exit 1
}

# Entra no diretório
Set-Location appspec

# Instala requirements
if (Test-Path "requirements.txt") {
    Write-Host "Instalando dependências..."

    python -m pip install -r requirements.txt

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao instalar dependências"
        exit 1
    }
}

# Executa setup.py
if (Test-Path "setup.py") {
    Write-Host "Executando setup.py..."

    python setup.py

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao executar setup.py"
        exit 1
    }
}

# Migrações
python manage.py migrate

# Runserver
Write-Host "Inicializando Django..."

python manage.py runserver