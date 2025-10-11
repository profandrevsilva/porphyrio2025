import os
import pandas as pd
import toolkit as tool
from tqdm import tqdm

turmas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

for turma in tqdm(turmas, desc="Processing Turma", unit="turma"):
    df_names = pd.read_csv(f'../names/csv/final_names_1{turma}.csv', sep=',')
    tool.create_folder(f'screenshots/corrected/math/{turma}')

    for name in df_names['Nome']:
        #print(f"Turma: {turma} - Aluno: {name}")
        name = name.replace(" ", "_")
        os.system(f'python3 detectCirclesToAnswerMATH.py {name} {turma}')

os.remove('detectCirclesToAnswerMATH.py')
os.remove('detectCirclesToAnswerMATH_ALL.py')