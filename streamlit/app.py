# app.py
import streamlit as st
import pandas as pd
import os
import openai  # Importar a biblioteca openai
from utils import configure_genai, configure_openai, count_tokens_in_folder, process_files_and_save, calculate_cost

# Configurar a página do Streamlit
st.set_page_config(
    page_title="Visualização de Dados de Vagas de Emprego",
    page_icon="icon.png",
    layout="wide",
)

# Título da Aplicação
st.title("Visualização e Extração de Dados de Vagas de Emprego")

# Barra Lateral para Navegação
st.sidebar.title("Navegação")
opcao = st.sidebar.selectbox("Escolha a aba:",
                             ["Áreas de Atuação", "Setores", "Remuneração", "Requisitos", "Extração de Dados"])

# Carregar os dados da planilha
df = pd.read_excel('dados/simplified_job_info_gpt3_125.xlsx', engine='openpyxl')

# Aba de Gráficos
if opcao in ["Áreas de Atuação", "Setores", "Remuneração", "Requisitos"]:
    if opcao == "Áreas de Atuação":
        st.header("Distribuição por Áreas de Atuação")
        areas_de_atuacao = df['Áreas de Atuação'].str.split(',').explode().str.strip().value_counts()
        st.bar_chart(areas_de_atuacao)

    elif opcao == "Setores":
        st.header("Distribuição por Setores")
        setores = df['Setor'].str.split(',').explode().str.strip().value_counts()
        st.bar_chart(setores)

    elif opcao == "Remuneração":
        st.header("Distribuição de Remuneração")
        remuneracao = df['Remuneração'].str.replace('R\$', '').str.replace(',', '').astype(float)
        st.hist_chart(remuneracao)

    elif opcao == "Requisitos":
        st.header("Requisitos mais Comuns")
        requisitos = df['Requisitos'].str.split(',').explode().str.strip().value_counts().head(20)
        st.bar_chart(requisitos)

# Aba de Extração de Dados
elif opcao == "Extração de Dados":
    st.header("Extração de Dados")

    # Listar as pastas dentro da pasta "vagas"
    pasta_selecionada = st.selectbox("Selecione a pasta com os dados:", os.listdir('vagas'))
    modelo_selecionado = st.selectbox("Selecione o modelo:", ["gpt-3.5-turbo"])

    if st.button("Contar Tokens"):
        total_tokens = count_tokens_in_folder(os.path.join('vagas', pasta_selecionada))
        st.write(f"Total de tokens necessários: {total_tokens}")

        # Calcular e exibir o custo
        custo = calculate_cost(total_tokens, modelo_selecionado)
        st.write(f"Custo estimado para o processamento: ${custo:.4f}")

    if st.button("Extrair Dados"):
        configure_genai('gemini_api_key.txt')
        configure_openai('openai_api_key2.txt')
        total_tokens_usados, nome_arquivo_gerado = process_files_and_save(os.path.join('vagas', pasta_selecionada),
                                                                          openai.api_key, modelo_selecionado)
        st.write(f"Total de tokens usados: {total_tokens_usados}")
        st.write(f"Arquivo gerado: {nome_arquivo_gerado}")


# Rodapé da aplicação
st.sidebar.text("Aplicação de Visualização e Extração de Vagas de Emprego")