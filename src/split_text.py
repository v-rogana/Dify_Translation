import os
import re
import sys

def split_text_by_word_count(text, min_words=300, max_words=600):
    """
    Divide o texto em chunks com base na contagem de palavras.
    Tenta finalizar o chunk em um ponto de pontuação (".", "!" ou "?")
    se houver entre min_words e max_words palavras; caso contrário, divide
    exatamente no limite de max_words.
    Essa abordagem preserva o contexto e a formatação original.
    """
    # Obtem todas as ocorrências de palavras com suas posições (preservando espaços)
    words_iter = list(re.finditer(r'\S+', text))
    total_words = len(words_iter)
    chunks = []
    start_word_idx = 0

    while start_word_idx < total_words:
        # Calcula o índice de fim ideal (limite máximo de palavras)
        end_idx = min(start_word_idx + max_words, total_words)

        # Se as palavras restantes forem menos que o mínimo, pega tudo
        if total_words - start_word_idx <= min_words:
            chunk = text[words_iter[start_word_idx].start():].strip()
            chunks.append(chunk)
            break

        # Tenta encontrar um ponto de quebra (palavra terminada com . ! ou ?)
        # entre o limite mínimo e o máximo
        break_idx = None
        lower_bound = start_word_idx + min_words
        # Procura do final para o início para achar o ponto de quebra mais próximo do max_words
        for i in range(end_idx, lower_bound - 1, -1):
            token = text[words_iter[i-1].start():words_iter[i-1].end()]
            if token and token[-1] in ".!?":
                break_idx = i
                break
        if break_idx is None:
            break_idx = end_idx

        # Determina o trecho do texto a partir do início da primeira palavra do chunk
        # até o final da última palavra do chunk (ou até o início da próxima, para não cortar parte do espaço)
        chunk_start = words_iter[start_word_idx].start()
        if break_idx < total_words:
            chunk_end = words_iter[break_idx].start()
        else:
            chunk_end = len(text)
        chunk = text[chunk_start:chunk_end].strip()
        chunks.append(chunk)
        start_word_idx = break_idx

    return chunks

def split_text_into_chunks(txt_path, output_folder, min_words=300, max_words=600):
    """
    Lê o arquivo de texto e divide seu conteúdo em chunks utilizando a contagem de palavras,
    tentando preservar pontos de quebra em sinais de pontuação.
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Erro ao abrir o arquivo {txt_path}: {e}")
        sys.exit(1)

    chunks = split_text_by_word_count(content, min_words, max_words)

    try:
        os.makedirs(output_folder, exist_ok=True)
    except Exception as e:
        print(f"Erro ao criar a pasta {output_folder}: {e}")
        sys.exit(1)

    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(output_folder, f"chunk_{i+1}.txt")
        try:
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(chunk)
        except Exception as e:
            print(f"Erro ao salvar o chunk em {chunk_path}: {e}")
            sys.exit(1)

    print(f"Texto dividido em {len(chunks)} chunks e salvo em {output_folder}")

def main():
    if len(sys.argv) != 2:
        print("Uso: python split_text.py \"<caminho_arquivo_entrada>\"")
        sys.exit(1)

    input_path = sys.argv[1]
    # Define a raiz do projeto (pasta acima deste script)
    raiz_projeto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if not os.path.isabs(input_path):
        input_path = os.path.join(raiz_projeto, input_path)

    if not os.path.exists(input_path):
        print(f"Arquivo de entrada não encontrado: {input_path}")
        sys.exit(1)

    nome_arquivo = os.path.basename(input_path)
    nome_base, _ = os.path.splitext(nome_arquivo)
    # Define a pasta de saída padrão: <raiz_projeto>/output/output_{nome_base}/chunks
    output_folder = os.path.join(raiz_projeto,"data", "output", f"output_{nome_base}", "chunks")

    print(f"Arquivo de entrada: {input_path}")
    print(f"Pasta de saída: {output_folder}")

    split_text_into_chunks(input_path, output_folder)

if __name__ == "__main__":
    main()
