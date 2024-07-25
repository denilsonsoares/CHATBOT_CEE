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

# Função para ler a chave da API do Gemini e do OpenAI do arquivo .txt
def get_api_key(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

# Configuração da API do Gemini
genai.configure(api_key=get_api_key('gemini_api_key.txt'))

# Configuração da API do OpenAI
openai_api_key = get_api_key('openai_api_key.txt')

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

# Função para extrair informações da vaga usando LangChain
def extract_job_info(text):
    template = """
        Extraia as seguintes informações do texto da vaga de estágio. Forneça respostas curtas e objetivas 
        apenas com as palavras-chave de cada campo:
        Empresa, Vaga, Localidade, Requisitos, Remuneração, Destinatários, Áreas de Atuação, Responsabilidades.
        Texto: {text}
        Informações extraídas:
        """
    prompt = PromptTemplate(input_variables=["text"], template=template)
    llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)
    chain = LLMChain(prompt=prompt, llm=llm)
    result = chain.run(text)
    return result.strip()

def main():
    columns = ['Empresa', 'Vaga', 'Localidade', 'Requisitos', 'Remuneração', 'Destinatários', 'Áreas de Atuação', 'Responsabilidades']
    data = []
    folder_path = './VAGAS'

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_path.endswith(('.pdf', '.txt', '.docx', '.png', '.jpg', '.jpeg')):
            text = extract_text_from_file(file_path)
            if text:
                job_info = extract_job_info(text)
                job_info_list = job_info.split('\n')
                extracted_info = []
                for info in columns:
                    found = False
                    for line in job_info_list:
                        if line.startswith(info):
                            extracted_info.append(line.split(':', 1)[1].strip())
                            found = True
                            break
                    if not found:
                        extracted_info.append('')
                data.append(extracted_info)

    df = pd.DataFrame(data, columns=columns)
    df.to_excel('job_info.xlsx', index=False)

if __name__ == '__main__':
    main()
