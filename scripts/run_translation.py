import os
import subprocess

# Função auxiliar para garantir que pastas existam
def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

if __name__ == "__main__":
    # Diretórios do projeto
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "..", "data")

    input_dir = os.path.join(data_dir, "input")
    chunks_dir = os.path.join(data_dir, "output", "chunks")
    translated_dir = os.path.join(data_dir, "output", "translated")

    # Nome do arquivo de entrada (pode ser alterado facilmente)
    input_filename = "teste.txt"
    input_file = os.path.join(input_dir, input_filename)

    # Nomes dos arquivos unificados com base no nome do arquivo de entrada
    base_name = os.path.splitext(input_filename)[0]
    unified_md = os.path.join(translated_dir, f"unified_{base_name}.md")
    unified_docx = os.path.join(translated_dir, f"unified_{base_name}.docx")

    # Garantir que os diretórios de saída existam
    ensure_folder_exists(chunks_dir)
    ensure_folder_exists(translated_dir)

    # 1. Quebra o texto em chunks
    print("[1/4] Dividindo texto em chunks...")
    subprocess.run(["python3", os.path.join(base_dir, "split_text.py"), input_file, chunks_dir])

    # 2. Envia os chunks para a API para tradução
    print("[2/4] Enviando chunks para a API...")
    subprocess.run(["python3", os.path.join(base_dir, "send_to_api.py"), chunks_dir, translated_dir])

    # 3. Concatena os arquivos traduzidos em um único Markdown
    print("[3/4] Concatenando arquivos traduzidos...")
    subprocess.run(["python3", os.path.join(base_dir, "concat_md.py"), translated_dir, unified_md])

    # 4. Converte o arquivo Markdown unificado para DOCX
    print("[4/4] Convertendo Markdown para DOCX...")
    subprocess.run(["python3", os.path.join(base_dir, "md_to_docx.py"), unified_md, unified_docx])

    print("Processo completo! Arquivo final disponível em:", unified_docx)
