import os
from PyPDF2 import PdfReader
from transformers import GPT2Tokenizer

# Função para ler texto de um arquivo PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para contar tokens em um texto usando o tokenizador GPT-2
def count_tokens(text):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokens = tokenizer.encode(text)
    return len(tokens)

# Função principal para contar tokens em todos os arquivos PDF em uma pasta
def main():
    folder_path = './VAGAS_75'
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    total_tokens = 0

    for file_name in pdf_files:
        file_path = os.path.join(folder_path, file_name)
        text = extract_text_from_pdf(file_path)
        num_tokens = count_tokens(text)
        #print(f'O arquivo {file_name} possui {num_tokens} tokens.')
        total_tokens += num_tokens

    print(f'Total de tokens em todos os arquivos PDF: {total_tokens}')

if __name__ == '__main__':
    main()
