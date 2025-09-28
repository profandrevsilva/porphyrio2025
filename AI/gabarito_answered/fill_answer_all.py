from pathlib import Path
from PyPDF2 import PdfReader
import re
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import cv2
import numpy as np
import random
import pandas as pd
import os
from icecream import ic

turmas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

def create_folder(turma):

    folder_name = f"gabaritos_preenchidos/{turma}"
    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully!")

    else:
        print(f"Folder '{folder_name}' already exists.")

for turma in turmas:
    create_folder(turma)
    df_names = pd.read_csv(f'../gabarito_name/classes_names/final_names_1{turma}.csv', sep=',')
    for name in df_names['Nome']:
        name = name.replace(" ", "_")
        print(f"Turma: {turma} - Aluno: {name}")
        os.system(f'python3 fill_answer_gabarito.py {name} {turma}')
    print(60*"#")
