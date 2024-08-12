TAREFAS:

Criar uma aplicação que recebe a descrição de uma vaga (em pdf, em .txt ou apenas em texto copiado e colado) e extraia as informações daquele texto e passe para uma planilha do excel. A princípio as colunas são:
Empresa
Vaga
Tipo
Requisitos
Remuneração

Ao longo do projeto vamos adicionando mais colunas e extraindo mais informações

Suponha que os arquivos que ele vai ler estão na mesma pasta que o arquivo main.py

Requisitos iniciais:

pip install openai pandas PyPDF2 openpyxl langchain tiktoken

pip install -U langchain-openai


Modificar a função de extrair texto da imagem:
 - Função: extract_text_from_image;
 - Caso os tokens da chave da api do gemini esgote, utilizar outra chave de outro email no código(ele deve mudar automaticamente
durante a execução e perceber se esgotou, ou para cada 5 imagens lidas mudar a chave);
 - É interessante ter pelo menos 3 chaves do gemini(de três emails diferentes) para extrair os dados
das imagens, pois é esperado pelo menos 15 imagens dentre os arquivos;

Simplificações(deixar o mais simplificado possível cada coluna):
 - Localidade: Deixar a penas Remoto/Presencial/Híbrido/Local especificado/ - (em branco se não informado); 
 - Requisitos: buscar apenas as palavras chaves(Python, Excel, Inglês Fluente/Avaçado, Proatividade ...);
 - Dividir a coluna de remuneração em Remuneração e Benefícios: requisitos deixar apenas o valor bruto ou a Combinar/
benefícios: texto completo explicando;
 - Destinatários: pegar apenas as palavras chaves/ ano de formação/semestre atual/curso;

Essa simplificação deve ser feita a princípio sem a api do chatgpt, vamos utilizar um banco de dados que vai identificar as
palavras esperadas para cada requisito e tentar deixar apenas a palavra chave.
Por exemplo:
Requisitos: Experiência com programação em Python -> deixar apenas "Python"

