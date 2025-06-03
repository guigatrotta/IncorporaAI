import os
import re
import csv
import time
import requests
import pandas as pd
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime

# Função para ler inputs de um arquivo inputs.txt
def get_user_inputs():
    with open("inputs.txt", "r") as f:
        lines = f.readlines()
    return {
        "edgedriver_path": lines[0].strip(),
        "url": lines[1].strip(),
        "excel_name": lines[2].strip(),
        "buscar_guias": lines[3].strip().lower() == "s"
    }

# Criar diretório temporário
temp_dir = "./temp"
os.makedirs(temp_dir, exist_ok=True)

# Coleta os caminhos
inputs = get_user_inputs()
EDGEDRIVER_PATH = inputs["edgedriver_path"]
url = inputs["url"]
nome_arquivo = inputs["excel_name"]
buscar_guias = inputs["buscar_guias"]

# Configura navegador
options = Options()
options.add_argument("--start-maximized")
service = Service(executable_path=EDGEDRIVER_PATH)
driver = webdriver.Edge(service=service, options=options)
wait = WebDriverWait(driver, 15)

# Scraping Imovelweb
driver.get(url)
time.sleep(5)

# Contar o número total de anúncios na página
try:
    anuncios = driver.find_elements(By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/div")
    total_anuncios = len(anuncios)
except:
    total_anuncios = 0
    print("Não foi possível contar os anúncios. Prosseguindo sem total.")

anuncio_index = 1
imoveis = []
falhas_seguidas = 0
limite_falhas = 5
start_time = time.time()

while True:
    try:
        def safe_find(xpath):
            try:
                return driver.find_element(By.XPATH, xpath).text
            except NoSuchElementException:
                return ""

        def safe_href(xpath):
            try:
                return driver.find_element(By.XPATH, xpath).get_attribute("href")
            except NoSuchElementException:
                return ""

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
                print("Fim dos anúncios por falhas seguidas.")
                break
            anuncio_index += 1
            continue

        falhas_seguidas = 0
        imoveis.append({"Endereco": endereco, "Bairro": bairro, "Valor": valor, "Area": area,
                        "Quartos": quartos, "Banheiros": banheiros, "Vagas": vagas, "Link": link})

        elapsed = time.time() - start_time
        anuncios_processados = len(imoveis)
        if total_anuncios > 0:
            avg_time_per_ad = elapsed / anuncios_processados if anuncios_processados > 0 else 0
            estimated_time = (total_anuncios - anuncios_processados) * avg_time_per_ad
            print(f"{anuncios_processados}/{total_anuncios} anúncios rastreados | Tempo decorrido: {int(elapsed)}s | Tempo estimado restante: {int(estimated_time)}s")
        else:
            print(f"{anuncios_processados} anúncios rastreados | Tempo decorrido: {int(elapsed)}s")

        anuncio_index += 1
        time.sleep(1)

    except NoSuchElementException:
        break

driver.quit()

# Processamento e exportação
caminho_arquivo = os.path.join(temp_dir, f"{nome_arquivo}.xlsx")

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
df.to_excel(caminho_arquivo, index=False)
print(f"Arquivo Excel salvo em: {caminho_arquivo}")

caminho_csv = os.path.join(temp_dir, "output.csv")
enderecos = []
for end in df["Endereco"][:-1]:
    match = re.match(r"(.+?),?\s?(\d+.*)", end)
    if match:
        logradouro = match.group(1).strip()
        numero = match.group(2).strip()
        bairro = df[df["Endereco"] == end]["Bairro"].values[0]
        enderecos.append([logradouro, numero, bairro])
    else:
        print(f"Ignorado: {end}")

with open(caminho_csv, "w", newline='', encoding='latin-1') as f:
    writer = csv.writer(f)
    writer.writerow(["logradouro", "numero", "bairro"])
    writer.writerows(enderecos)
print(f"Arquivo CSV salvo em: {caminho_csv}")

if buscar_guias:
    driver = webdriver.Edge(service=Service(executable_path=EDGEDRIVER_PATH), options=options)
    wait = WebDriverWait(driver, 15)
    pdf_dir = os.path.join(temp_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)

    with open(caminho_csv, newline='', encoding='latin-1') as csvfile:
        reader = list(csv.reader(csvfile, delimiter=','))
        total = len(reader) - 1
        start_time_guias = time.time()
        for i, row in enumerate(reader[1:], start=1):
            logradouro_input, numero_input, bairro = row
            bairro = bairro.strip().replace(" ", "_")
            
            elapsed_guias = time.time() - start_time_guias
            avg_time_per_guia = elapsed_guias / i if i > 0 else 0
            estimated_time_guias = (total - i) * avg_time_per_guia
            
            print(f"Baixando guia {i}/{total} para {logradouro_input}, {numero_input} | Tempo decorrido: {int(elapsed_guias)}s | Tempo estimado restante: {int(estimated_time_guias)}s")

            try:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get("https://geocuritiba.ippuc.org.br/mapacadastral/")
                time.sleep(2)
                try:
                    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/button"))).click()
                except: pass

                logradouro_field = wait.until(EC.element_to_be_clickable((By.ID, "dijit_form_ComboBox_2")))
                logradouro_field.clear()
                for c in logradouro_input: logradouro_field.send_keys(c); time.sleep(0.1)
                time.sleep(1.5)
                logradouro_field.send_keys(Keys.DOWN, Keys.ENTER)

                numero_field = wait.until(EC.element_to_be_clickable((By.ID, "dijit_form_ComboBox_3")))
                numero_field.click()
                numero_field.clear()
                for c in numero_input: numero_field.send_keys(c); time.sleep(0.1)
                time.sleep(1.5)
                numero_field.send_keys(Keys.DOWN, Keys.ENTER)

                time.sleep(2)
                guia_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "CONSULTA INFORMATIVA DE LOTE (GUIA AMARELA)")))
                guia_link.click()
                time.sleep(2)
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)

                try:
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "proceed-button"))).click()
                except: pass

                emitir_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "_ctl0_MainContent_btnEmitir")))
                emitir_btn.click()
                time.sleep(3)
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)

                pdf_url = driver.current_url
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://geocuritiba.ippuc.org.br"}
                response = requests.get(pdf_url, headers=headers)
                if response.status_code == 200 and b"%PDF" in response.content[:10]:
                    nome_final = f"{bairro}-{numero_input}.pdf"
                    caminho_final = os.path.join(pdf_dir, nome_final)
                    with open(caminho_final, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ PDF salvo como: {nome_final}")
                else:
                    print(f"❌ Conteúdo inválido para {bairro}-{numero_input}")

            except Exception as e:
                print(f"❌ Erro com {logradouro_input}, {numero_input}: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

    driver.quit()
    print("\U0001F3C1 Processo finalizado.")

    # Criar ZIP com os PDFs
    zip_path = os.path.join(temp_dir, "guias_amarelas.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(pdf_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_dir))
    print(f"Arquivo ZIP salvo em: {zip_path}")