import cv2
import numpy as np
import pdfplumber
from collections import defaultdict
from icecream import ic
import sys
import pandas as pd
import os

# ------------------------------
# 1. Ler PDF e extrair nome e turma
# ------------------------------
#pdf_path = "circulos_preenchidos.pdf"
#full_text = ""

#with pdfplumber.open(pdf_path) as pdf:
#    for page in pdf.pages:
#        text = page.extract_text()
#        if text:
#            full_text += text + "\n"

#name  = full_text.split("Aluno(a): ")[1].split("Turma:")[0].strip()
#turma = full_text.split("Turma: ")[1].split("Nome do Aluno(a)")[0].strip()
#print("Nome:", name)
#print("Turma:", turma)

name = sys.argv[1]
turma = sys.argv[2]

# ------------------------------
# 2. Ler gabarito e pré-processar
# ------------------------------
OUT_IMG  = f"screenshot_math_cnt_corrected/{turma}/CNT_corrected_{name}_{turma}.png"
img_gray = cv2.imread(f"screenshot_math_cnt/{turma}/{name}_{turma}_cnt.png", cv2.IMREAD_GRAYSCALE)

# binarização: bolha preta -> branco
_, thresh = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
kernel = np.ones((3, 3), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

# ------------------------------
# 3. Detectar círculos pretos
# ------------------------------
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
circles = []
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 10:
        continue
    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        continue
    circularity = 4 * np.pi * (area / (perimeter * perimeter))
    if 0.7 < circularity <= 1.2:
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if radius > 12:
            circles.append((int(x), int(y), int(radius)))

print(f"Detectados {len(circles)} círculos pretos")

# ------------------------------
# 4. Criar matrizes de referência
# ------------------------------
img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)

def build_matrix(x0, y_start=237, n_rows=10, n_cols=5, x_step=106, y_step=83):
    m = np.empty((n_rows, n_cols), dtype=object)
    y = y_start
    for i in range(n_rows):
        x = x0
        for j in range(n_cols):
            m[i, j] = (x, y)
            x += x_step
        y += y_step
    return m

matrix1 = build_matrix(141)    # coluna esquerda
matrix2 = build_matrix(1068)   # coluna direita

# desenhar pontos de referência
for matrix in (matrix1, matrix2):
    for row in matrix:
        for (x, y) in row:
            cv2.circle(img_color, (x, y), 5, (0, 255, 0), -1)

# ------------------------------
# 5. Detectar respostas
# ------------------------------
jalternative = ['A', 'B', 'C', 'D', 'E']

def detect_answers_multi(circles, matrix, start_q):
    out = defaultdict(list)
    n_rows = matrix.shape[0]
    for cx, cy, _ in circles:
        for i, row in enumerate(matrix):
            qnum = start_q + i
            for j, (x, y) in enumerate(row):
                if np.hypot(cx - x, cy - y) < 30:
                    out[qnum].append(jalternative[j])
                    # desenhar bolha detectada
                    cv2.circle(img_color, (cx, cy), 12, (0, 0, 255), 2)
    return dict(out)

answers_col1 = detect_answers_multi(circles, matrix1, 11)
answers_col2 = detect_answers_multi(circles, matrix2, 21)

# combinar
answers_combined = defaultdict(list)
for k, v in answers_col1.items():
    answers_combined[k].extend(v)
for k, v in answers_col2.items():
    answers_combined[k].extend(v)

# alerta para múltiplas respostas
#for q, alts in answers_combined.items():
#    if len(alts) > 1:
#        print(f"Atenção: Questão {q} tem múltiplas respostas {alts}")

answers_combined = dict(answers_combined)

# Criar DataFrame
df = pd.DataFrame([{
    "Nome": name,
    "Turma": turma,
    "Respostas": answers_combined
}])

ic(df)

path_file = "csv/data_answer_cnt.csv"

# Se o arquivo existir, abre em modo append, sem escrever o cabeçalho de novo
if os.path.exists(path_file):
    df.to_csv(path_file, mode="a", header=False, index=False)
else:
    df.to_csv(path_file, index=False)

# ------------------------------
# 6. Anotar imagem
# ------------------------------
sorted_questions = sorted(answers_combined.keys())  # ordem crescente
y_base = 200
for idx, q in enumerate(sorted_questions):
    alts = answers_combined[q]
    txt = f"{q}: {'/'.join(alts)}"
    cv2.putText(img_color, txt,
                (650, y_base + 30 * idx),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 0, 255), 2)

cv2.putText(img_color, name,
            (600, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 0, 255), 2, cv2.LINE_AA)

cv2.putText(img_color, f"Turma: {turma}",
            (700, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 0, 255), 2, cv2.LINE_AA)

cv2.imwrite(OUT_IMG, img_color)
print(f"Imagem final salva em {OUT_IMG}")
