import streamlit as st
import subprocess
import os

st.title("IncorporaAI - Scraping de Imóveis")

st.write("Selecione os arquivos e pastas para executar o scraping de imóveis do Imovelweb e, opcionalmente, baixar Guias Amarelas.")
st.write("Para selecionar pastas, clique em 'Browse files' e escolha qualquer arquivo dentro da pasta desejada. O script usará a pasta onde o arquivo está localizado.")

# Função para extrair caminho da pasta a partir de um arquivo selecionado
def get_folder_path(file):
    if file and len(file) > 0:
        return os.path.dirname(file[0].name) if hasattr(file[0], 'name') else ""
    return ""

# Formulário para inputs
edgedriver_file = st.file_uploader("Selecione o EdgeDriver (msedgedriver.exe):", type=["exe"], key="edgedriver")
pasta_imoveis_files = st.file_uploader("Selecionar Pasta para salvar os arquivos Excel:", type=["*"], accept_multiple_files=True, key="pasta_imoveis")
pasta_guias_files = st.file_uploader("Selecionar Pasta para salvar as Guias Amarelas (PDF):", type=["*"], accept_multiple_files=True, key="pasta_guias")
csv_files = st.file_uploader("Selecionar Pasta para o arquivo CSV:", type=["*"], accept_multiple_files=True, key="csv")
url = st.text_input("Link da página do Imovelweb:", key="url")
excel_name = st.text_input("Nome do arquivo Excel (sem extensão):", key="excel_name")
buscar_guias = st.checkbox("Buscar Guias Amarelas após o scraping", key="buscar_guias")

# Extrair caminhos de pastas
pasta_imoveis = get_folder_path(pasta_imoveis_files)
pasta_guias = get_folder_path(pasta_guias_files)
csv_folder = get_folder_path(csv_files)

# Exibir pastas selecionadas (para feedback ao usuário)
if pasta_imoveis:
    st.success(f"Pasta para arquivos Excel selecionada: {pasta_imoveis}")
if pasta_guias:
    st.success(f"Pasta para Guias Amarelas selecionada: {pasta_guias}")
if csv_folder:
    st.success(f"Pasta para o arquivo CSV selecionada: {csv_folder}")

# Definir caminho padrão para o CSV (usando a pasta selecionada e um nome fixo)
csv_caminho = os.path.join(csv_folder, "output.csv") if csv_folder else ""

if st.button("Executar Scraping"):
    if not all([edgedriver_file, pasta_imoveis, pasta_guias, csv_folder, url, excel_name]):
        st.error("Preencha todos os campos e selecione os arquivos/pastas!")
    else:
        # Salvar edgedriver.exe temporariamente
        edgedriver_path = os.path.join(os.getcwd(), "msedgedriver.exe")
        with open(edgedriver_path, "wb") as f:
            f.write(edgedriver_file.getvalue())
        
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
            if os.path.exists("inputs.txt"):
                os.remove("inputs.txt")