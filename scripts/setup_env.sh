#!/bin/bash
# Aborta se qualquer comando falhar
set -e

# Diretório base (assume que o script está no diretório scripts/)
BASE_DIR=$(dirname "$(realpath "$0")")
PROJECT_DIR=$(realpath "$BASE_DIR/..")

# Criar ambiente virtual, se ainda não existir
if [ ! -d "$PROJECT_DIR/venv" ]; then
  echo "Criando ambiente virtual..."
  /c/Users/victo/AppData/Local/Programs/Python/Python313/python.exe -m venv "$PROJECT_DIR/venv"
else
  echo "Ambiente virtual já existe."
fi

# Ativar ambiente virtual (ajuste para Windows)
if [[ "$OSTYPE" == "msys" ]]; then
  source "$PROJECT_DIR/venv/Scripts/activate"
else
  source "$PROJECT_DIR/venv/bin/activate"
fi

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r "$PROJECT_DIR/requirements.txt"

# Configurar pastas de dados
DATA_DIR="$PROJECT_DIR/data"
INPUT_DIR="$DATA_DIR/input"
# Agora a pasta de output ficará diretamente na raiz do projeto
OUTPUT_DIR="$DATA_DIR/output"

mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

echo "Setup completo! Estrutura do projeto configurada em:"
echo "- Input: $INPUT_DIR"
echo "- Output: $OUTPUT_DIR"
