import pandas as pd
import re

# Carregar a planilha de entrada
input_file = 'job_info_gpt3.xlsx'
df = pd.read_excel(input_file)

# Carregar o arquivo de palavras-chave
keywords_file = 'keywords.xlsx'
keywords_df = pd.read_excel(keywords_file)

# Converter as colunas do DataFrame em listas
keywords = {
    'Localidade': keywords_df['Localidade'].dropna().tolist(),
    'Requisitos': keywords_df['Requisitos'].dropna().tolist(),
    'Destinatários': keywords_df['Destinatários'].dropna().tolist(),
    'Carga Horária': keywords_df['Carga Horária'].dropna().tolist()
}

# Função para simplificar a localidade
def simplify_localidade(localidade):
    if pd.isna(localidade) or localidade.lower() in ['não mencionado', 'não mencionada', 'não informado',
                                                     'não informada', 'não especificado', 'não especificada', '']:
        return 'Não especificada'
    for keyword in keywords['Localidade']:
        if keyword.lower() in localidade.lower():
            return keyword
    return localidade

# Função para simplificar os requisitos
def simplify_requisitos(requisitos):
    if pd.isna(requisitos):
        return 'Não especificado'
    simplified = []
    for keyword in keywords['Requisitos']:
        if keyword.lower() in requisitos.lower():
            simplified.append(keyword)
    return ', '.join(simplified)

# Função para simplificar os destinatários
def simplify_destinatarios(destinatarios):
    if pd.isna(destinatarios):
        return ''
    if not isinstance(destinatarios, str):
        return 'Não mencionado'
    simplified = []
    for keyword in keywords['Destinatários']:
        if keyword.lower() in destinatarios.lower():
            simplified.append(keyword)
    return ', '.join(simplified)

# Função para simplificar a carga horária
def simplify_carga_horaria(carga_horaria):
    if pd.isna(carga_horaria) or carga_horaria.lower() in ['não mencionada', 'não mencionado', 'não informado', 'não informada']:
        return 'Não especificada'
    for keyword in keywords['Carga Horária']:
        if keyword.lower() in carga_horaria.lower():
            return keyword
    return carga_horaria

# Função para simplificar a coluna de remuneração
def simplify_remuneracao(remuneracao):
    if pd.isna(remuneracao) or remuneracao.lower() in ['a combinar', 'não especificada', 'não especificado']:
        return 'A combinar'

    # Expressões regulares para identificar valores monetários
    value_pattern = re.compile(r'(\d+\.?\d*\,?\d*)')

    # Extrair valores monetários
    values = value_pattern.findall(remuneracao.replace('.', '').replace(',', '.'))

    if values:
        # Converter valores para float
        values = [float(value.replace(',', '.')) for value in values]
        # Identificar o valor mais alto
        highest_value = max(values)
        # Formatar o valor mais alto
        return f"R$ {highest_value:,.2f}".replace(',', '.')

    return 'A combinar'

# Aplicar simplificações
df['Localidade'] = df['Localidade'].apply(simplify_localidade)
df['Requisitos'] = df['Requisitos'].apply(simplify_requisitos)
df['Remuneração'] = df['Remuneração'].apply(simplify_remuneracao)
df['Destinatários'] = df['Destinatários'].apply(simplify_destinatarios)
df['Carga Horária'] = df['Carga Horária'].apply(simplify_carga_horaria)

# Salvar o resultado em um novo arquivo
output_file = 'simplified_job_info_gpt3.xlsx'
df.to_excel(output_file, index=False)
