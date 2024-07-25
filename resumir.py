import pandas as pd

# Carregar a planilha de entrada
input_file = 'job_info.xlsx'
df = pd.read_excel(input_file)

# Carregar o arquivo de palavras-chave
keywords_file = 'keywords.xlsx'
keywords_df = pd.read_excel(keywords_file)

# Converter as colunas do DataFrame em listas
keywords = {
    'Localidade': keywords_df['Localidade'].dropna().tolist(),
    'Requisitos': keywords_df['Requisitos'].dropna().tolist(),
    'Destinatários': keywords_df['Destinatários'].dropna().tolist()
}

# Função para simplificar a localidade
def simplify_localidade(localidade):
    if pd.isna(localidade) or localidade.lower() in ['não mencionado', 'não mencionada', 'não informado',
                                                     'não informada', 'não especificado', 'não especificada', '']:
        return 'Não mencionado'
    for keyword in keywords['Localidade']:
        if keyword.lower() in localidade.lower():
            return keyword
    return localidade

# Função para simplificar os requisitos
def simplify_requisitos(requisitos):
    if pd.isna(requisitos):
        return ''
    simplified = []
    for keyword in keywords['Requisitos']:
        if keyword.lower() in requisitos.lower():
            simplified.append(keyword)
    return ', '.join(simplified)

# Função para dividir a coluna de remuneração
def split_remuneracao(remuneracao):
    if pd.isna(remuneracao):
        return '', ''
    parts = remuneracao.split('/')
    return parts[0].strip(), '/'.join(parts[1:]).strip() if len(parts) > 1 else ''

# Função para simplificar os destinatários
def simplify_destinatarios(destinatarios):
    if pd.isna(destinatarios):
        return ''
    simplified = []
    for keyword in keywords['Destinatários']:
        if keyword.lower() in destinatarios.lower():
            simplified.append(keyword)
    return ', '.join(simplified)

# Aplicar simplificações
df['Localidade'] = df['Localidade'].apply(simplify_localidade)
df['Requisitos'] = df['Requisitos'].apply(simplify_requisitos)
df['Remuneração'], df['Benefícios'] = zip(*df['Remuneração'].apply(split_remuneracao))
df['Destinatários'] = df['Destinatários'].apply(simplify_destinatarios)

# Salvar o resultado em um novo arquivo
output_file = 'simplified_job_info.xlsx'
df.to_excel(output_file, index=False)
