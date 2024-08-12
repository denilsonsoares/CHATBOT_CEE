import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Carregar o arquivo Excel
df = pd.read_excel('simplified_job_info_gpt3_125.xlsx', engine='openpyxl')

# Título da Aplicação
st.title("Visualização de Dados de Vagas de Emprego")

# Barra Lateral para Navegação
st.sidebar.title("Navegação")
opcao = st.sidebar.selectbox("Escolha o gráfico:", ["Áreas de Atuação", "Setores", "Remuneração", "Requisitos"])

# Gráfico de Distribuição por Áreas de Atuação
if opcao == "Áreas de Atuação":
    st.header("Distribuição por Áreas de Atuação")
    areas_de_atuacao = df['Áreas de Atuação'].str.split(',').explode().str.strip().value_counts()
    st.bar_chart(areas_de_atuacao)

# Gráfico de Distribuição por Setores
elif opcao == "Setores":
    st.header("Distribuição por Setores")
    setores = df['Setor'].str.split(',').explode().str.strip().value_counts()
    st.bar_chart(setores)

# Gráfico de Distribuição de Remuneração
elif opcao == "Remuneração":
    st.header("Distribuição de Remuneração")
    remuneracao = df['Remuneração'].value_counts()
    st.bar_chart(remuneracao)

# Gráfico de Requisitos mais Comuns
elif opcao == "Requisitos":
    st.header("Requisitos mais Comuns")
    requisitos = df['Requisitos'].str.split(',').explode().str.strip().value_counts().head(20)  # Mostra os 20 principais
    st.bar_chart(requisitos)

# Rodapé da aplicação
st.sidebar.text("Aplicação de Visualização de Vagas de Emprego")
