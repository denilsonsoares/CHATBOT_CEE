import pandas as pd
import re

# Carregar a planilha de entrada
input_file = 'job_info_gpt3_50.xlsx'
df = pd.read_excel(input_file)

# Carregar o arquivo de palavras-chave
keywords_file = 'keywords.xlsx'
keywords_df = pd.read_excel(keywords_file)
print(keywords_df.columns)
# Converter as colunas do DataFrame em listas
keywords = {
    'Localidade': keywords_df['Localidade'].dropna().tolist(),
    'Requisitos': keywords_df['Requisitos'].dropna().tolist(),
    'Destinatários': keywords_df['Destinatários'].dropna().tolist(),
    'Categorias Carga Horária': keywords_df['Categorias Carga Horária'].dropna().tolist(),
    'Benefícios':keywords_df['Subs_Benefícios'].dropna().tolist()
}

# Carregar mapeamento de substituição de palavras para os requisitos
requisitos_map = {}
if 'Substituicoes' in keywords_df:
    substitutions = keywords_df['Substituicoes'].dropna().tolist()
    for item in substitutions:
        original, replacement = item.split(',')
        requisitos_map[original.strip()] = replacement.strip()

#Carregar substituições de Benefícios
benefícios_map={}
if 'Subs_Benefícios' in keywords_df:
    bene_substitutions=keywords_df['Subs_Benefícios'].dropna().tolist()
    for item in bene_substitutions:
        parts_bene=item.split(',')
        replacement_bene=parts_bene[0].strip().lower()
        for term in parts_bene[1:]:
            benefícios_map[term.strip().lower()]=replacement_bene


# Carregar categorias de carga horária
carga_horaria_map = {}
if 'Categorias Carga Horária' in keywords_df:
    categorias = keywords_df['Categorias Carga Horária'].dropna().tolist()
    for item in categorias:
        parts = item.split(',')
        main_category = parts[0].strip().lower()
        for term in parts[1:]:
            carga_horaria_map[term.strip().lower()] = main_category

# Função para simplificar a localidade
def simplify_localidade(localidade):
    if pd.isna(localidade) or localidade.lower() in ['não mencionado', 'não mencionada', 'não informado',
                                                     'não informada', 'não especificado', 'não especificada', '']:
        return 'Não especificada'
    for keyword in keywords['Localidade']:
        if re.search(r'\b' + re.escape(keyword) + r'\b', localidade, re.IGNORECASE):
            return keyword
    return localidade

# Função para simplificar os requisitos
def simplify_requisitos(requisitos):
    if pd.isna(requisitos):
        return 'Não especificado'
    simplified = set()  # Usar set para evitar duplicatas
    for keyword in keywords['Requisitos']:
        if re.search(r'\b' + re.escape(keyword) + r'\b', requisitos, re.IGNORECASE):
            simplified.add(keyword)
    for original, replacement in requisitos_map.items():
        if re.search(r'\b' + re.escape(original) + r'\b', requisitos, re.IGNORECASE):
            simplified.add(replacement)
    return ', '.join(sorted(simplified))  # Ordenar a lista e juntar os elementos

# Função para simplificar os destinatários
def simplify_destinatarios(destinatarios):
    if pd.isna(destinatarios):
        return ''
    if not isinstance(destinatarios, str):
        return 'Não mencionado'
    simplified = set()
    for keyword in keywords['Destinatários']:
        if re.search(r'\b' + re.escape(keyword) + r'\b', destinatarios, re.IGNORECASE):
            simplified.add(keyword)
    return ', '.join(sorted(simplified))

# Função para simplificar a carga horária
def simplify_carga_horaria(carga_horaria):
    if pd.isna(carga_horaria) or carga_horaria.lower() in ['não mencionado', 'não mencionada', 'não informado',
                                                           'não informada', 'não especificada']:
        return 'Não especificada'

    carga_horaria_lower = carga_horaria.lower()
    for term, category in carga_horaria_map.items():
        if re.search(r'\b' + re.escape(term) + r'\b', carga_horaria_lower):
            return category

    # Se nenhum termo específico foi encontrado, retornar 'Não especificada'
    return 'Não especificada'

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


def simplify_benefícios(benefícios):
    if pd.isna(benefícios):
        return 'Não especificado'
    simplified=set()
    for keyword in keywords['Benefícios']:
        if re.search(r'\b'+re.escape(keyword)+r'\b', benefícios, re.IGNORECASE):
            simplified.add(keyword)
    for original,replacement in benefícios_map.items():
        if re.search(r'\b'+re.escape(original)+r'\b',benefícios,re.IGNORECASE):
            simplified.add(replacement)

    return ', '.join(sorted(simplified))





# Aplicar simplificações
df['Localidade'] = df['Localidade'].apply(simplify_localidade)
df['Requisitos'] = df['Requisitos'].apply(simplify_requisitos)
df['Remuneração'] = df['Remuneração'].apply(simplify_remuneracao)
df['Destinatários'] = df['Destinatários'].apply(simplify_destinatarios)
df['Carga Horária'] = df['Carga Horária'].apply(simplify_carga_horaria)
df['Benefícios']=df['Benefícios'].apply(simplify_benefícios)

# Salvar o resultado em um novo arquivo
output_file = 'simplified_job_info_gpt3_50_att.xlsx'
df.to_excel(output_file, index=False)
