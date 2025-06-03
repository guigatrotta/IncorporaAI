import streamlit as st
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import MsEdgeDriverManager
import pandas as pd
import os
import zipfile
import re
import time
import csv

# Diretório temporário
TEMP_DIR = "./temp"
os.makedirs(TEMP_DIR, exist_ok=True)

st.set_page_config(page_title="IncorporaAI", layout="centered")
st.title("🏘️ IncorporaAI - Scraping + Guias Amarelas")

# Inputs
url = st.text_input("🔗 Link do Imovelweb:", key="url")
excel_name = st.text_input("📁 Nome do arquivo Excel (sem extensão):", key="excel_name")
buscar_guias = st.checkbox("📄 Buscar Guias Amarelas", key="buscar_guias")

def iniciar_scraping(url, nome_arquivo):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    driver = webdriver.Edge(service=Service(MsEdgeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(5)
    imoveis = []

    anuncio_index = 1
    falhas_seguidas = 0
    limite_falhas = 5
    start_time = time.time()

    def safe_find(xpath):
        try:
            return driver.find_element("xpath", xpath).text
        except:
            return ""

    def safe_href(xpath):
        try:
            return driver.find_element("xpath", xpath).get_attribute("href")
        except:
            return ""

    while True:
        try:
            base_xpath = f"/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div[{anuncio_index}]/div/div[1]/div[2]/div[1]/div[1]"
            valor = safe_find(f"{base_xpath}/div[1]/div/div/div/div[1]/div")
            endereco = safe_find(f"{base_xpath}/div[2]/div/div")
            bairro = safe_find(f"{base_xpath}/div[2]/div/h2")
            area = safe_find(f"{base_xpath}/div[3]/h3/span[1]")
            quartos = safe_find(f"{base_xpath}/div[3]/h3/span[2]")
            banheiros = safe_find(f"{base_xpath}/div[3]/h3/span[3]")
            vagas = safe_find(f"{base_xpath}/div[3]/h3/span[4]")
            link = safe_href(f"{base_xpath}/h3/a")

            if not any([valor, endereco, bairro, area]):
                falhas_seguidas += 1
                if falhas_seguidas >= limite_falhas:
                    break
                anuncio_index += 1
                continue

            imoveis.append({
                "Endereco": endereco,
                "Bairro": bairro,
                "Valor": valor,
                "Area": area,
                "Quartos": quartos,
                "Banheiros": banheiros,
                "Vagas": vagas,
                "Link": link
            })

            anuncio_index += 1
        except:
            break

    driver.quit()

    df = pd.DataFrame(imoveis)
    df["Valor"] = df["Valor"].str.replace("R\\$|\\.", "", regex=True).str.replace(",", ".").apply(pd.to_numeric, errors='coerce')
    df["Area"] = df["Area"].str.extract(r"(\d+)").apply(pd.to_numeric, errors='coerce')
    df["Quartos"] = df["Quartos"].apply(lambda x: int(re.search(r"\d+", x).group()) if pd.notna(x) and re.search(r"\d+", x) else 0)
    df["Banheiros"] = df["Banheiros"].apply(lambda x: int(re.search(r"\d+", x).group()) if pd.notna(x) and re.search(r"\d+", x) else 0)
    df["Vagas"] = df["Vagas"].apply(lambda x: int(re.search(r"\d+", x).group()) if pd.notna(x) and re.search(r"\d+", x) else 0)
    df["Valor por m²"] = (df["Valor"] / df["Area"]).round(2)
    media = df[["Valor", "Area", "Quartos", "Banheiros", "Vagas", "Valor por m²"]].mean().to_frame().T
    media["Endereco"] = "Média"; media["Bairro"] = "-"; media["Link"] = "-"
    df = pd.concat([df, media], ignore_index=True, sort=False)
    df = df[["Endereco", "Bairro", "Valor", "Area", "Valor por m²", "Quartos", "Banheiros", "Vagas", "Link"]]

    caminho_excel = os.path.join(TEMP_DIR, f"{nome_arquivo}.xlsx")
    df.to_excel(caminho_excel, index=False)

    caminho_csv = os.path.join(TEMP_DIR, "output.csv")
    enderecos = []
    for end in df["Endereco"][:-1]:
        match = re.match(r"(.+?),?\s?(\d+.*)", end)
        if match:
            logradouro = match.group(1).strip()
            numero = match.group(2).strip()
            bairro = df[df["Endereco"] == end]["Bairro"].values[0]
            enderecos.append([logradouro, numero, bairro])
    with open(caminho_csv, "w", newline='', encoding='latin-1') as f:
        writer = csv.writer(f)
        writer.writerow(["logradouro", "numero", "bairro"])
        writer.writerows(enderecos)

    return caminho_excel, caminho_csv

if st.button("🚀 Executar"):
    if not url or not excel_name:
        st.error("Preencha todos os campos!")
    else:
        excel_path, csv_path = iniciar_scraping(url, excel_name)
        st.success("Scraping finalizado com sucesso!")

        with open(excel_path, "rb") as f:
            st.download_button("📥 Baixar Excel", f, file_name=os.path.basename(excel_path))

        with open(csv_path, "rb") as f:
            st.download_button("📥 Baixar endereços (CSV)", f, file_name="enderecos.csv")

        if buscar_guias:
            st.warning("⚠️ Automação das Guias Amarelas será integrada em breve.")