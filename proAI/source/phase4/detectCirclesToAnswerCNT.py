import cv2
import numpy as np
from collections import defaultdict
import sys
import pandas as pd
import os

# ---------------------------------------------------
# 1. Argumentos: nome e turma
# ---------------------------------------------------
name = sys.argv[1]
turma = sys.argv[2]

# ---------------------------------------------------
# 2. Ler gabarito e pré-processar
# ---------------------------------------------------
OUT_IMG  = f"screenshots/corrected/cnt/{turma}/{name}_{turma}.png"
IMG_PATH = f"../respostas/screenshots/cnt/{turma}/{name}_{turma}_cnt.png"

img_gray = cv2.imread(IMG_PATH, cv2.IMREAD_GRAYSCALE)
if img_gray is None:
    raise FileNotFoundError(f"Arquivo não encontrado: {IMG_PATH}")

# Binarização: bolha preta -> branco
_, thresh = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
kernel = np.ones((3, 3), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
thresh = cv2.medianBlur(thresh, 5)  # ajuda a eliminar ruído

# ---------------------------------------------------
# 3. Detectar círculos pretos
# ---------------------------------------------------
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

# ---------------------------------------------------
# 4. Criar matrizes de referência
# ---------------------------------------------------
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

# ---------------------------------------------------
# 5. Detectar respostas
# ---------------------------------------------------
jalternative = ['A', 'B', 'C', 'D', 'E']

def detect_answers_multi(circles, matrix, start_q, tol=30):
    """
    Para cada posição de referência (x,y) na matriz,
    verifica se há um círculo detectado dentro de uma tolerância.
    Retorna dict { qnum: [alternativas] }.
    """
    out = defaultdict(list)
    if len(circles) == 0:
        return {}

    circle_arr = np.array(circles)  # (cx, cy, r)
    for i, row in enumerate(matrix):
        qnum = start_q + i
        for j, (x, y) in enumerate(row):
            dx = circle_arr[:, 0] - x
            dy = circle_arr[:, 1] - y
            d = np.hypot(dx, dy)
            matches = np.where(d < np.maximum(tol, circle_arr[:, 2] * 0.8))[0]
            if matches.size > 0:
                out[qnum].append(jalternative[j])
    # remover duplicatas e ordenar
    for q in list(out.keys()):
        out[q] = sorted(set(out[q]), key=lambda a: jalternative.index(a))
    return dict(out)

answers_col1 = detect_answers_multi(circles, matrix1, 11)
answers_col2 = detect_answers_multi(circles, matrix2, 21)

# Combinar resultados
answers_combined = defaultdict(list)
for k, v in answers_col1.items():
    answers_combined[k].extend(v)
for k, v in answers_col2.items():
    answers_combined[k].extend(v)

# Normalizar e ordenar
answers_combined = {k: sorted(set(v), key=lambda a: jalternative.index(a)) for k, v in answers_combined.items()}
answers_combined = dict(sorted(answers_combined.items()))

# ---------------------------------------------------
# 6. Verificar múltiplas respostas
# ---------------------------------------------------
multiple_answers = {q: alts for q, alts in answers_combined.items() if len(alts) > 1}
if multiple_answers:
    #print("Atenção: Questões com múltiplas respostas detectadas:")
    for q, alts in multiple_answers.items():
        pass
        #print(f" - Questão {q}: {alts}")

# ---------------------------------------------------
# 7. Gerar DataFrame (formato pedido)
# ---------------------------------------------------
# Caso nenhuma resposta tenha sido marcada, marcar como 'Branco'
for q in range(11, 31):
    if q not in answers_combined:
        answers_combined[q] = ['BRANCO']
    elif len(answers_combined[q]) == 0:
        answers_combined[q] = ['BRANCO']
    elif len(answers_combined[q]) > 1:
        answers_combined[q] = ['ANULADA']

# Criar dicionário {questão: resposta única}
respostas_dict = {q: alts[0] for q, alts in answers_combined.items()}

# Montar DataFrame no formato solicitado
df = pd.DataFrame([{
    "Nome": name,
    "Turma": turma,
    "Respostas": str(respostas_dict)
}])

path_file = "csv/data_answer_cnt.csv"
if os.path.exists(path_file):
    df.to_csv(path_file, mode="a", header=False, index=False)
else:
    df.to_csv(path_file, index=False)

# ---------------------------------------------------
# 8. Anotar imagem com resultados
# ---------------------------------------------------
sorted_questions = sorted(answers_combined.keys())
y_base = 200
for idx, q in enumerate(sorted_questions):
    alts = answers_combined[q]
    color = (0, 0, 255)
    if alts[0] == 'Múltipla':
        color = (0, 165, 255)  # laranja
    elif alts[0] == 'Branco':
        color = (128, 128, 128)  # cinza

    txt = f"{q}: {'/'.join(alts)}"
    cv2.putText(img_color, txt,
                (650, y_base + 30 * idx),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, color, 2)

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
