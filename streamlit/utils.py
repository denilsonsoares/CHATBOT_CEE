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
from transformers import GPT2Tokenizer

# Função para ler a chave da API do Gemini e do OpenAI do arquivo .txt
def get_api_key(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

# Configuração da API do Gemini
def configure_genai(api_key_file):
    api_key = get_api_key(api_key_file)
    genai.configure(api_key=api_key)

# Configuração da API do OpenAI
def configure_openai(api_key_file):
    openai.api_key = get_api_key(api_key_file)

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

# Função para contar tokens em todos os arquivos de uma pasta
def count_tokens_in_folder(folder_path):
    total_tokens = 0
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_path.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            total_tokens += count_tokens(text)
    return total_tokens

# Função para extrair informações da vaga usando LangChain
def extract_job_info(text, openai_api_key, model_name="gpt-3.5-turbo"):
    template = """
        Extraia as seguintes informações do texto da vaga de estágio. Forneça respostas curtas e objetivas 
        apenas com as palavras-chave de cada campo:
        Empresa, Vaga, Localidade, Requisitos, Remuneração, Carga Horária, Benefícios, Curso, Semestre/Previsão de Formatura, Áreas de Atuação, Responsabilidades.
        Texto: {text}
        Informações extraídas:
        """
    prompt = PromptTemplate(input_variables=["text"], template=template)
    llm = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key)
    chain = LLMChain(prompt=prompt, llm=llm)
    result = chain.run(text)
    return result.strip()

# Função para processar os arquivos e salvar os resultados
def process_files_and_save(folder_path, openai_api_key, model_name="gpt-3.5-turbo"):
    columns = ['Empresa', 'Vaga', 'Localidade', 'Requisitos', 'Remuneração', 'Carga Horária', 'Benefícios', 'Curso', 'Semestre/Previsão de Formatura', 'Áreas de Atuação', 'Responsabilidades', 'Nome do Arquivo']
    data = []
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
                    break

                if total_tokens_used + num_tokens > token_limit_per_minute:
                    elapsed_time = time.time() - start_time
                    if elapsed_time < 60:
                        time.sleep(60 - elapsed_time)
                    start_time = time.time()

                job_info = extract_job_info(text, openai_api_key, model_name)
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

    df = pd.DataFrame(data, columns=columns)
    output_filename = f"job_info__modelo_{len(os.listdir(folder_path))}.xlsx"
    output_path = os.path.join('dados_brutos', output_filename)
    df.to_excel(output_path, index=False)
    return total_tokens_used, output_filename
