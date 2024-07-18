import os
import openai
import pandas as pd
from PyPDF2 import PdfReader
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Função para ler a chave da API do arquivo .txt
def get_api_key():
    with open('api_key.txt', 'r') as file:
        return file.read().strip()

# Configuração da API do OpenAI
api_key = get_api_key()

# Função para extrair texto de PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para extrair texto de arquivos PDF e TXT
def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return ''

# Função para extrair informações da vaga usando LangChain
def extract_job_info(text):
    template = """
    Extraia as seguintes informações do texto da vaga de estágio: Empresa, Vaga, Localidade, Requisitos, Remuneração.
    Texto: {text}
    Informações extraídas:
    """
    prompt = PromptTemplate(input_variables=["text"], template=template)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key)
    chain = LLMChain(prompt=prompt, llm=llm)
    result = chain.run(text)
    return result.strip()

def main():
    columns = ['Empresa', 'Vaga', 'Localidade', 'Requisitos', 'Remuneração']
    data = []
    folder_path = './VAGAS'

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_path.endswith('.pdf') or file_path.endswith('.txt'):
            text = extract_text_from_file(file_path)
            if text:
                job_info = extract_job_info(text)
                job_info_list = job_info.split('\n')
                data.append([info.split(':')[1].strip() for info in job_info_list if ':' in info])

    df = pd.DataFrame(data, columns=columns)
    df.to_excel('job_info.xlsx', index=False)

if __name__ == '__main__':
    main()
