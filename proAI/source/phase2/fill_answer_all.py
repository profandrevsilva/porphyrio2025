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
import toolkit as tool
from tqdm import tqdm

turmas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

for turma in tqdm(turmas, desc=f"Processing Turma", unit="turma"):
    df_names = pd.read_csv(f'../names/csv/final_names_1{turma}.csv', sep=',')
    tool.create_folder(f'pdfs/{turma}')
    for name in df_names['Nome']:
        name = name.replace(" ", "_")
        #print(f"Turma: {turma} - Aluno: {name}")
        os.system(f'python3 fill_answer_gabarito.py {name} {turma}')
    print(60*"#")

os.remove('fill_answer_all.py')
os.remove('fill_answer_gabarito.py')
os.remove('toolkit.py')
