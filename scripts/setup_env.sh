# Abortar se houver erro
Set-StrictMode -Version Latest

# Diretório base (assume que o script está no diretório scripts/)
$BASE_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PROJECT_DIR = Join-Path $BASE_DIR ".."

# Criar ambiente virtual
$VENV_DIR = Join-Path $PROJECT_DIR "venv"
if (-Not (Test-Path $VENV_DIR)) {
    Write-Host "Criando ambiente virtual..."
    python -m venv $VENV_DIR
} else {
    Write-Host "Ambiente virtual já existe."
}

# Ativar o ambiente virtual
$ACTIVATE_SCRIPT = Join-Path $VENV_DIR "Scripts\Activate.ps1"
if (-Not (Test-Path $ACTIVATE_SCRIPT)) {
    Write-Error "Erro: Não foi possível localizar o script de ativação do ambiente virtual."
    Exit 1
}

Write-Host "Ativando o ambiente virtual..."
& $ACTIVATE_SCRIPT

# Atualizar pip
Write-Host "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
Write-Host "Instalando dependências do requirements.txt..."
$REQUIREMENTS_FILE = Join-Path $PROJECT_DIR "requirements.txt"
pip install -r $REQUIREMENTS_FILE

# Configurar pastas de dados
Write-Host "Criando pastas de dados..."
$DATA_DIR = Join-Path $PROJECT_DIR "data"
$INPUT_DIR = Join-Path $DATA_DIR "input"
$OUTPUT_DIR = Join-Path $DATA_DIR "output"
$CHUNKS_DIR = Join-Path $OUTPUT_DIR "chunks"
$TRANSLATED_DIR = Join-Path $OUTPUT_DIR "translated"

New-Item -ItemType Directory -Force -Path $INPUT_DIR, $CHUNKS_DIR, $TRANSLATED_DIR | Out-Null

# Confirmar setup
Write-Host "Setup completo! Estrutura do projeto configurada:"
Write-Host "- Input: $INPUT_DIR"
Write-Host "- Output Chunks: $CHUNKS_DIR"
Write-Host "- Output Translated: $TRANSLATED_DIR"
