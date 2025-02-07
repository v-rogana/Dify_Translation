import time
import requests
import os
import sys

# Verifica se os argumentos foram passados corretamente
if len(sys.argv) < 4:
    print("Uso: python send_to_api.py <chunks_dir> <translated_dir> <API_KEY_TRADUCAO>")
    sys.exit(1)

chunks_dir    = sys.argv[1]
translated_dir = sys.argv[2]
API_KEY       = sys.argv[3]

API_URL = "https://api.dify.ai/v1/workflows/run"
USER_ID = "teste_usuario"  # Pode ser qualquer identificador único

def read_txt_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        print(f"Arquivo '{file_path}' lido com sucesso.")
        return content
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
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
            # Extrai o texto retornado (ajuste conforme o retorno real da API)
            output = result.get("data", {}).get("outputs", {}).get("text", "")
            return output
        else:
            print(f"Erro na execução da API. Status: {response.status_code}")
            print("Mensagem de erro:", response.text)
            return None
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        return None

def save_to_markdown(content, original_file, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.join(output_folder, f"{os.path.splitext(original_file)[0]}.md")
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Arquivo salvo: {filename}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo {filename}: {e}")

def process_files_in_folder(folder_path, output_folder):
    try:
        files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        if not files:
            print("Nenhum arquivo .txt encontrado na pasta.")
            return

        for file in files:
            file_path = os.path.join(folder_path, file)
            input_text = read_txt_file(file_path)
            if input_text:
                result = run_workflow(input_text)
                if result:
                    save_to_markdown(result, file, output_folder)
            # Pausa de 1 minuto entre os arquivos
            time.sleep(60)
    except Exception as e:
        print(f"Erro ao processar os arquivos: {e}")

if __name__ == "__main__":
    # Utiliza os diretórios passados via argumento
    input_folder = os.path.abspath(sys.argv[1])
    output_folder = os.path.abspath(sys.argv[2])
    
    process_files_in_folder(input_folder, output_folder)
