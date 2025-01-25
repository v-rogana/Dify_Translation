import os
import re

def split_text_into_chunks(txt_path, output_folder, min_words=300, max_words=600):
    # Lê o conteúdo do arquivo de texto
    with open(txt_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Normaliza as quebras de linha e remove múltiplas linhas em branco consecutivas
    content = re.sub(r'\n\s*\n+', '\n\n', content)

    # Divide o texto em parágrafos com base em linhas em branco
    paragraphs = content.split('\n\n')

    # Remove espaços extras dos parágrafos
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks = []
    current_chunk = []
    current_word_count = 0

    # Agrupa parágrafos em chunks
    for paragraph in paragraphs:
        word_count = len(paragraph.split())

        if current_word_count + word_count <= max_words:
            current_chunk.append(paragraph)
            current_word_count += word_count
        else:
            if current_word_count >= min_words:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [paragraph]
                current_word_count = word_count
            else:
                current_chunk.append(paragraph)
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_word_count = 0

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    # Garante que a pasta de saída existe
    os.makedirs(output_folder, exist_ok=True)

    # Salva os chunks em arquivos separados
    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(output_folder, f'chunk_{i+1}.txt')
        with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
            chunk_file.write(chunk)

    print(f"Texto dividido em {len(chunks)} chunks e salvo em {output_folder}")

if __name__ == "__main__":
    txt_path = os.path.join(os.path.dirname(__file__), "..", "data", "input", "Principles_of_Psicology.txt")
    output_folder = os.path.join(os.path.dirname(__file__), "..", "data", "output", "chunks")

    split_text_into_chunks(txt_path, output_folder)
