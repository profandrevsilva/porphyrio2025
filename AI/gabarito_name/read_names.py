####################################
# Author: @andvsilva

# Description:
####################################

name_classe = 'names_1A'

import pandas as pd

# Load the Excel file
excel_file = f'classes_names/{name_classe}.xlsx'  # Replace with your file path
df = pd.read_excel(excel_file, sheet_name=0)  # You can specify the sheet name

# Save as CSV
csv_file = f'classes_names/{name_classe}.csv'  # Replace with desired CSV path
df.to_csv(csv_file, index=False)  # index=False removes the row numbers

df = pd.read_csv(f'classes_names/{name_classe}.csv', sep=',')

n = 8
df = df.iloc[n:]

df = df.drop(columns=['Relatório de Consulta de Fechamento', 
       'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7',
       'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11'])

df.columns = ['Situacao', 'Nome']

rm_names = ['Baixa - Transferência', 'Transferido', 'Remanejamento', 'Não Comparecimento']

for name in rm_names:
    df = df[df['Situacao'] != name]

print(df)
