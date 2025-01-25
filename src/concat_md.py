import os
import re

def merge_markdown_files_with_titles(folder_path, output_file):
    try:
        # Lista todos os arquivos .md na pasta
        files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
        
        if not files:
            print("Nenhum arquivo .md encontrado na pasta.")
            return

        # Ordena os arquivos por número no nome
        files.sort(key=lambda f: int(re.search(r'\d+', f).group()) if re.search(r'\d+', f) else float('inf'))

        # Abre o arquivo de saída para escrita
        with open(output_file, "w", encoding="utf-8") as outfile:
            for file in files:
                file_path = os.path.join(folder_path, file)
                # Usa o nome do arquivo como título (removendo a extensão)
                title = os.path.splitext(file)[0]
                outfile.write(f"# {title}\n\n")  # Adiciona o título no formato Markdown
                
                # Lê o conteúdo de cada arquivo .md
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    # Escreve o conteúdo no arquivo final
                    outfile.write(content + "\n\n")

        print(f"Arquivos combinados com sucesso em: {output_file}")
    except Exception as e:
        print(f"Erro ao combinar os arquivos: {e}")

if __name__ == "__main__":
    input_folder = os.path.join(os.path.dirname(__file__), "..", "data", "output", "translated")
    output_file = os.path.join(input_folder, "unified_output.md")

    merge_markdown_files_with_titles(input_folder, output_file)
