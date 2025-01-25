import time
import requests
import os

# Configuração básica da API
API_KEY = "app-Owkq7rHqT7X4AfTnPlQ5WvEM"
API_URL = "https://api.dify.ai/v1/workflows/run"
USER_ID = "teste_usuario"  # Pode ser qualquer identificador único

# Função para ler o conteúdo de um arquivo .txt
def read_txt_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        print(f"Arquivo '{file_path}' lido com sucesso.")
        return content
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        return None

# Função para executar o workflow
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
            output = result.get("data", {}).get("outputs", {}).get("output", "")
            return output
        else:
            print(f"Erro na execução da API. Status: {response.status_code}")
            print("Mensagem de erro:", response.text)
            return None
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        return None

# Função para salvar o resultado em um arquivo Markdown
def save_to_markdown(content, original_file, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.join(output_folder, f"{os.path.splitext(original_file)[0]}.md")
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Resultado salvo em: {filename}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")

# Loop para processar múltiplos arquivos em intervalos de 3 minutos
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
                if result:  # Apenas salva se houver output
                    save_to_markdown(result, file, output_folder)
            print("Aguardando 2 minutos para processar o próximo arquivo...")
            time.sleep(2 * 60)  # Espera 2 minutos entre os arquivos
    except Exception as e:
        print(f"Erro ao processar os arquivos: {e}")

# Configuração dos caminhos de entrada e saída com base na nova estrutura
if __name__ == "__main__":
    input_folder = os.path.join(os.path.dirname(__file__), "..", "data", "input")
    output_folder = os.path.join(os.path.dirname(__file__), "..", "data", "output")

    # Executa o processamento
    process_files_in_folder(input_folder, output_folder)
