import streamlit as st
import subprocess
import os

st.title("IncorporaAI - Scraping de Imóveis")

st.write("Este aplicativo executa o script de scraping de imóveis do Imovelweb e, opcionalmente, baixa Guias Amarelas.")

# Formulário para inputs
edgedriver_path = st.text_input("Caminho do EdgeDriver (msedgedriver.exe):")
pasta_imoveis = st.text_input("Pasta para salvar os arquivos Excel:")
pasta_guias = st.text_input("Pasta para salvar as Guias Amarelas (PDF):")
csv_caminho = st.text_input("Caminho para salvar o CSV:")
url = st.text_input("Link da página do Imovelweb:")
excel_name = st.text_input("Nome do arquivo Excel (sem extensão):")
buscar_guias = st.checkbox("Buscar Guias Amarelas após o scraping")

if st.button("Executar Scraping"):
    if not all([edgedriver_path, pasta_imoveis, pasta_guias, csv_caminho, url, excel_name]):
        st.error("Preencha todos os campos!")
    else:
        # Salvar inputs em um arquivo temporário
        with open("inputs.txt", "w") as f:
            f.write(f"{edgedriver_path}\n{pasta_imoveis}\n{pasta_guias}\n{csv_caminho}\n{url}\n{excel_name}\n{'s' if buscar_guias else 'n'}")
        
        # Executar o script principal
        try:
            result = subprocess.run(["python", "IncorporaAI 4.0.py"], capture_output=True, text=True)
            st.text_area("Saída do Script", result.stdout, height=300)
            if result.stderr:
                st.error(f"Erro: {result.stderr}")
            st.success("Scraping concluído!")
        except Exception as e:
            st.error(f"Erro ao executar o script: {e}")