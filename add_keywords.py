import pandas as pd

# Carregar o arquivo Excel
df = pd.read_excel('keywords.xlsx', engine='openpyxl')

# Palavra-chave principal
palavra_principal = "Educação"

# Substituir NaN por string vazia para evitar erros na busca
df['Subs_Areas'] = df['Subs_Areas'].fillna('')

# Ler as palavras-chave adicionais do arquivo .txt com codificação UTF-8
with open('palavras_chave.txt', 'r', encoding='utf-8') as file:
    novas_palavras = file.read().strip().split(',')

# Localizar a linha onde a palavra-chave principal é a primeira palavra
linha_index = df[df['Subs_Areas'].str.split(',').str[0].str.strip().str.lower() == palavra_principal.lower()].index[0]

# Obter o conteúdo existente
conteudo_atual = df.at[linha_index, 'Subs_Areas']

# Agregar as novas palavras-chave ao final
palavras_existentes = conteudo_atual.split(',')
palavras_existentes.extend(novas_palavras)

# Remover duplicatas mantendo a ordem e atualizar a célula com as palavras-chave agregadas
df.at[linha_index, 'Subs_Areas'] = ','.join(dict.fromkeys(palavras_existentes))

# Verificar todas as linhas e remover duplicatas
for index, row in df.iterrows():
    palavras = row['Subs_Areas'].split(',')
    palavras_unicas = list(dict.fromkeys([palavra.strip() for palavra in palavras if palavra.strip()]))
    df.at[index, 'Subs_Areas'] = ', '.join(palavras_unicas)

# Salvar o arquivo Excel atualizado
df.to_excel('keywords.xlsx', index=False, engine='openpyxl')
