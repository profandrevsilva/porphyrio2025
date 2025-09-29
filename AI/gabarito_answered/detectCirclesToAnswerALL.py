from pdf2image import convert_from_path
import cv2
import numpy as np
import os
import pandas as pd

turmas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

def create_folder(turma):

    folder_name = f"screenshot_math_cnt_corrected/{turma}"
    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully!")

    else:
        print(f"Folder '{folder_name}' already exists.")

for turma in turmas:
    df_names = pd.read_csv(f'../gabarito_name/classes_names/final_names_1{turma}.csv', sep=',')
    create_folder(turma)

    for name in df_names['Nome']:
        #print(f"Turma: {turma} - Aluno: {name}")
        name = name.replace(" ", "_")
        os.system(f'python3 detectCirclesToAnswer.py {name} {turma}')