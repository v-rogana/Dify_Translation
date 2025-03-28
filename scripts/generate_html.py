#!/usr/bin/env python3
import os
import re
import sys
import webbrowser

def get_chunk_number(filename):
    """
    Extrai o número do chunk (ex.: '1' de 'chunk_1' ou 'chunk1_corrigido').
    Retorna o número (como string) ou None se não encontrar.
    """
    match = re.search(r"chunk[_-]?(\d+)", filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def read_file(filepath):
    """Lê o arquivo em UTF-8 e retorna seu conteúdo."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
        return ""

def merge_paragraphs(text):
    """
    Une linhas em parágrafos, considerando que uma linha em branco indica a separação.
    Retorna uma lista de parágrafos.
    """
    lines = text.split("\n")
    merged = []
    buffer_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            buffer_lines.append(stripped)
        else:
            if buffer_lines:
                merged.append(" ".join(buffer_lines))
                buffer_lines = []
    if buffer_lines:
        merged.append(" ".join(buffer_lines))
    return merged

def highlight_unknown(text):
    """
    Destaca com fundo vermelho as palavras que contenham o caractere de substituição �.
    """
    return re.sub(r'(\S*�\S*)', r'<span style="background-color: red;">\1</span>', text)

def split_correction_items(text):
    """
    Fallback: Separa o texto de correção em itens enumerados usando números.
    """
    single_line = " ".join(text.split("\n"))
    if not single_line.strip():
        return []
    items = re.split(r'(?=\d+\.\s)', single_line)
    items = [item.strip() for item in items if item.strip()]
    return items

def split_correction_sections(text):
    """
    Separa o texto de correção em seções com base nos marcadores.
    """
    pattern = r"<OBSERVAÇÕES E AJUSTES>(.*?)<VERSÃO CORRIGIDA \(APENAS TRECHOS RELEVANTES\)>(.*)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if m:
        observacoes_raw = m.group(1).strip()
        versao_raw = m.group(2).strip()
        observacoes_items = re.split(r"\n?\d+\.\s", observacoes_raw)
        observacoes_items = [item.strip() for item in observacoes_items if item.strip()]
        versao_items = re.split(r"\n?-+\s*", versao_raw)
        versao_items = [item.strip() for item in versao_items if item.strip()]
        return {"observacoes": observacoes_items, "versao": versao_items}
    else:
        return {"observacoes": split_correction_items(text), "versao": []}

def merge_small_chunks(txt_files, translated_files, corrected_files, min_words=100):
    """
    Lê os arquivos dos chunks originais, traduzidos e corrigidos (se existirem) e
    mescla os chunks cujo texto original seja menor que 'min_words' com o seguinte.
    Retorna uma lista de dicionários com os dados mesclados.
    """
    merged_chunks = []
    keys = sorted(txt_files.keys(), key=lambda x: int(x))
    i = 0
    while i < len(keys):
        key = keys[i]
        orig_text = read_file(txt_files[key])
        trans_text = read_file(translated_files.get(key, ""))
        corr_text = read_file(corrected_files.get(key, ""))
        current_ids = [key]
        current_orig = orig_text
        current_trans = trans_text
        current_corr = corr_text
        word_count = len(current_orig.split())
        # Mescla com o próximo chunk se o atual for muito pequeno
        while word_count < min_words and i + 1 < len(keys):
            i += 1
            next_key = keys[i]
            next_orig = read_file(txt_files[next_key])
            next_trans = read_file(translated_files.get(next_key, ""))
            next_corr = read_file(corrected_files.get(next_key, ""))
            current_ids.append(next_key)
            current_orig += "\n\n" + next_orig
            current_trans += "\n\n" + next_trans
            current_corr += "\n\n" + next_corr
            word_count = len(current_orig.split())
        merged_chunks.append({
            'ids': current_ids,
            'original': current_orig,
            'translated': current_trans,
            'corrected': current_corr,
        })
        i += 1
    return merged_chunks

def main():
    if len(sys.argv) != 2:
        print("Uso: python generate_html.py \"<caminho_da_pasta_output>\"")
        sys.exit(1)
    
    base_output_folder = sys.argv[1]
    if not os.path.isabs(base_output_folder):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        base_output_folder = os.path.join(project_root, base_output_folder)
    
    if not os.path.isdir(base_output_folder):
        print("O caminho informado não existe ou não é um diretório. Verifique e tente novamente.")
        sys.exit(1)
    
    print("Caminho informado:", repr(base_output_folder))
    
    # Define as subpastas (seguindo o padrão usado nos demais scripts)
    txt_folder = os.path.join(base_output_folder, "chunks")
    translated_folder = os.path.join(base_output_folder, "translated")
    corrected_folder = os.path.join(base_output_folder, "correcao")
    
    # Define o nome do HTML final (remove prefixo "output_" se existir)
    folder_name = os.path.basename(base_output_folder)
    suffix = folder_name[7:] if folder_name.lower().startswith("output_") else folder_name
    html_file_name = f"revisao_humana_{suffix}.html"
    html_output_file = os.path.join(base_output_folder, html_file_name)
    
    txt_files = {}
    translated_files = {}
    corrected_files = {}
    
    if os.path.isdir(txt_folder):
        for f in os.listdir(txt_folder):
            if f.lower().endswith(".txt"):
                num = get_chunk_number(f)
                if num:
                    txt_files[num] = os.path.join(txt_folder, f)
    
    if os.path.isdir(translated_folder):
        for f in os.listdir(translated_folder):
            if f.lower().endswith(".md"):
                num = get_chunk_number(f)
                if num:
                    translated_files[num] = os.path.join(translated_folder, f)
    
    if os.path.isdir(corrected_folder):
        for f in os.listdir(corrected_folder):
            if f.lower().endswith(".md"):
                num = get_chunk_number(f)
                if num:
                    corrected_files[num] = os.path.join(corrected_folder, f)
    
    # Mescla chunks pequenos (menores que 100 palavras)
    merged_chunks = merge_small_chunks(txt_files, translated_files, corrected_files, min_words=100)
    
    html_content = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Revisão Final: Correção, Original e Tradução</title>
  <style>
    body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
    .container { width: 90%; max-width: 1200px; margin: 20px auto; background-color: #fff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    .header { text-align: center; margin-bottom: 20px; }
    .header h1 { margin: 0; font-size: 28px; color: #333; }
    .header p { color: #666; font-size: 16px; }
    .instructions { border: 1px solid #ccc; padding: 15px; background-color: #e7f3fe; border-radius: 8px; margin-bottom: 20px; }
    .instructions h2 { margin-top: 0; color: #333; }
    .instructions ul { margin-left: 20px; }
    .chunk-container { border: 1px solid #ddd; margin-bottom: 30px; padding: 15px; border-radius: 8px; background-color: #fafafa; }
    .chunk-header { font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333; }
    .comparison-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
    .comparison-table th, .comparison-table td { border: 1px solid #ccc; padding: 8px; vertical-align: top; }
    .comparison-table th { background-color: #f0f0f0; font-weight: bold; }
    .correction-area { background-color: #fff8e1; border: 1px solid #ffeb3b; border-radius: 4px; padding: 10px; max-height: 250px; overflow-y: auto; margin-bottom: 10px; }
    .correction-area ul { margin: 0; padding-left: 20px; }
    .correction-area li { margin-bottom: 5px; }
    .final-text { margin-top: 10px; }
    .final-text textarea { width: 100%; min-height: 150px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; resize: vertical; }
    .chunk-buttons { margin-top: 10px; }
    .chunk-buttons button { margin-right: 10px; padding: 8px 12px; background-color: #4285f4; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
    .chunk-buttons button:hover { background-color: #3367d6; }
    .export-button { display: block; width: 100%; padding: 12px; background-color: #4CAF50; color: #fff; border: none; border-radius: 4px; font-size: 18px; cursor: pointer; margin-top: 20px; }
    .export-button:hover { background-color: #45a049; }
  </style>
  <script>
    function copyTranslation(chunkId) {
      var transCells = document.querySelectorAll("#chunk_" + chunkId + " .translation-paragraph");
      var text = "";
      for (var i = 0; i < transCells.length; i++) {
        text += transCells[i].innerText.trim() + "\\n\\n";
      }
      var finalTextArea = document.getElementById("final_" + chunkId);
      if (finalTextArea) { finalTextArea.value = text.trim(); }
    }
    function exportAllFinalText() {
      var finalTextAreas = document.querySelectorAll(".final-text textarea");
      var combinedText = "";
      for (var i = 0; i < finalTextAreas.length; i++) {
        var idParts = finalTextAreas[i].id.split("_");
        var chunkNum = idParts[1];
        combinedText += "Chunk " + chunkNum + ":\\n" + finalTextAreas[i].value.trim() + "\\n\\n";
      }
      if (!combinedText) { alert("Nenhum texto final foi inserido."); return; }
      var blob = new Blob([combinedText], {type: "text/plain;charset=utf-8"});
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = "texto_final_unificado.txt";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  </script>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Revisão Final: Correção, Original e Tradução</h1>
      <p>Revise os textos, analise as correções sugeridas e edite o texto final de cada chunk. Ao concluir, clique em "Exportar Texto Final Unificado" para baixar o documento completo.</p>
    </div>
    <div class="instructions">
      <h2>Instruções para Revisão</h2>
      <p>Bem-vindo à ferramenta de revisão do Dify Translator. Aqui você deve:</p>
      <ul>
        <li>Analisar o trecho traduzido comparado ao original.</li>
        <li>Utilizar as correções sugeridas como guia, mas lembre-se: <strong>não leve a correção tão a sério</strong> – a correção humana e o seu julgamento prevalecem.</li>
        <li>Clicar no botão "Copiar Tradução para Texto Final" para copiar a tradução completa para o campo de edição abaixo.</li>
        <li>Editar o texto final conforme o seu critério, adaptando as sugestões quando necessário.</li>
      </ul>
      <p>Após revisar cada chunk, edite o texto final no campo indicado e, quando terminar, utilize o botão de exportação para baixar o texto unificado.</p>
    </div>
"""
    # Geração do HTML para cada merged chunk
    for chunk in merged_chunks:
        if len(chunk['ids']) == 1:
            header_label = f"Chunk {chunk['ids'][0]}"
            chunk_id = chunk['ids'][0]
        else:
            header_label = f"Chunks {chunk['ids'][0]} - {chunk['ids'][-1]}"
            chunk_id = f"{chunk['ids'][0]}-{chunk['ids'][-1]}"
        
        orig_paragraphs = merge_paragraphs(chunk['original'])
        # Destaca palavras com caractere desconhecido na coluna Original
        orig_paragraphs = [highlight_unknown(p) for p in orig_paragraphs]
        trans_paragraphs = merge_paragraphs(chunk['translated'])
        
        max_rows = max(len(orig_paragraphs), len(trans_paragraphs))
        orig_paragraphs += [""] * (max_rows - len(orig_paragraphs))
        trans_paragraphs += [""] * (max_rows - len(trans_paragraphs))
        
        table_rows = ""
        for i in range(max_rows):
            table_rows += f"<tr><td>{orig_paragraphs[i]}</td><td class='translation-paragraph'>{trans_paragraphs[i]}</td></tr>"
        
        if chunk['corrected'].strip():
            sections = split_correction_sections(chunk['corrected'])
            correction_html = ""
            if sections["observacoes"]:
                correction_html += "<strong>OBSERVAÇÕES E AJUSTES</strong><ul>"
                for item in sections["observacoes"]:
                    correction_html += f"<li>{item}</li>"
                correction_html += "</ul>"
            if sections["versao"]:
                correction_html += "<strong>VERSÃO CORRIGIDA (APENAS TRECHOS RELEVANTES)</strong><ul>"
                for item in sections["versao"]:
                    correction_html += f"<li>{item}</li>"
                correction_html += "</ul>"
            if not correction_html:
                correction_html = "Nenhuma correção registrada."
        else:
            correction_html = "Nenhuma correção registrada."
        
        html_content += f"""
    <div class="chunk-container" id="chunk_{chunk_id}">
      <div class="chunk-header">{header_label}</div>
      <table class="comparison-table">
        <tr>
          <th>Original</th>
          <th>Tradução</th>
        </tr>
        {table_rows}
      </table>
      <div class="correction-area">
        {correction_html}
      </div>
      <div class="chunk-buttons">
        <button onclick="copyTranslation('{chunk_id}')">Copiar Tradução para Texto Final</button>
      </div>
      <div class="final-text">
        <h3>Texto Final (Edite abaixo)</h3>
        <textarea id="final_{chunk_id}" placeholder="Edite o texto final deste chunk..."></textarea>
      </div>
    </div>
"""
    html_content += """
    <button class="export-button" onclick="exportAllFinalText()">Exportar Texto Final Unificado (TXT)</button>
  </div>
</body>
</html>
"""
    with open(html_output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    webbrowser.open(html_output_file)
    print(f"Arquivo HTML gerado: {html_output_file}")

if __name__ == "__main__":
    main()
