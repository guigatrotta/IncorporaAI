import streamlit as st
import subprocess
import os
import sys

st.title("IncorporaAI - Scraping de Imóveis")

st.write("Insira os dados para executar o scraping de imóveis do Imovelweb e, opcionalmente, baixar Guias Amarelas.")
st.write("Após a execução, links para download dos arquivos gerados serão fornecidos.")

# Inputs fixos locais
edgedriver_path = os.path.join(os.getcwd(), "drivers", "msedgedriver.exe")
url = st.text_input("Link da página do Imovelweb:", key="url")
excel_name = st.text_input("Nome do arquivo Excel (sem extensão):", key="excel_name")
buscar_guias = st.checkbox("Buscar Guias Amarelas após o scraping", key="buscar_guias")

if st.button("Executar Scraping"):
    if not all([os.path.exists(edgedriver_path), url, excel_name]):
        st.error("Preencha todos os campos corretamente e verifique o caminho do EdgeDriver!")
    else:
        # Salvar inputs em inputs.txt
        with open("inputs.txt", "w") as f:
            f.write(f"{edgedriver_path}\n{url}\n{excel_name}\n{'s' if buscar_guias else 'n'}")

        # Executar o script principal com o mesmo Python do ambiente atual
        try:
            result = subprocess.run([sys.executable, "IncorporaAI 4.0.py"], capture_output=True, text=True)
            st.text_area("Saída do Script", result.stdout, height=300)
            if result.stderr:
                st.error(f"Erro: {result.stderr}")
            else:
                st.success("Scraping concluído!")

                # Fornecer links de download
                excel_path = os.path.join("./temp", f"{excel_name}.xlsx")
                csv_path = os.path.join("./temp", "output.csv")
                zip_path = os.path.join("./temp", "guias_amarelas.zip") if buscar_guias else None

                if os.path.exists(excel_path):
                    with open(excel_path, "rb") as f:
                        st.download_button(
                            label="Download do Arquivo Excel",
                            data=f,
                            file_name=f"{excel_name}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                if os.path.exists(csv_path):
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            label="Download do Arquivo CSV",
                            data=f,
                            file_name="output.csv",
                            mime="text/csv"
                        )
                if buscar_guias and os.path.exists(zip_path):
                    with open(zip_path, "rb") as f:
                        st.download_button(
                            label="Download do ZIP com Guias Amarelas",
                            data=f,
                            file_name="guias_amarelas.zip",
                            mime="application/zip"
                        )
        except Exception as e:
            st.error(f"Erro ao executar o script: {e}")
        finally:
            if os.path.exists("inputs.txt"):
                os.remove("inputs.txt")
