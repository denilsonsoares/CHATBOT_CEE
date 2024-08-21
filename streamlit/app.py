import sys
import streamlit as st
import pandas as pd
import os
import openai
from utils import configure_genai, configure_openai, count_tokens_in_folder, process_files_and_save, calculate_cost
from resumir_stream import simplify
from add_keywords_stream import new_keywords
import plotly.express as px

# Configurar a página do Streamlit
st.set_page_config(
    page_title="Visualização de Dados de Vagas de Emprego",
    page_icon="icon.png",
    layout="wide",
)

st.markdown("""
    <style>
    /* Cor da barra lateral de navegação */
    [data-testid="stSidebar"] {
        background-color: #d23237;
    }

    /* Cor dos botões */
    .stButton>button {
        background-color: #d23237;
        color: white;
    }

    .stButton>button:hover {
        background-color: #b8282e;
        color: white;
    }

    /* Cor do texto e elementos na barra lateral */
    [data-testid="stSidebar"] * {
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)


# Diretório base do script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Título da Aplicação
st.title("Visualização e Extração de Dados de Vagas de Emprego")

# Barra Lateral para Navegação
st.sidebar.title("Navegação")
opcao = st.sidebar.selectbox("Escolha a aba:",
                             ["Visualização", "Extração de Dados", 'Simplificar Dados', 'Adicionar palavras-chave'])

# Aba de Visualização de Dados
if opcao == "Visualização":
    st.header("Visualização de Dados")

    def to_df(column, column_name):
        df = column.str.split(',').explode().str.strip().value_counts().reset_index()
        df.columns = [column_name, 'Contagem']
        return df

    # Seletor de arquivo na pasta dados_simplificados
    dados_simplificados_dir = os.path.join(base_dir, 'dados_simplificados')
    arquivo_selecionado = st.selectbox("Selecione o arquivo .xlsx para visualizar:", os.listdir(dados_simplificados_dir))

    if arquivo_selecionado:
        df_visualizacao = pd.read_excel(os.path.join(dados_simplificados_dir, arquivo_selecionado), engine='openpyxl')

        sub_opcao = st.selectbox("Escolha a sub-aba:",
                                 ["Áreas de Atuação", "Setores", "Requisitos", "Resumo", "Tabela", "Gráficos",
                                  "Benefícios", "Empresas"])

        if sub_opcao == "Áreas de Atuação":
            st.header("Distribuição por Áreas de Atuação")
            areas_de_atuacao = to_df(df_visualizacao['Áreas de Atuação'], 'Área')
            st.subheader('Áreas de Atuação mais comuns')
            areas_de_atuacao_comum = areas_de_atuacao.head(10)
            fig_area_comum = px.pie(areas_de_atuacao_comum, values='Contagem', names='Área')
            st.plotly_chart(fig_area_comum)
            st.subheader('Áreas de atuação menos comuns')
            areas_de_atuação_raro = areas_de_atuacao.tail(10)
            fig_area_raro = px.pie(areas_de_atuação_raro, values='Contagem', names='Área')
            st.plotly_chart(fig_area_raro)

        elif sub_opcao == "Setores":
            st.header("Distribuição por Setores")
            setores = to_df(df_visualizacao['Setor'], 'Setor')
            fig_setor = px.bar(setores, x='Setor', y='Contagem')
            st.plotly_chart(fig_setor)


        elif sub_opcao == "Requisitos":

            df_req_exploded = df_visualizacao.assign(Requisitos=df_visualizacao['Requisitos'].str.split(', ')).explode('Requisitos')
            requisito_count = df_req_exploded['Requisitos'].value_counts().reset_index()
            requisito_count.columns = ['Requisitos', 'Contagem']

            # adiciona um filtro de requisitos
            filtro = st.multiselect("Remover Requisitos da Análise", df_req_exploded['Requisitos'].unique())

            # remove os requisitos selecionados
            df_req_exploded = df_req_exploded[~df_req_exploded['Requisitos'].isin(filtro)]
            st.header("Requisitos por localidade")

            # adiciona input para o usuário escolher o número de requisitos a serem exibidos
            n_req = st.number_input("Número de Requisitos a serem exibidos", min_value=1, max_value=100, value=30)

            # Ordenar o df_req_exploded baseado na frequência dos requisitos
            df_req_exploded = df_req_exploded.merge(requisito_count, on='Requisitos').sort_values(by='Contagem', ascending=False)
            top_x_requisitos = df_req_exploded.groupby('Requisitos').head(n_req)
            top_x_requisitos_unicos = df_req_exploded['Requisitos'].value_counts().head(n_req).index
            df_req_exploded = df_req_exploded[df_req_exploded['Requisitos'].isin(top_x_requisitos_unicos)]

            df_req_exploded_arch = df_req_exploded.copy()

            comparacao = st.selectbox("Comparar por:", df_req_exploded.columns.drop('Requisitos'))
            if comparacao:
                lista_comparacao = st.selectbox("Comparar como lista:", df_req_exploded.columns.drop(['Requisitos', comparacao]))

            # pega apenas a comparação principal, caso seja lista
            df_req_exploded[comparacao] = df_req_exploded[comparacao].str.split(',').str[0].str.strip()

            # Contando as ocorrências de cada Requisito por Variavel de comparacao e adicionando a lista concatenada
            df_grouped = df_req_exploded.groupby(['Requisitos', comparacao]).agg(
                    Contagem=('Requisitos', 'size'),
                    ListaConcatenada=(lista_comparacao, lambda x: ', '.join(x.dropna().astype(str)))
                ).reset_index()

            # Criando o gráfico de barras empilhadas
            fig = px.bar(df_grouped,
                        x='Requisitos',
                        y='Contagem',
                        color=comparacao,
                        title="Contagem de Requisitos por " + comparacao,
                        labels={'Contagem':'Número de Vagas'},
                        barmode='stack',
                        hover_data="ListaConcatenada"
                        )

            fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig)

            st.dataframe(df_grouped)

            st.dataframe(df_req_exploded_arch)

        elif sub_opcao == "Resumo":
            st.subheader("Resumo dos Dados")
            st.write(df_visualizacao.describe())

        elif sub_opcao == "Tabela":
            st.subheader("Tabela de Dados")
            st.dataframe(df_visualizacao)

        elif sub_opcao == "Gráficos":
            st.subheader("Gráficos Genéricos")
            coluna_grafico = st.selectbox("Selecione a coluna para visualizar o gráfico:", df_visualizacao.columns)
            if df_visualizacao[coluna_grafico].dtype == 'object':
                contagem = df_visualizacao[coluna_grafico].str.split(',').explode().str.strip().value_counts()
                st.bar_chart(contagem)
            else:
                st.line_chart(df_visualizacao[coluna_grafico])

        elif sub_opcao == 'Benefícios':
            st.subheader('Benefícios mais comuns')
            beneficios = to_df(df_visualizacao['Benefícios'], 'Benefícios')
            beneficios_comuns = beneficios.head(10)
            fig_beneficios_comuns = px.pie(beneficios_comuns, names='Benefícios', values='Contagem')
            st.plotly_chart(fig_beneficios_comuns)
            st.subheader('Benefícios menos comuns')
            beneficios_raros = beneficios.tail(10)
            fig_beneficios_raros = px.pie(beneficios_raros, names='Benefícios', values='Contagem')
            st.plotly_chart(fig_beneficios_raros)

        elif sub_opcao == 'Empresas':
            st.header('Empresas mais comuns:')
            empresas = to_df(df_visualizacao['Empresa'], 'Empresa').head(10)
            fig_empresas = px.pie(empresas, names='Empresa', values='Contagem')
            st.plotly_chart(fig_empresas)

# Aba de Extração de Dados
elif opcao == "Extração de Dados":
    st.header("Extração de Dados")

    # Listar as pastas dentro da pasta "vagas"
    vagas_dir = os.path.join(base_dir, 'vagas')
    pasta_selecionada = st.selectbox("Selecione a pasta com os dados:", os.listdir(vagas_dir))
    modelo_selecionado = st.selectbox("Selecione o modelo:", ["gpt-3.5-turbo"])

    if st.button("Contar Tokens"):
        total_tokens = count_tokens_in_folder(os.path.join(vagas_dir, pasta_selecionada))
        st.write(f"Total de tokens necessários: {total_tokens}")

        custo = calculate_cost(total_tokens, modelo_selecionado)
        st.write(f"Custo estimado para o processamento: ${custo:.4f}")

    if st.button("Extrair Dados"):
        configure_genai(os.path.join(base_dir, 'gemini_api_key.txt'))
        configure_openai(os.path.join(base_dir, 'openai_api_key.txt'))
        total_tokens_usados, nome_arquivo_gerado = process_files_and_save(os.path.join(vagas_dir, pasta_selecionada),
                                                                          openai.api_key, modelo_selecionado)
        st.write(f"Total de tokens usados: {total_tokens_usados}")
        st.write(f"Arquivo gerado: {nome_arquivo_gerado}")

elif opcao == 'Simplificar Dados':
    st.header('Simplificação de Dados')

    # Seletor de arquivo na pasta dados_brutos
    dados_brutos_dir = os.path.join(base_dir, 'dados_brutos')
    arquivos_dados_brutos = os.listdir(dados_brutos_dir)

    if arquivos_dados_brutos:
        arquivo_selecionado = st.selectbox("Selecione o arquivo para simplificar:", arquivos_dados_brutos)

        if st.button("Simplificar Dados"):
            caminho_arquivo = os.path.join(dados_brutos_dir, arquivo_selecionado)
            df_simplificado = simplify(caminho_arquivo)

            # Salvar o arquivo simplificado na pasta dados_simplificados
            dados_simplificados_dir = os.path.join(base_dir, 'dados_simplificados')
            nome_arquivo_simplificado = f"{os.path.splitext(arquivo_selecionado)[0]}_simplificado.xlsx"
            caminho_arquivo_simplificado = os.path.join(dados_simplificados_dir, nome_arquivo_simplificado)
            df_simplificado.to_excel(caminho_arquivo_simplificado, index=False, engine='openpyxl')

            st.success(f"Arquivo simplificado salvo em: {caminho_arquivo_simplificado}")
    else:
        st.write("Nenhum arquivo encontrado na pasta 'dados_brutos'.")

elif opcao == 'Adicionar palavras-chave':
    keywords_df = pd.read_excel(os.path.join(base_dir, 'keywords_streamlit.xlsx'), engine='openpyxl')
    st.dataframe(keywords_df)
    st.header('Adicionar palavras-chave')

    column = st.selectbox('Digite a coluna que quer adicionar palavra-chave:', keywords_df.columns)
    new_key = st.text_input('Digite as novas palavras-chave:')

    if st.button('Adicionar palavras'):
        with open(os.path.join(base_dir, 'new_keys_file.txt'), 'w') as f:
            f.write(new_key)
        keywords_df = new_keywords(column, os.path.join(base_dir, 'new_keys_file.txt'), keywords_df)
        keywords_df.to_excel(os.path.join(base_dir, 'keywords_streamlit.xlsx'), index=False, engine='openpyxl')

# Rodapé da aplicação
st.sidebar.text("Aplicação de Visualização e Extração de Vagas de Emprego")
