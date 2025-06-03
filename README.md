# IncorporaAI

Este repositório contém duas formas de executar o scraping de anúncios e gerar informações em planilhas.

## Instalação

Instale as dependências em um ambiente Python 3:

```bash
pip install -r requirements.txt
```

## Executando com Streamlit

Para abrir a interface web do projeto, execute:

```bash
streamlit run app.py
```

A aplicação cria automaticamente o diretório `temp` para armazenar o Excel e o CSV gerados após a execução.

## Executando o script `IncorporaAI 4.0.py`

Prepare um arquivo `inputs.txt` com quatro linhas contendo:

1. Caminho do EdgeDriver.
2. URL do Imovelweb a ser raspado.
3. Nome desejado para o Excel (sem extensão).
4. `s` ou `n` indicando se as Guias Amarelas devem ser baixadas.

Depois execute:

```bash
python 'IncorporaAI 4.0.py'
```

Os resultados (Excel, `output.csv` e, se solicitados, os PDFs e o ZIP das Guias) serão gravados dentro do diretório `temp`, criado automaticamente.
