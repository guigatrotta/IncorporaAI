import streamlit as st
import subprocess
import os

st.title("IncorporaAI - Scraping de Imóveis")

st.write("Selecione os arquivos e pastas para executar o scraping de imóveis do Imovelweb e, opcionalmente, baixar Guias Amarelas.")

# Função para extrair caminho da pasta a partir de um arquivo selecionado
def get_folder_path(file):
    if file:
        return os.path.dirname(file.name) if hasattr(file, 'name') else ""
    return ""

# Formulário para inputs
edgedriver_file = st.file_uploader("Selecione o EdgeDriver (msedgedriver.exe):", type=["exe"], key="edgedriver")
pasta_imoveis_file = st.file_uploader("Selecionar Pasta para salvar os arquivos Excel:", type=["*"], key="pasta_imoveis")
pasta_guias_file = st.file_uploader("Selecionar Pasta para salvar as Guias Amarelas (PDF):", type=["*"], key="pasta_guias")
csv_file = st.file_uploader("Selecionar Pasta para o arquivo CSV:", type=["csv"], key="csv")
url = st.text_input("Link da página do Imovelweb:", key="url")
excel_name = st.text_input("Nome do arquivo Excel (sem extensão):", key="excel_name")
buscar_guias = st.checkbox("Buscar Guias Amarelas após o scraping", key="buscar_guias")

# Extrair caminhos de pastas
pasta_imoveis = get_folder_path(pasta_imoveis_file) if pasta_imoveis_file else ""
pasta_guias = get_folder_path(pasta_guias_file) if pasta_guias_file else ""

if st.button("Executar Scraping"):
    if not all([edgedriver_file, pasta_imoveis, pasta_guias, csv_file, url, excel_name]):
        st.error("Preencha todos os campos e selecione os arquivos/pastas!")
    else:
        # Salvar edgedriver.exe temporariamente
        edgedriver_path = os.path.join(os.getcwd(), "msedgedriver.exe")
        with open(edgedriver_path, "wb") as f:
            f.write(edgedriver_file.getvalue())
        
        # Salvar CSV temporariamente
        csv_caminho = os.path.join(os.getcwd(), csv_file.name)
        with open(csv_caminho, "wb") as f:
            f.write(csv_file.getvalue())
        
        # Salvar inputs em inputs.txt
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
        finally:
            # Limpar arquivos temporários
            if os.path.exists(edgedriver_path):
                os.remove(edgedriver_path)
            if os.path.exists(csv_caminho):
                os.remove(csv_caminho)
            if os.path.exists("inputs.txt"):
                os.remove("inputs.txt")