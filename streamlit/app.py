import streamlit as st
import pandas as pd
import os
import openai
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
                             ["Visualização", "Extração de Dados"])

# Aba de Visualização de Dados
if opcao == "Visualização":
    st.header("Visualização de Dados")

    # Seletor de arquivo na pasta dados_simplificados
    arquivo_selecionado = st.selectbox("Selecione o arquivo .xlsx para visualizar:", os.listdir('dados_simplificados'))

    if arquivo_selecionado:
        df_visualizacao = pd.read_excel(os.path.join('dados_simplificados', arquivo_selecionado), engine='openpyxl')

        sub_opcao = st.selectbox("Escolha a sub-aba:",
                                 ["Áreas de Atuação", "Setores", "Requisitos", "Resumo", "Tabela", "Gráficos"])

        if sub_opcao == "Áreas de Atuação":
            st.header("Distribuição por Áreas de Atuação")
            areas_de_atuacao = df_visualizacao['Áreas de Atuação'].str.split(',').explode().str.strip().value_counts()
            st.bar_chart(areas_de_atuacao)

        elif sub_opcao == "Setores":
            st.header("Distribuição por Setores")
            setores = df_visualizacao['Setor'].str.split(',').explode().str.strip().value_counts()
            st.bar_chart(setores)

        elif sub_opcao == "Requisitos":
            st.header("Requisitos mais Comuns")
            requisitos = df_visualizacao['Requisitos'].str.split(',').explode().str.strip().value_counts().head(20)
            st.bar_chart(requisitos)

        elif sub_opcao == "Resumo":
            st.subheader("Resumo dos Dados")
            st.write(df_visualizacao.describe())

        elif sub_opcao == "Tabela":
            st.subheader("Tabela de Dados")
            st.dataframe(df_visualizacao)

        elif sub_opcao == "Gráficos Genéricos":
            st.subheader("Gráficos")
            coluna_grafico = st.selectbox("Selecione a coluna para visualizar o gráfico:", df_visualizacao.columns)
            if df_visualizacao[coluna_grafico].dtype == 'object':
                contagem = df_visualizacao[coluna_grafico].str.split(',').explode().str.strip().value_counts()
                st.bar_chart(contagem)
            else:
                st.line_chart(df_visualizacao[coluna_grafico])

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
