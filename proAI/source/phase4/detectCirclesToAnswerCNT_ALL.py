import os
import pandas as pd
import toolkit as tool
from tqdm import tqdm

# Get start time 
start_time = tool.start_time()

turmas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

for turma in tqdm(turmas, desc="Processing Turma", unit="turma"):
    df_names = pd.read_csv(f'../names/csv/final_names_1{turma}.csv', sep=',')
    tool.create_folder(f'screenshots/corrected/cnt/{turma}')
    
    for name in df_names['Nome']:
        #print(f"Turma: {turma} - Aluno: {name}")
        name = name.replace(" ", "_")
        os.system(f'python3 detectCirclesToAnswerCNT.py {name} {turma}')

os.remove('detectCirclesToAnswerCNT.py')
os.remove('detectCirclesToAnswerCNT_ALL.py')

tool.time_exec(start_time)