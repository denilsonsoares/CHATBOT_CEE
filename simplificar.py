import openai
import pandas as pd
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

def get_api_key(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

# Configuração da API do OpenAI
openai_api_key = get_api_key('openai_api_key.txt')

# Defina a classe para simplificação
class SimplifyPromptTemplate(PromptTemplate):
    def __init__(self):
        super().__init__(input_variables=["text"], template="Deixe apenas as palavras chaves do texto:\n\n{text}")

# Configure o LLM com LangChain
llm = OpenAI(openai_api_key=openai_api_key)  # Passe a chave da API corretamente

# Configure o template de prompt
template = SimplifyPromptTemplate()

# Configure a chain para o LLM
chain = LLMChain(llm=llm, prompt=template)

# Carregar a planilha
planilha = pd.read_excel('job_info.xlsx')

# Selecionar as colunas que deseja simplificar
colunas_para_simplificar = ['Requisitos']  # Substitua com as colunas desejadas

# Função para simplificar o texto utilizando LangChain, apenas nas colunas selecionadas
def simplificar_texto(texto):
    response = chain.run({"text": texto})
    return response.strip()

# Simplificar apenas as colunas selecionadas na planilha
for coluna in colunas_para_simplificar:
    if coluna in planilha.columns:
        planilha[coluna] = planilha[coluna].apply(simplificar_texto)

# Salvar a planilha simplificada
planilha.to_excel('job_info_simplificada.xlsx', index=False)

print("Planilha simplificada salva como job_info_simplificada.xlsx")
