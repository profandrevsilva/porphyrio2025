import cv2
import numpy as np
import pdfplumber
from icecream import ic

# ---------------------------------------------------
# 1. Ler PDF e extrair nome e turma
# ---------------------------------------------------
pdf_path = "circulos_preenchidos.pdf"
full_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

name  = full_text.split("Aluno(a): ")[1].split("Turma:")[0].strip()
turma = full_text.split("Turma: ")[1].split("Nome do Aluno(a)")[0].strip()
print("Nome:", name)
print("Turma:", turma)

# ---------------------------------------------------
# 2. Ler gabarito e pré-processar
# ---------------------------------------------------
OUT_IMG  = "gabarito_final_CNT_corrected.png"
img_gray = cv2.imread("edf_cnt_gabarito.png", cv2.IMREAD_GRAYSCALE)

# binarização: bolha preta -> branco
_, thresh = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
kernel = np.ones((3, 3), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

# ---------------------------------------------------
# 3. Detectar círculos pretos por contorno
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
    if 0.7 < circularity <= 1.2:               # razoavelmente circular
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if radius > 12:                         # ignora ruídos
            circles.append((int(x), int(y), int(radius)))

print(f"Detectados {len(circles)} círculos pretos")

# ---------------------------------------------------
# 4. Criar matrizes de coordenadas de referência
# ---------------------------------------------------
img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)

def build_matrix(x0):
    """
    Retorna matriz 10x5 com coordenadas centrais esperadas
    para cada questão/alternativa (ajuste se o layout mudar).
    """
    m = np.empty((10, 5), dtype=object)
    y = 237
    for i in range(10):
        x = x0
        for j in range(5):
            m[i, j] = (x, y)
            x += 106
        y += 83
    return m

matrix1 = build_matrix(141)   # primeira coluna
matrix2 = build_matrix(1068)  # segunda coluna

# pontos de referência (opcional para depuração)
for matrix in (matrix1, matrix2):
    for row in matrix:
        for (x, y) in row:
            cv2.circle(img_color, (x, y), 5, (0, 255, 0), -1)

# ---------------------------------------------------
# 5. Detectar respostas múltiplas
# ---------------------------------------------------
jalternative = ['A', 'B', 'C', 'D', 'E']

def detect_answers_multi(circles, matrix, start_q):
    """
    Associa as bolhas detectadas às questões e retorna
    dict {numero_questao: [lista de alternativas]}.
    """
    out = {start_q - i: [] for i in range(10)}  # ex: {20:[],19:[],...}
    for cx, cy, _ in circles:
        for i, linha in enumerate(matrix):
            qnum = start_q - i
            for j, (x, y) in enumerate(linha):
                if (x - 25 < cx < x + 25) and (y - 25 < cy < y + 25):
                    out[qnum].append(jalternative[j])
    return {k: v for k, v in out.items() if v}  # remove vazios

answers  = detect_answers_multi(circles, matrix1, 20)
answers2 = detect_answers_multi(circles, matrix2, 30)
answers.update(answers2)
ic(answers)

# ---------------------------------------------------
# 6. Anotar respostas, nome e turma na imagem
# ---------------------------------------------------
for q, alts in answers.items():
    txt = f"{q}:{'/'.join(alts)}"
    cv2.putText(img_color, txt,
                (750, 20 + 30 * q),
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
