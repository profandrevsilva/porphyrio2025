from pathlib import Path
import cv2
import numpy as np
import os
import csv
import pandas as pd
from icecream import ic

# ----------------------------
# CONFIGURAÇÃO
# ----------------------------
IMG_PATH = "edf_cnt_gabarito.png"
OUT_CSV  = "gabarito_CNT.csv"
OUT_IMG  = "gabarito_final_CNT.png"

# Limiares para considerar preenchido
FILL_THRESHOLD = 0.5     # proporção mínima de pixels escuros
K_COLUMNS       = 2       # A, B, C, D, E
OPTIONS         = ['A','B','C','D','E']

# ----------------------------
# 1. Leitura e pré-processamento
# ----------------------------
img_path = Path(IMG_PATH)   # ✅ converte string para Path

if not img_path.exists():
    raise FileNotFoundError(f"Imagem {IMG_PATH} não encontrada.")

gray = cv2.imread(str(IMG_PATH), cv2.IMREAD_GRAYSCALE)
if gray is None:
    raise RuntimeError("Falha ao carregar a imagem.")

# Binarização: áreas escuras -> branco
_, thresh = cv2.threshold(gray, 0, 255,
                          cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# ----------------------------
# 2. Detectar círculos
# ----------------------------
circles = cv2.HoughCircles(
    thresh,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=20,
    param1=50,
    param2=15,
    minRadius=18,
    maxRadius=25
)

if circles is None:
    raise RuntimeError("Nenhum círculo detectado.")

ic(len(circles[0]))

circles = np.uint16(np.around(circles[0]))

# Ordenar de cima para baixo, esquerda para direita
circles = sorted(circles, key=lambda c: (c[1], c[0]))

# ----------------------------
# 3. Agrupar em linhas (questões)
# ----------------------------
rows = []
current_row = []
last_y = None
tol = 5  # tolerância para considerar mesma linha

for (x, y, r) in circles:
    if last_y is None or abs(y - last_y) < tol:
        current_row.append((x, y, r))
        last_y = y if last_y is None else (last_y + y) / 2
    else:
        rows.append(sorted(current_row, key=lambda c: c[0]))
        current_row = [(x, y, r)]
        last_y = y
if current_row:
    rows.append(sorted(current_row, key=lambda c: c[0]))



# ----------------------------
# 4. Avaliar preenchimento
# ----------------------------
results = []
img_color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

q_num = 11  # número inicial da questão
for row in rows:
    # se não tiver 5 círculos, pula
    if len(row) < K_COLUMNS:
        continue

    scores = []
    for i, (x, y, r) in enumerate(row):
        mask = np.zeros_like(thresh)
        cv2.circle(mask, (x, y), r-2, 255, -1)
        total = cv2.countNonZero(mask)
        filled = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
        ratio = filled / float(total)
        scores.append((ratio, i))
    
    best_ratio, best_idx = max(scores, key=lambda t: t[0])
    chosen = OPTIONS[best_idx] if best_ratio >= FILL_THRESHOLD else '-'

    results.append({
        'Questão': q_num,
        'Alternativa': chosen,
        'Score': round(best_ratio, 2)
    })

    # Desenho na imagem
    for (ratio, i) in scores:
        x, y, r = row[i]
        if ratio > 0.8:
            print(x, y, ratio)
            color = (0, 0, 255)
            cv2.circle(img_color, (x, y), r, color, 2)

    ##############################################
    ## Block - 1
    x_alt = 141

    for icon in ['A', 'B', 'C', 'D', 'E']:
        # block 1 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (x_alt, 190)      # Starting coordinate
        end_point   = (x_alt, 800)    # Ending coordinate
        color       = (255, 0, 0)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        x_alt = x_alt + 106

    y_alt = 237
    for q in range(11,18):
        # block 1 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (130, y_alt)      # Starting coordinate
        end_point   = (600, y_alt)    # Ending coordinate
        color       = (100,0,255)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        y_alt = y_alt + 86

    ##################################################################

    ##############################################
    ## Block - 2
    x_alt = 759
    for icon in ['A', 'B', 'C', 'D', 'E']:
        # block 1 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (x_alt, 190)      # Starting coordinate
        end_point   = (x_alt, 800)    # Ending coordinate
        color       = (255, 0, 0)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        x_alt = x_alt + 106

    y_alt = 237
    for q in range(11,18):
        # block 1 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (750, y_alt)      # Starting coordinate
        end_point   = (1200, y_alt)    # Ending coordinate
        color       = (100,0,255)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        y_alt = y_alt + 84

    ##################################################################

    ##############################################
    ## Block - 3
    x_alt = 1381
    for icon in ['A', 'B', 'C', 'D', 'E']:
        # block 1 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (x_alt, 190)      # Starting coordinate
        end_point   = (x_alt, 800)    # Ending coordinate
        color       = (255, 0, 0)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        x_alt = x_alt + 106

    y_alt = 238
    for q in range(11,18):
        # block 1 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (1360, y_alt)      # Starting coordinate
        end_point   = (1860, y_alt)    # Ending coordinate
        color       = (100,0,255)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        y_alt = y_alt + 101

    ##################################################################

    ## Fill matrix
    rows, cols = 7, 5
    
    # block 1
    matrix1 = np.empty((rows, cols), dtype=object)

    xcoor = 141
    ycoor = 237
    for y in range(rows):
        for x in range(cols):
            matrix1[y, x] = (xcoor, ycoor)
            xcoor = xcoor + 106
        ycoor = ycoor + 86
        xcoor = 141
    
    ic(matrix1)

    # block 2
    matrix2 = np.empty((rows, cols), dtype=object)

    xcoor = 759
    ycoor = 237
    for y in range(rows):
        for x in range(cols):
            matrix2[y, x] = (xcoor, ycoor)
            xcoor = xcoor + 106
        ycoor = ycoor + 84
        xcoor = 759
    
    ic(matrix2)

    # block 3
    matrix3 = np.empty((rows, cols), dtype=object)

    xcoor = 1381
    ycoor = 237
    for y in range(rows):
        for x in range(cols):
            matrix3[y, x] = (xcoor, ycoor)
            xcoor = xcoor + 106
        ycoor = ycoor + 101
        xcoor = 1381
    
    ic(matrix3)

    # Cor e raio dos pontos
    color = (0, 225, 0)   # vermelho em BGR
    radius = 5
    thickness = -1        # -1 = círculo preenchido

    # Percorrer linhas e colunas
    for row in matrix1:
        for (x, y) in row:             # cada elemento é uma tupla (x, y)
            cv2.circle(img_color, (x, y), radius, color, thickness)

    # Cor e raio dos pontos
    color = (0, 225, 0)   # vermelho em BGR
    radius = 5
    thickness = -1        # -1 = círculo preenchido

    # Percorrer linhas e colunas
    for row in matrix2:
        for (x, y) in row:             # cada elemento é uma tupla (x, y)
            cv2.circle(img_color, (x, y), radius, color, thickness)
    
    # Percorrer linhas e colunas
    for row in matrix3:
        for (x, y) in row:             # cada elemento é uma tupla (x, y)
            cv2.circle(img_color, (x, y), radius, color, thickness)

        # Show the image in a window
        #cv2.imshow("Line Example", img_color)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        #if x == 139 and y == 489:
        #    color = (0, 255, 255)
        #    cv2.circle(img_color, (x, y), r, color, 2)

        #color = (0, 0, 255) if ratio >= FILL_THRESHOLD else (0, 0, 0)
        #cv2.circle(img_color, (x, y), r, color, 2)
    #if chosen != '-':
    #    x, y, r = row[OPTIONS.index(chosen)]
    #    cv2.putText(img_color, chosen, (x - 10, y + 5),
    #                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    q_num += 1

# ----------------------------
# 5. Salvar resultados
# ----------------------------
df = pd.DataFrame(results)
df.to_csv(OUT_CSV, index=False, encoding="utf-8")
cv2.imwrite(OUT_IMG, img_color)

print("Resultados salvos em", OUT_CSV)
print("Imagem anotada salva em", OUT_IMG)
print(df)
