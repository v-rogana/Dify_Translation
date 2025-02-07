import os
import subprocess
import sys

def ensure_folder_exists(folder_path):
    """Cria o diretório se ele não existir."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

if __name__ == "__main__":
    # Verifica se os parâmetros foram passados:
    #   1. Nome do arquivo de entrada (TXT) – obrigatório
    #   2. API_KEY_TRADUCAO
    #   3. API_KEY_CORRECAO
    if len(sys.argv) < 4:
        print("Uso: python orquestrador.py <input_filename> <API_KEY_TRADUCAO> <API_KEY_CORRECAO>")
        sys.exit(1)

    input_filename    = sys.argv[1]
    api_key_traducao  = sys.argv[2]
    api_key_correcao  = sys.argv[3]

    # Diretórios base do projeto
    base_dir  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_dir   = os.path.join(base_dir, "src")
    data_dir  = os.path.join(base_dir, "data")
    input_dir = os.path.join(data_dir, "input")

    # Caminho completo do arquivo de entrada (assumindo que esteja em data/input)
    input_file = os.path.join(input_dir, input_filename)

    # Define o nome base (sem extensão) para nomear os diretórios de output
    base_name = os.path.splitext(input_filename)[0]

    # Cria a pasta de output (com subpastas para chunks, traduções e correções)
    output_folder  = os.path.join(data_dir, "output", f"output_{base_name}")
    chunks_dir     = os.path.join(output_folder, "chunks")
    translated_dir = os.path.join(output_folder, "translated")
    corrected_dir  = os.path.join(output_folder, "correcao")

    ensure_folder_exists(chunks_dir)
    ensure_folder_exists(translated_dir)
    ensure_folder_exists(corrected_dir)

    # 1. Divide o arquivo de entrada em chunks
    print("[1/3] Dividindo texto em chunks...")
    subprocess.run([
        "python",
        os.path.join(src_dir, "split_text.py"),
        input_filename,
        chunks_dir
    ])

    # 2. Envia os chunks para a API de tradução
    print("[2/3] Enviando chunks para a API para tradução...")
    subprocess.run([
        "python",
        os.path.join(src_dir, "send_to_api.py"),
        chunks_dir,
        translated_dir,
        api_key_traducao  # Envia a chave de tradução
    ])

    # 3. Executa o processo de correção
    print("[3/3] Realizando correções dos arquivos...")
    subprocess.run([
        "python",
        os.path.join(src_dir, "correction.py"),
        chunks_dir,
        translated_dir,
        corrected_dir,
        api_key_correcao  # Envia a chave de correção
    ])

    print("Processo completo!")
    print("Arquivos corrigidos disponíveis em:", corrected_dir)
