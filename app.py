from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeDriverManager
import streamlit as st
import os

st.title("IncorporaAI - Scraping de Imóveis")

st.write("Insira os dados para executar o scraping de imóveis do Imovelweb e, opcionalmente, baixar Guias Amarelas.")
st.write("Após a execução, links para download dos arquivos gerados serão fornecidos.")

# Inputs
url = st.text_input("Link da página do Imovelweb:", key="url")
excel_name = st.text_input("Nome do arquivo Excel (sem extensão):", key="excel_name")
buscar_guias = st.checkbox("Buscar Guias Amarelas após o scraping", key="buscar_guias")

if st.button("Executar Scraping"):
    if not all([url, excel_name]):
        st.error("Preencha todos os campos corretamente!")
    else:
        try:
            # Configuração dinâmica do EdgeDriver
            service = Service(EdgeDriverManager().install())
            driver = webdriver.Edge(service=service)

            # Exemplo de inicialização do Selenium
            driver.get(url)
            # Adicione a lógica de scraping aqui

            st.success("Scraping concluído com sucesso!")
        except Exception as e:
            st.error(f"Erro ao iniciar o EdgeDriver ou executar o scraping: {e}")
        finally:
            if 'driver' in locals():
                driver.quit()