###########################################################################
# Author: Andre Silva seg 29 set 2025 18:26:35
# github: https://github.com/andvsilva
# Description: This code reads the Excel file and saves it as a CSV file.
# This already remove students that are not in the classes.
###########################################################################
import pandas as pd
import os
import time

# Get start time 
start_time = time.time()

name_classes  = ['names_1A', 
                 'names_1B', 
                 'names_1C', 
                 'names_1D', 
                 'names_1E', 
                 'names_1F', 
                 'names_1G']

# path to folders: csv and xlsx
path_folder_csv = 'csv/'

for name_classe in name_classes:
    print(f'READING NAMES >>> Class: {name_classe}')
    # Load the Excel file
    excel_file = f'{name_classe}.xlsx'  # Replace with your file path
    df = pd.read_excel(excel_file, sheet_name=0)  # You can specify the sheet name

    # Save as CSV
    csv_file = f'{path_folder_csv}/{name_classe}.csv'  # Replace with desired CSV path
    df.to_csv(csv_file, index=False)  # index=False removes the row numbers

    df = pd.read_csv(f'{path_folder_csv}/{name_classe}.csv', sep=',')

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

    # remove csv
    os.remove(f'{path_folder_csv}/{name_classe}.csv')
    os.remove(f'{name_classe}.xlsx')

    name_classe = 'final_' + name_classe

    df.to_csv(f'{path_folder_csv}/{name_classe}.csv', index=False)

# time of execution in minutes
time_exec_min = round( (time.time() - start_time)/60, 4)

print(f'time of execution (preprocessing): {time_exec_min} minutes')
print("READING NAMES: Done. :)")