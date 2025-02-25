# Dify Translator Project

Este projeto automatiza todo o fluxo de tradução, correção e revisão de arquivos de texto utilizando a API Dify. O sistema divide o arquivo de entrada em partes menores (chunks), envia cada parte para tradução e, em seguida, para correção. Por fim, gera uma interface HTML interativa para que o usuário revise, edite e exporte o resultado final em formatos TXT e DOCX.

---

## Funcionalidades

- **Divisão de Texto:**  
  O arquivo de entrada é automaticamente dividido em chunks para facilitar o processamento.

- **Tradução Automatizada:**  
  Cada chunk é enviado para a API Dify, que realiza a tradução do texto.

- **Correção Automatizada:**  
  O texto original e a tradução são combinados e enviados para correção. As correções são organizadas em duas seções:

  - **OBSERVAÇÕES E AJUSTES:** Comentários e sugestões pontuais.
  - **VERSÃO CORRIGIDA (APENAS TRECHOS RELEVANTES):** Trechos revisados e aprimorados.

- **Interface de Revisão Interativa (HTML):**  
  Gera um arquivo HTML que exibe lado a lado o texto original, a tradução e as correções – permitindo a edição do texto final por chunk.

- **Exportação:**  
  O usuário pode exportar o texto final unificado em formato TXT, com opção de conversão para DOCX através de um script auxiliar.

---

## Estrutura do Projeto

```plaintext
dify-translator/
│
├── data/
│   └── input/                 # Arquivos de entrada para tradução.
│     └── pdf/
│        ├── converted/        # TXTs convertidos
│        └── original/         # PDFs para serem convertidos
│     └── txt_original/        # Arquivos originalmente TXT
│   └── output/                # Saída gerada automaticamente pelo orquestrador.
│       └── output_<nome>/     # Pasta de saída com:
│           ├── chunks/        # Chunks de texto gerados.
│           ├── translated/    # Arquivos traduzidos (Markdown).
│           └── correcao/      # Arquivos corrigidos (Markdown).
├── scripts/
│   ├── setup_env.sh           # Script para configurar o ambiente do projeto.
│   ├── run_translation.py     # Orquestra todo o fluxo de tradução.
│   └── gerar_html.py          # Gera a interface HTML para revisão dos chunks.
├── src/
│   ├── split_text.py          # Divide o arquivo de entrada em chunks.
│   ├── send_to_api.py         # Envia os chunks para tradução via API Dify.
│   ├── extract_pdf.py         # Extrai o texto de PDF e passa para um TXT
│   └── correction.py          # Combina o original e a tradução para correção via API.
│
│
├── requirements.txt           # Dependências do projeto.
└── README.md                  # Este arquivo.
```

---

## Configuração Inicial

1. **Clone o Repositório:**

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd dify-translator
   ```

2. **Instale as Dependências:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Organize os Arquivos de Entrada:**
   - Coloque os arquivos de texto (TXT) a serem traduzidos na pasta `data/input/`.

---

## Uso

### Execução Completa do Fluxo

O fluxo completo é iniciado pelo script **orquestrador.py**. Para executá-lo, abra um terminal e utilize o comando:

```bash
python src/orquestrador.py <nome_arquivo.txt> <API_KEY_TRADUCAO> <API_KEY_CORRECAO>
```

- `<nome_arquivo.txt>`: Nome do arquivo presente em `data/input/`.
- `<API_KEY_TRADUCAO>`: Chave da API para tradução.
- `<API_KEY_CORRECAO>`: Chave da API para correção.

**Exemplo:**

```bash
python src/orquestrador.py MeuTexto.txt minhaChaveTraducao minhaChaveCorrecao
```

> **Nota:** O orquestrador criará automaticamente uma pasta de saída em `data/output/output_<nome_arquivo>` com as subpastas `chunks`, `translated` e `correcao`.

O fluxo para usar o **extract_pdf.py** eh colocar o pdf original na pasta `data/input/pdf/original` onde sua verção txt sera armazenada automaticamente em `data/input/pdf/converted`, para utilizar a função deve executar o seguinte comando

```bash
python src/extract_pdf.py <entrada.pdf>
```

sendo que o arquivo de entrada deve ser digitado entre aspas, seguindo o exemplo, sendo que não eh necessario colocar a pasta do arquivo de entrada, porem ele deve estar em `data/input/pdf/original`

```bash
python src/extract_pdf.py "La Peculiaridad de lo Estetico Vol. 1.pdf"
```

O fluxo para usar o **split_text.py** eh utilizar o comando abaixo com o caminho do txt a ser divido, como por exemplo `data/input/txt_original/{nome_do_txt}`, os arquivos de chunk serão armazenadas em `data/output/output_{nome_do_txt}/chunks`

```bash
python src/split_text.py <caminho_para_entrada.txt>
```

O fluxo para usar o **correction.py** eh colocar o mesmo do **generate_html.py**, porem com a alteração do arquivo a ser executado

```bash
python src/correction.py <caminho_para_a_pasta_output>
```

### Revisão e Exportação

1. **Geração do HTML para Revisão:**
   Após a execução do orquestrador, execute o script para gerar a interface HTML:

   ```bash
   python scripts/gerar_html.py <caminho_para_a_pasta_output>
   ```

   ex de uso do comando `scripts>python generate_html.py "data\output\output_teste"`

   - No HTML, cada chunk exibirá:
     - **Original:** Texto original.
     - **Tradução:** Texto traduzido.
     - **Correções:** Separadas em “OBSERVAÇÕES E AJUSTES” e “VERSÃO CORRIGIDA (APENAS TRECHOS RELEVANTES)” (se os marcadores estiverem presentes no conteúdo de correção).
     - **Área para Edição:** Onde você pode editar o texto final.

2. **Exportação do Texto Final:**
   - No HTML, utilize o botão “Exportar Texto Final Unificado (TXT)” para baixar um arquivo TXT com o texto final de todos os chunks.

---

## Fluxo de Trabalho

1. **Divisão do Texto (`split_text.py`):**  
   Divide o arquivo de entrada em chunks menores.

2. **Tradução (`send_to_api.py`):**  
   Cada chunk é enviado para a API Dify e o resultado é salvo em Markdown na pasta `translated`.

3. **Correção (`correction.py`):**  
   Combina o texto original e a tradução, enviando para correção via API, e salva os resultados na pasta `correcao`.

4. **Revisão Interativa (`gerar_html.py`):**  
   Gera um HTML que permite a visualização e edição interativa dos textos (original, tradução e correção).

5. **Exportação:**
   - **TXT:** Gerado diretamente via interface HTML.

---

## Contribuições

Contribuições são sempre bem-vindas! Para contribuir:

1. **Fork o repositório.**
2. **Crie uma branch para suas alterações:**
   ```bash
   git checkout -b minha-feature
   ```
3. **Realize os commits com suas mudanças:**
   ```bash
   git commit -m "Descrição das alterações"
   ```
4. **Envie sua branch para o seu fork:**
   ```bash
   git push origin minha-feature
   ```
5. **Abra um Pull Request** no repositório original descrevendo suas alterações.

---

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

---

## Contribuidores

- [@v-rogana](https://github.com/v-rogana) - Criador e mantenedor principal
- [@pdMiranda](https://github.com/pdMiranda) - Melhorias na API de tradução
