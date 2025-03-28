import re
import os
import PyPDF2
import pytesseract
import logging
from pdf2image import convert_from_path
import argparse

def normalizar_terminadores_linha(texto: str) -> str:
    """
    Normaliza as quebras de linha e, se houver poucas quebras duplas,
    insere novas quebras duplas após sinais de pontuação final seguidos de letra maiúscula.
    """
    # Substitui diferentes quebras de linha por \n
    texto = re.sub(r'(\r\n|\r|\u2028|\u2029)', '\n', texto)
    # Se houver menos de 5 quebras duplas, insere novas quebras após ponto, interrogação ou exclamação
    if texto.count('\n\n') < 5:
        texto = re.sub(r'([.!?])\s+(?=[A-Z])', r'\1\n\n', texto)
    return texto

def extrair_texto_simples(caminho_pdf: str):
    """
    Extrai o texto de cada página do PDF usando PyPDF2.
    Retorna o texto completo, o número de páginas com texto e o total de páginas.
    """
    texto_paginas = []
    paginas_com_texto = 0

    with open(caminho_pdf, 'rb') as arquivo_pdf:
        leitor = PyPDF2.PdfReader(arquivo_pdf)
        total_paginas = len(leitor.pages)
        for idx, pagina in enumerate(leitor.pages):
            t = pagina.extract_text()
            if t and len(t.strip()) > 20:
                paginas_com_texto += 1
                texto_paginas.append(t)
            else:
                texto_paginas.append("")
            percent = ((idx + 1) / total_paginas) * 100
            print(f"Extracao simples: pagina {idx+1} de {total_paginas} processada ({percent:.1f}%)")
    texto_extraido = "\n".join(texto_paginas)
    return texto_extraido, paginas_com_texto, total_paginas

def extrair_texto_com_ocr(caminho_pdf: str, poppler_path: str = None):
    """
    Extrai o texto de cada página do PDF utilizando OCR.
    """
    if poppler_path:
        imagens = convert_from_path(caminho_pdf, dpi=300, poppler_path=poppler_path)
    else:
        imagens = convert_from_path(caminho_pdf, dpi=300)
    
    total_paginas = len(imagens)
    texto_total = []
    for idx, imagem in enumerate(imagens):
        texto = pytesseract.image_to_string(imagem, lang='por')
        texto_total.append(texto)
        percent = ((idx + 1) / total_paginas) * 100
        print(f"OCR: pagina {idx+1} de {total_paginas} processada ({percent:.1f}%)")
    return "\n".join(texto_total)

def extrair_texto_pdf(caminho_pdf: str, threshold: float = 0.5, poppler_path: str = None) -> str:
    print("Iniciando extracao simples com PyPDF2...")
    texto_simples, paginas_com_texto, total_paginas = extrair_texto_simples(caminho_pdf)
    ratio = (paginas_com_texto / total_paginas) if total_paginas > 0 else 0

    if ratio < threshold:
        print(f"\nExtracao simples apresentou apenas {ratio*100:.1f}% de paginas com texto.")
        print("Utilizando OCR para extracao...")
        texto_final = extrair_texto_com_ocr(caminho_pdf, poppler_path=poppler_path)
    else:
        texto_final = texto_simples

    print("Normalizando terminadores de linha...")
    texto_final = normalizar_terminadores_linha(texto_final)
    return texto_final

def salvar_texto_em_arquivo(texto: str, caminho_txt: str):
    """
    Salva o texto extraído em um arquivo TXT.
    """
    with open(caminho_txt, 'w', encoding='utf-8') as arquivo_txt:
        arquivo_txt.write(texto)
    print(f"Arquivo salvo: {caminho_txt}")

def processar_pdf_para_txt(nome_arquivo_pdf: str, threshold: float = 0.5, poppler_path: str = None):
    """
    Processa o PDF para extrair o texto e salvar em um arquivo TXT.
    Os caminhos de entrada e saída são definidos relativos à raiz do projeto.
    """
    raiz_projeto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    pasta_entrada = os.path.join(raiz_projeto, "data", "input", "pdf", "original")
    pasta_saida = os.path.join(raiz_projeto, "data", "input", "pdf", "converted")
    
    # Criar o caminho absoluto do arquivo de entrada
    caminho_pdf = os.path.join(pasta_entrada, nome_arquivo_pdf)
    
    # Gerar o nome do arquivo de saída
    nome_base = os.path.splitext(nome_arquivo_pdf)[0]
    caminho_txt = os.path.join(pasta_saida, f"{nome_base}_convertido.txt")

    # Cria a pasta de saída caso não exista
    os.makedirs(pasta_saida, exist_ok=True)

    print(f"\nProcessando o PDF: {caminho_pdf}")
    texto_extraido = extrair_texto_pdf(caminho_pdf, threshold=threshold, poppler_path=poppler_path)
    salvar_texto_em_arquivo(texto_extraido, caminho_txt)
    return texto_extraido


if __name__ == '__main__':
    # Argumentos de comando
    parser = argparse.ArgumentParser(description="Extrair texto de PDF e salvar em arquivo TXT")
    parser.add_argument('input_pdf', type=str, help="Nome do arquivo PDF de entrada (sem caminho)")
    parser.add_argument('--threshold', type=float, default=0.5,
                        help="Limite de páginas com texto para considerar OCR (default 50%)")
    parser.add_argument('--poppler_path', type=str, default=None,
                        help="Caminho para o Poppler (opcional)")
    
    args = parser.parse_args()
    logging.getLogger("PyPDF2").setLevel(logging.ERROR)
    
    texto_extraido = processar_pdf_para_txt(args.input_pdf,
                                             threshold=args.threshold,
                                             poppler_path=args.poppler_path)
    print("\nProcessamento concluído!")
