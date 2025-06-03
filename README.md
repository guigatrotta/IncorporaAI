# IncorporaAI

This project scrapes real estate listings from Imovelweb and can optionally retrieve "Guia Amarela" PDFs. The main interface is a Streamlit app, but a command-line script is also provided.

## Requirements
* Python 3.9 or newer
* Packages listed in `requirements.txt`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running the Streamlit app
Execute the following command to start the web interface:

```bash
streamlit run app.py
```

The app will open in your browser (default port 8501) and allows you to provide the Imovelweb URL and the desired Excel file name.

## Running the command-line scraper
The script `IncorporaAI 4.0.py` reads parameters from an `inputs.txt` file. Create `inputs.txt` with four lines:

1. Path to the Edge WebDriver executable
2. Imovelweb URL to scrape
3. Name of the Excel file without extension
4. `s` to download Guias Amarelas or `n` to skip

Example `inputs.txt`:

```
/path/to/msedgedriver
https://www.imovelweb.com.br/some/url
meu_arquivo
s
```

Then run the scraper with:

```bash
python "IncorporaAI 4.0.py"
```

Scraped data and downloaded PDFs are stored in the `temp` directory.
