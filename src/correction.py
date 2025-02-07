import os
import time
import requests
import sys

# Verifica se os argumentos foram passados corretamente
if len(sys.argv) < 5:
    print("Uso: python correction.py <chunks_dir> <translated_dir> <corrected_dir> <API_KEY_CORRECAO>")
    sys.exit(1)

chunks_dir     = sys.argv[1]
translated_dir = sys.argv[2]
corrected_dir  = sys.argv[3]
API_KEY        = sys.argv[4]

API_URL = "https://api.dify.ai/v1/workflows/run"
USER_ID = "usuario_qualquer"  # Pode ser qualquer identificador único
WAIT_SECONDS = 60             # 1 minuto de pausa entre requisições

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[ERRO] Não foi possível ler o arquivo: {file_path} -> {e}")
        return None

def run_workflow(input_text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": {
            "input_text": input_text
        },
        "response_mode": "blocking",
        "user": USER_ID
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            output_text = result.get("data", {}).get("outputs", {}).get("text", "")
            return output_text
        else:
            print(f"[ERRO] Falha ao chamar a API. Status code: {response.status_code}")
            print("Detalhes:", response.text)
            return None
    except Exception as e:
        print(f"[ERRO] Exceção ao chamar a API: {e}")
        return None

def save_correction(content, output_filename, corrected_folder):
    ensure_folder_exists(corrected_folder)
    output_path = os.path.join(corrected_folder, output_filename)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[OK] Correção salva em: {output_path}")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar '{output_path}': {e}")

def process_corrections(chunks_folder, translated_folder, corrected_folder):
    ensure_folder_exists(corrected_folder)
    chunk_files = [f for f in os.listdir(chunks_folder) if f.endswith(".txt")]
    chunk_files.sort()  # Ordena os arquivos para processamento sequencial

    if not chunk_files:
        print("Nenhum arquivo .txt encontrado em:", chunks_folder)
        return

    for txt_file in chunk_files:
        nome_base, _ = os.path.splitext(txt_file)
        path_txt = os.path.join(chunks_folder, txt_file)
        # Arquivo traduzido correspondente (ex: chunk1.md)
        md_file = f"{nome_base}.md"
        path_md = os.path.join(translated_folder, md_file)

        if not os.path.isfile(path_md):
            print(f"[AVISO] Não encontrei a tradução para {txt_file} em {translated_folder} ({md_file}). Pulando...")
            continue

        original_content = read_file(path_txt)
        translated_content = read_file(path_md)

        if not original_content or not translated_content:
            print(f"[AVISO] Não foi possível ler um dos arquivos para {txt_file}. Pulando...")
            continue

        combined_text = f"<Original>\n{original_content}\n\n<Tradução>\n{translated_content}\n"

        print(f"[PROCESSO] Enviando '{nome_base}' para correção...")
        response_text = run_workflow(combined_text)

        if response_text:
            corrected_filename = f"{nome_base}_corrigido.md"
            save_correction(response_text, corrected_filename, corrected_folder)
        else:
            print(f"[ERRO] Sem texto de resposta da API para {nome_base}.")

        print(f"[AGUARDE] Pausando {WAIT_SECONDS} segundos antes do próximo chunk...")
        time.sleep(WAIT_SECONDS)

if __name__ == "__main__":
    # Utiliza os diretórios passados via argumento
    chunks_folder     = os.path.abspath(sys.argv[1])
    translated_folder = os.path.abspath(sys.argv[2])
    corrected_folder  = os.path.abspath(sys.argv[3])
    
    process_corrections(chunks_folder, translated_folder, corrected_folder)
