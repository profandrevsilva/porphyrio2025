####################################
# Author: @andvsilva

# Description:
####################################
import pandas as pd

name_classes  = ['names_1A', 'names_1B', 'names_1C', 'names_1D', 'names_1E', 'names_1F', 'names_1G']

for name_classe in name_classes:
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

    df = df.drop(columns=['Situacao'])

    print(df)

    name_classe = 'final_' + name_classe

    df.to_csv(f'classes_names/{name_classe}.csv', index=False)
