# Dify Translator Project

Este projeto automatiza o fluxo de tradução de arquivos de texto usando a API Dify, estruturando cada etapa em scripts independentes e bem organizados. O fluxo completo é executado pelo script `run_translation.py`.

## Estrutura do Projeto

```plaintext
dify-translator/
│
├── src/
│   ├── split_text.py          # Quebra o arquivo de entrada em chunks.
│   ├── send_to_api.py         # Envia os chunks para tradução pela API.
│   ├── concat_md.py           # Concatena os arquivos traduzidos em um único arquivo .md.
│   ├── md_to_docx.py          # Converte o arquivo .md final para .docx.
│
├── data/
│   ├── input/                 # Pasta para os arquivos de texto a serem traduzidos.
│   ├── output/
│       ├── chunks/            # Chunks de texto gerados na etapa de divisão.
│       ├── translated/        # Arquivos traduzidos e o resultado final.
│
├── scripts/
│   ├── setup_env.sh           # Script para configurar o ambiente do projeto.
│   ├── run_translation.py     # Orquestra todo o fluxo de tradução.
│
├── requirements.txt           # Dependências do projeto.
├── README.md                  # Documentação do projeto.
```

## Requisitos

- Python 3.8+
- Linux ou macOS
- Ambiente configurado com as bibliotecas do `requirements.txt`

## Configuração Inicial

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd dify-translator
   ```

2. Torne o script de setup executável:
   ```bash
   chmod +x scripts/setup_env.sh
   ```

3. Execute o script de setup:
   ```bash
   ./scripts/setup_env.sh
   ```

4. Coloque o arquivo de entrada em `data/input/`.

## Uso

1. **Executar o fluxo completo**:
   ```bash
   python3 scripts/run_translation.py
   ```

2. **Alterar o arquivo de entrada**:
   - Modifique o valor da variável `input_filename` no arquivo `run_translation.py`.
   - O nome do arquivo traduzido será baseado no nome do arquivo de entrada (ex.: `unified_<nome>.md` e `unified_<nome>.docx`).

## Fluxo de Trabalho

1. **Divisão do Texto** (`split_text.py`):
   - Quebra o texto em chunks menores para facilitar a tradução.

2. **Envio para a API** (`send_to_api.py`):
   - Processa os chunks e obtém a tradução de cada parte.

3. **Concatenação** (`concat_md.py`):
   - Junta todos os arquivos traduzidos em um único `.md`.

4. **Conversão para DOCX** (`md_to_docx.py`):
   - Converte o arquivo Markdown final para um documento Word.

## Contribuições

1. Abra um fork do repositório.
2. Crie uma branch para suas alterações:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça o commit de suas mudanças:
   ```bash
   git commit -m "Descrição das mudanças"
   ```
4. Envie suas alterações:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).
