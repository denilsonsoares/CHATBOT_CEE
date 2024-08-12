import pandas as pd

# Carregar o arquivo Excel
df = pd.read_excel('keywords.xlsx', engine='openpyxl')

# Palavra-chave principal
palavra_principal = "Consultoria"

# Substituir NaN por string vazia para evitar erros na busca
df['Subs_Areas'] = df['Subs_Areas'].fillna('')

# Ler as palavras-chave adicionais do arquivo .txt com codificação UTF-8
with open('palavras_chave.txt', 'r', encoding='utf-8') as file:
    novas_palavras = file.read().strip().split(',')

# Localizar a linha correspondente à palavra-chave principal
linha_index = df[df['Subs_Areas'].str.contains(palavra_principal, case=False)].index[0]

# Obter o conteúdo existente
conteudo_atual = df.at[linha_index, 'Subs_Areas']

# Agregar as novas palavras-chave ao final
palavras_existentes = conteudo_atual.split(',')
palavras_existentes.extend(novas_palavras)

# Remover duplicatas mantendo a ordem e atualizar a célula com as palavras-chave agregadas
df.at[linha_index, 'Subs_Areas'] = ','.join(dict.fromkeys(palavras_existentes))

# Salvar o arquivo Excel atualizado
df.to_excel('keywords_atualizado.xlsx', index=False, engine='openpyxl')
