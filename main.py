import os
import openai
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import time
import tiktoken

# Função para ler a chave da API do Gemini e do OpenAI do arquivo .txt
def get_api_key(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

# Configuração da API do Gemini
genai.configure(api_key=get_api_key('gemini_api_key.txt'))

# Configuração da API do OpenAI
openai_api_key = get_api_key('openai_api_key2.txt')
openai.api_key = openai_api_key

# Função para extrair texto de PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para extrair texto de arquivos .docx
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Função para extrair texto de imagens usando a API do Gemini
def extract_text_from_image(file_path):
    img = Image.open(file_path)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(img)
    return response.text

# Função para extrair texto de arquivos PDF, TXT, DOCX e imagens
def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return extract_text_from_image(file_path)
    else:
        return ''

# Função para contar tokens usando a biblioteca tiktoken
def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    return len(tokens)

# Função para extrair informações da vaga usando LangChain
def extract_job_info(text):
    template = """
        Extraia as seguintes informações do texto da vaga de estágio. Forneça respostas curtas e objetivas 
        apenas com as palavras-chave de cada campo:
        Empresa, Vaga, Localidade, Requisitos, Remuneração, Carga Horária, Benefícios, Destinatários, Áreas de Atuação, Responsabilidades.
        Texto: {text}
        Informações extraídas:
        """
    prompt = PromptTemplate(input_variables=["text"], template=template)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)
    chain = LLMChain(prompt=prompt, llm=llm)
    result = chain.run(text)
    return result.strip()

def main():
    columns = ['Empresa', 'Vaga', 'Localidade', 'Requisitos', 'Remuneração', 'Carga Horária', 'Benefícios', 'Destinatários', 'Áreas de Atuação', 'Responsabilidades', 'Nome do Arquivo']
    data = []
    folder_path = './VAGAS_125'
    total_tokens_used = 0
    token_limit_per_minute = 200000
    token_limit_per_day = 2000000
    start_time = time.time()

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_path.endswith(('.pdf', '.txt', '.docx', '.png', '.jpg', '.jpeg')):
            text = extract_text_from_file(file_path)
            if text:
                num_tokens = count_tokens(text)
                if total_tokens_used + num_tokens > token_limit_per_day:
                    print(f'Limite diário de tokens excedido ao processar {file_name}. Salvando dados parciais.')
                    break

                if total_tokens_used + num_tokens > token_limit_per_minute:
                    elapsed_time = time.time() - start_time
                    if elapsed_time < 60:
                        time.sleep(60 - elapsed_time)
                    start_time = time.time()

                job_info = extract_job_info(text)
                job_info_list = job_info.split('\n')
                extracted_info = []
                for info in columns[:-1]:  # Ignorar 'Nome do Arquivo' na extração de dados
                    found = False
                    for line in job_info_list:
                        if line.startswith(info):
                            extracted_info.append(line.split(':', 1)[1].strip())
                            found = True
                            break
                    if not found:
                        extracted_info.append('')
                extracted_info.append(file_name)  # Adicionar nome do arquivo
                data.append(extracted_info)
                total_tokens_used += num_tokens
                print(f'{file_name} processado com sucesso.')

    df = pd.DataFrame(data, columns=columns)
    df.to_excel('job_info_gpt3_125.xlsx', index=False)
    print(f'Total de tokens usados: {total_tokens_used}')

if __name__ == '__main__':
    main()
