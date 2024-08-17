import pandas as pd
def new_keywords(column,file,keywords_df):

    # Substituir NaN por string vazia para evitar erros na busca
    keywords_df[column] = keywords_df[column].fillna('')

    # Ler as palavras-chave adicionais do arquivo .txt com codificação UTF-8
    with open(file, 'r') as file:
        novas_palavras = file.read().strip().split(',')
    palavra_principal=novas_palavras[0]
    # Localizar a linha onde a palavra-chave principal é a primeira palavra
    linha_index = keywords_df[keywords_df[column].str.split(',').str[0].str.strip().str.lower() == palavra_principal.lower()].index[0]

    # Obter o conteúdo existente
    conteudo_atual = keywords_df.at[linha_index, column]

    # Agregar as novas palavras-chave ao final
    palavras_existentes = conteudo_atual.split(',')
    palavras_existentes.extend(novas_palavras)

    # Remover duplicatas mantendo a ordem e atualizar a célula com as palavras-chave agregadas
    keywords_df.at[linha_index, column] = ','.join(dict.fromkeys(palavras_existentes))

    # Verificar todas as linhas e remover duplicatas
    for index, row in keywords_df.iterrows():
        palavras = row[column].split(',')
        palavras_unicas = list(dict.fromkeys([palavra.strip() for palavra in palavras if palavra.strip()]))
        keywords_df.at[index, column] = ', '.join(palavras_unicas)

    return keywords_df
