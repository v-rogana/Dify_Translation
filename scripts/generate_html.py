import os
import re
import webbrowser

# --- Solicitação do caminho ---
default_folder = r"C:\Users\victo\OneDrive\Documentos\Projetos_Allos\Dify_translation\data\output\output_Essays_Empirism"
user_input = input(f"Informe o caminho da pasta de output (default: {default_folder}): ").strip()
if not user_input:
    base_output_folder = default_folder
else:
    base_output_folder = user_input

print("Caminho informado:", repr(base_output_folder))
if not os.path.isdir(base_output_folder):
    print("O caminho informado não existe ou não é um diretório. Por favor, verifique e tente novamente.")
    exit(1)

# --- Define os diretórios de cada etapa ---
txt_folder = os.path.join(base_output_folder, "chunks")         # Arquivos originais (TXT)
translated_folder = os.path.join(base_output_folder, "translated")  # Arquivos traduzidos (MD)
corrected_folder = os.path.join(base_output_folder, "correcao")       # Arquivos de correção (MD)

# --- Nome do arquivo HTML final ---
folder_name = os.path.basename(base_output_folder)
if folder_name.lower().startswith("output_"):
    suffix = folder_name[7:]  # remove "output_"
else:
    suffix = folder_name
html_file_name = f"revisao_humana_{suffix}.html"
html_output_file = os.path.join(base_output_folder, html_file_name)

# --- Funções Auxiliares ---
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
    """Lê o arquivo em UTF-8 e retorna o conteúdo."""
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

def split_correction_items(text):
    """
    Separa o texto de correção em itens enumerados.
    Exemplo: "1. [Error] ... 2. [Melhoria] ..." 
    → retorna uma lista de itens, que serão exibidos como bullet points.
    """
    single_line = " ".join(text.split("\n"))
    if not single_line.strip():
        return []
    # Divide considerando um número seguido de ponto e espaço
    items = re.split(r'(?=\d+\.\s)', single_line)
    items = [item.strip() for item in items if item.strip()]
    return items

# --- Carrega os arquivos de cada subpasta ---
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

all_chunks = sorted(
    set(list(txt_files.keys()) + list(translated_files.keys()) + list(corrected_files.keys())),
    key=lambda x: int(x)
)

# --- Geração do conteúdo HTML ---
html_content = r"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Revisão Final: Correção, Original e Tradução</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      padding: 0;
    }
    .container {
      width: 90%;
      max-width: 1200px;
      margin: 20px auto;
      background-color: #fff;
      padding: 20px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .header {
      text-align: center;
      margin-bottom: 20px;
    }
    .header h1 {
      margin: 0;
      font-size: 28px;
      color: #333;
    }
    .header p {
      color: #666;
      font-size: 16px;
    }
    .chunk-container {
      border: 1px solid #ddd;
      margin-bottom: 30px;
      padding: 15px;
      border-radius: 8px;
      background-color: #fafafa;
    }
    .chunk-header {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 10px;
      color: #333;
    }
    .comparison-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 10px;
    }
    .comparison-table th, .comparison-table td {
      border: 1px solid #ccc;
      padding: 8px;
      vertical-align: top;
    }
    .comparison-table th {
      background-color: #f0f0f0;
      font-weight: bold;
    }
    .correction-area {
      background-color: #fff8e1;
      border: 1px solid #ffeb3b;
      border-radius: 4px;
      padding: 10px;
      max-height: 150px;
      overflow-y: auto;
      margin-bottom: 10px;
    }
    .correction-area ul {
      margin: 0;
      padding-left: 20px;
    }
    .correction-area li {
      margin-bottom: 5px;
    }
    .final-text {
      margin-top: 10px;
    }
    .final-text textarea {
      width: 100%;
      min-height: 150px;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 5px;
      font-size: 16px;
      resize: vertical;
    }
    .chunk-buttons {
      margin-top: 10px;
    }
    .chunk-buttons button {
      margin-right: 10px;
      padding: 8px 12px;
      background-color: #4285f4;
      color: #fff;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    .chunk-buttons button:hover {
      background-color: #3367d6;
    }
    .export-button {
      display: block;
      width: 100%;
      padding: 12px;
      background-color: #4CAF50;
      color: #fff;
      border: none;
      border-radius: 4px;
      font-size: 18px;
      cursor: pointer;
      margin-top: 20px;
    }
    .export-button:hover {
      background-color: #45a049;
    }
  </style>
  <script>
    function copyTranslation(chunkId) {
      // Seleciona todos os parágrafos da coluna de tradução para o chunk
      var transCells = document.querySelectorAll("#chunk_" + chunkId + " .translation-paragraph");
      var text = "";
      for (var i = 0; i < transCells.length; i++) {
        text += transCells[i].innerText.trim() + "\n\n";
      }
      var finalTextArea = document.getElementById("final_" + chunkId);
      if (finalTextArea) {
        finalTextArea.value = text.trim();
      }
    }
    
    function exportAllFinalText() {
      var finalTextAreas = document.querySelectorAll(".final-text textarea");
      var combinedText = "";
      // Itera sobre cada campo de texto final e adiciona um rótulo com o número do chunk
      for (var i = 0; i < finalTextAreas.length; i++) {
        var idParts = finalTextAreas[i].id.split("_"); // Exemplo: "final_1"
        var chunkNum = idParts[1];
        combinedText += "Chunk " + chunkNum + ":\n" + finalTextAreas[i].value.trim() + "\n\n";
      }
      if (!combinedText) {
        alert("Nenhum texto final foi inserido.");
        return;
      }
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
"""

for chunk in all_chunks:
    orig_text = read_file(txt_files.get(chunk, "")) if chunk in txt_files else ""
    trans_text = read_file(translated_files.get(chunk, "")) if chunk in translated_files else ""
    corr_text = read_file(corrected_files.get(chunk, "")) if chunk in corrected_files else ""
    
    orig_paragraphs = merge_paragraphs(orig_text)
    trans_paragraphs = merge_paragraphs(trans_text)
    max_rows = max(len(orig_paragraphs), len(trans_paragraphs))
    orig_paragraphs += [""] * (max_rows - len(orig_paragraphs))
    trans_paragraphs += [""] * (max_rows - len(trans_paragraphs))
    
    table_rows = ""
    for i in range(max_rows):
        table_rows += f"<tr><td>{orig_paragraphs[i]}</td><td class='translation-paragraph'>{trans_paragraphs[i]}</td></tr>"
    
    corrections = split_correction_items(corr_text)
    if corrections:
        correction_html = "<ul>"
        for item in corrections:
            correction_html += f"<li>{item}</li>"
        correction_html += "</ul>"
    else:
        correction_html = "Nenhuma correção registrada."
    
    html_content += f"""
    <div class="chunk-container" id="chunk_{chunk}">
      <div class="chunk-header">Chunk {chunk}</div>
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
        <button onclick="copyTranslation('{chunk}')">Copiar Tradução para Texto Final</button>
      </div>
      <div class="final-text">
        <h3>Texto Final (Edite abaixo)</h3>
        <textarea id="final_{chunk}" placeholder="Edite o texto final deste chunk..."></textarea>
      </div>
    </div>
    """
    
html_content += """
    <button class="export-button" onclick="exportAllFinalText()">Exportar Texto Final Unificado</button>
  </div>
</body>
</html>
"""

with open(html_output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open(html_output_file)
print(f"Arquivo HTML gerado: {html_output_file}")
