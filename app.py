import streamlit as st
import subprocess
import os
from streamlit_javascript import st_javascript

st.title("IncorporaAI - Scraping de Imóveis")

st.write("Selecione os arquivos e pastas para executar o scraping de imóveis do Imovelweb e, opcionalmente, baixar Guias Amarelas.")

# Função para extrair caminho da pasta a partir de um arquivo selecionado
def get_folder_path(file_path):
    if file_path:
        return os.path.dirname(file_path) if file_path else ""
    return ""

# Formulário para inputs
edgedriver_file = st.file_uploader("Selecione o EdgeDriver (msedgedriver.exe):", type=["exe"], key="edgedriver")

# Função para criar um botão personalizado "Selecionar Pasta"
def custom_folder_picker(label, key, accept="*"):
    st.write(label)
    script = f"""
    <input type="file" id="{key}" style="display:none;" accept="{accept}" onchange="this.setAttribute('value', this.value);"/>
    <button onclick="document.getElementById('{key}').click();">Selecionar Pasta</button>
    <script>
    document.getElementById('{key}').addEventListener('change', function(e) {{
        if (e.target.files.length > 0) {{
            window.sessionStorage.setItem('{key}', e.target.files[0].path || e.target.files[0].webkitRelativePath || e.target.files[0].name);
        }}
    }});
    </script>
    """
    st.markdown(script, unsafe_allow_html=True)
    file_path = st_javascript(f"sessionStorage.getItem('{key}') || ''")
    return file_path

# Campos para pastas e CSV com botão "Selecionar Pasta"
pasta_imoveis_path = custom_folder_picker("Selecionar Pasta para salvar os arquivos Excel:", "pasta_imoveis")
pasta_guias_path = custom_folder_picker("Selecionar Pasta para salvar as Guias Amarelas (PDF):", "pasta_guias")
csv_path = custom_folder_picker("Selecionar Pasta para o arquivo CSV:", "csv", accept=".csv")

url = st.text_input("Link da página do Imovelweb:", key="url")
excel_name = st.text_input("Nome do arquivo Excel (sem extensão):", key="excel_name")
buscar_guias = st.checkbox("Buscar Guias Amarelas após o scraping", key="buscar_guias")

# Extrair caminhos de pastas
pasta_imoveis = get_folder_path(pasta_imoveis_path)
pasta_guias = get_folder_path(pasta_guias_path)

if st.button("Executar Scraping"):
    if not all([edgedriver_file, pasta_imoveis, pasta_guias, csv_path, url, excel_name]):
        st.error("Preencha todos os campos e selecione os arquivos/pastas!")
    else:
        # Salvar edgedriver.exe temporariamente
        edgedriver_path = os.path.join(os.getcwd(), "msedgedriver.exe")
        with open(edgedriver_path, "wb") as f:
            f.write(edgedriver_file.getvalue())
        
        # Para o CSV, usamos o caminho diretamente
        csv_caminho = os.path.join(os.getcwd(), os.path.basename(csv_path) if csv_path else "temp.csv")
        if not os.path.exists(csv_caminho):
            with open(csv_caminho, "w") as f:
                pass  # Cria um arquivo CSV vazio se não existir
        
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