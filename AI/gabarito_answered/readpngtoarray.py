import cv2
import numpy as np
from pathlib import Path
import pdfplumber
from icecream import ic
import pandas as pd

# -------------------------------------------------------------
# CONFIGURAÇÃO GERAL
# -------------------------------------------------------------
pdf_path = "circulos_preenchidos.pdf"     # PDF com nome/turma
img_path = "math_gabarito.png"            # imagem do gabarito
out_annot = "gabarito_final_MATH.png"

FILL_THRESHOLD = 0.25     # fração mínima para considerar uma bolha marcada
K_COLUMNS = 5             # A–E
# parâmetros Hough
HOUGH_DP = 1.2
HOUGH_MIN_DIST = 25
HOUGH_PARAM1 = 50
HOUGH_PARAM2 = 28
HOUGH_MIN_RADIUS = 10
HOUGH_MAX_RADIUS = 40
TOP_MARGIN_FRAC = 0.12

# --- Modo para múltiplas respostas ---
# 'flag'    -> registra como "A/C"
# 'invalid' -> registra "MULTIPLE"
# 'best'    -> pega a mais cheia, mas se a 2ª chega a MULTI_RATIO*top marca como "A/C"
MULTI_MODE = 'flag'
MULTI_RATIO = 0.6  # usado apenas se MULTI_MODE == 'best'
# -------------------------------------------------------------

# =============================================================
# 1) Texto do PDF (nome/turma)
# =============================================================
full_text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

# Extrai nome e turma (ajuste se layout mudar)
name = full_text.split("Aluno(a): ")[1].split("Turma:")[0].strip()
turma = full_text.split("Turma: ")[1].split("Nome do Aluno(a)")[0].strip()
print("Nome:", name)
print("Turma:", turma)

# =============================================================
# 2) Carrega imagem e detecta círculos
# =============================================================
img_path = Path(img_path)
if not img_path.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {img_path}")

img_color = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
h, w = img_gray.shape

# HoughCircles para achar círculos
blur = cv2.medianBlur(img_gray, 5)
circles_raw = cv2.HoughCircles(
    blur, cv2.HOUGH_GRADIENT, dp=HOUGH_DP, minDist=HOUGH_MIN_DIST,
    param1=HOUGH_PARAM1, param2=HOUGH_PARAM2,
    minRadius=HOUGH_MIN_RADIUS, maxRadius=HOUGH_MAX_RADIUS
)
if circles_raw is None:
    raise RuntimeError("HoughCircles não encontrou círculos — ajuste parâmetros.")

circles = np.uint16(np.round(circles_raw[0, :]))
circles = sorted([(int(x), int(y), int(r)) for x, y, r in circles],
                 key=lambda t: (t[1], t[0]))

# descarta cabeçalho
y_thresh = int(h * TOP_MARGIN_FRAC)
circles = [(x, y, r) for (x, y, r) in circles if y >= y_thresh]

# imagem binária invertida (preto->branco)
_, thresh = cv2.threshold(
    cv2.GaussianBlur(img_gray, (5, 5), 0),
    0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

# Raio médio para máscaras internas
all_r = np.array([r for (_, _, r) in circles])
median_r = float(np.median(all_r)) if len(all_r) > 0 else 20.0

# -------------------------------------------------------------
# Função simples de K-means 1D
# -------------------------------------------------------------
def kmeans_1d(xs, k=5, iters=20):
    xs = np.array(xs, dtype=float)
    if len(xs) == 0:
        return []
    centers = np.linspace(xs.min(), xs.max(), k)
    for _ in range(iters):
        groups = [[] for _ in range(k)]
        for x in xs:
            idx = int(np.argmin(np.abs(centers - x)))
            groups[idx].append(x)
        changed = False
        for i in range(k):
            if groups[i]:
                newc = np.mean(groups[i])
                if newc != centers[i]:
                    centers[i] = newc
                    changed = True
            else:
                centers[i] = xs[np.random.randint(0, len(xs))]
                changed = True
        if not changed:
            break
    return sorted(list(centers))

alternatives = ["A", "B", "C", "D", "E"]
results = {}
question_offset = 0

# =============================================================
# 3) Divide em blocos de colunas (esquerda/direita) se houver
# =============================================================
xs = sorted([c[0] for c in circles])
blocks = [circles]
if len(xs) > 1:
    diffs = np.diff(xs)
    max_gap_idx = int(np.argmax(diffs))
    if diffs[max_gap_idx] > np.median(diffs) * 2.0:
        split_x = (xs[max_gap_idx] + xs[max_gap_idx + 1]) / 2.0
        left = [c for c in circles if c[0] <= split_x]
        right = [c for c in circles if c[0] > split_x]
        blocks = [left, right]

# =============================================================
# 4) Para cada bloco, agrupa em linhas e colunas
# =============================================================
for block in blocks:
    if not block:
        continue
    block_xs = sorted([c[0] for c in block])
    col_centers = kmeans_1d(block_xs, k=K_COLUMNS, iters=20)
    if len(col_centers) != K_COLUMNS:
        # fallback simples por gaps
        diffs = np.diff(block_xs) if len(block_xs) > 1 else np.array([])
        tol = np.median(diffs) * 3 if len(diffs) > 0 else 50
        groups, current = [], [block_xs[0]]
        for didx in range(len(diffs)):
            if diffs[didx] < tol:
                current.append(block_xs[didx + 1])
            else:
                groups.append(current)
                current = [block_xs[didx + 1]]
        groups.append(current)
        col_centers = [int(np.median(g)) for g in groups]
        if len(col_centers) != K_COLUMNS:
            col_centers = list(np.linspace(min(block_xs), max(block_xs), K_COLUMNS))

    # agrupa linhas em Y
    block_sorted = sorted(block, key=lambda t: t[1])
    ys = np.array([b[1] for b in block_sorted])
    diffs_y = np.diff(ys) if len(ys) > 1 else np.array([])
    candidate = diffs_y[diffs_y > 5] if len(diffs_y) > 0 else np.array([])
    row_spacing = float(np.median(candidate)) if len(candidate) > 0 else 60.0
    tol_y = max(8.0, row_spacing * 0.5)
    rows, current = [], [block_sorted[0]]
    for c in block_sorted[1:]:
        if abs(c[1] - current[-1][1]) <= tol_y:
            current.append(c)
        else:
            rows.append(current)
            current = [c]
    rows.append(current)

    # =========================================================
    # 5) Avalia cada linha
    # =========================================================
    for i, row in enumerate(rows, start=1):
        row_y = int(np.median([r[1] for r in row]))
        fill_scores = []

        for center_x in col_centers:
            # procura círculo mais próximo
            candidates = [c for c in block
                          if abs(c[1] - row_y) <= tol_y
                          and abs(c[0] - center_x) <= median_r * 1.2]
            if candidates:
                c = min(candidates, key=lambda t: abs(t[0] - center_x))
                cx, cy, cr = c
                mask_cx, mask_cy = int(cx), int(cy)
                mask_r = max(3, int(cr * 0.6))
            else:
                mask_cx, mask_cy = int(center_x), int(row_y)
                mask_r = max(3, int(median_r * 0.6))

            mask = np.zeros_like(thresh)
            cv2.circle(mask, (mask_cx, mask_cy), mask_r, 255, -1)
            mask_area = cv2.countNonZero(mask)
            if mask_area == 0:
                fill_frac = 0.0
            else:
                filled = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
                fill_frac = filled / float(mask_area)
            fill_scores.append(fill_frac)

        # ---------------- lógica de múltiplas respostas ----------------
        qnum = question_offset + i
        if not fill_scores:
            continue
        sorted_idx = sorted(range(len(fill_scores)),
                            key=lambda idx: fill_scores[idx], reverse=True)
        top = sorted_idx[0]
        top_val = fill_scores[top]
        second_val = fill_scores[sorted_idx[1]] if len(sorted_idx) > 1 else 0.0

        if top_val > FILL_THRESHOLD:
            marked = [j for j, v in enumerate(fill_scores) if v > FILL_THRESHOLD]
            if len(marked) == 1:
                results[qnum] = alternatives[top]
            else:
                if MULTI_MODE == 'flag':
                    results[qnum] = '/'.join([alternatives[j] for j in marked])
                elif MULTI_MODE == 'invalid':
                    results[qnum] = 'MULTIPLE'
                elif MULTI_MODE == 'best':
                    if second_val > 0 and (second_val / top_val) > MULTI_RATIO:
                        results[qnum] = '/'.join([alternatives[j] for j in marked])
                    else:
                        results[qnum] = alternatives[top]
        # se ninguém passou do limiar, não marca nada
    question_offset += len(rows)

# =============================================================
# 6) Saída
# =============================================================
question_offset = {}

if not results:
    print("Nenhuma marcação detectada — ajuste parâmetros.")
else:
    for q in sorted(results):
        #print(f"Questão {q}: {results[q]}")
        question_offset[q] = results[q]

ic(question_offset)

# =============================================================
# 7) Anotação final da imagem
# =============================================================
annot = img_color.copy()
font = cv2.FONT_HERSHEY_SIMPLEX
color = (0, 0, 255)
cv2.putText(annot, name, (600, 60), font, 1, color, 2, cv2.LINE_AA)
cv2.putText(annot, 'Turma: ' + turma, (700, 100), font, 1, color, 2, cv2.LINE_AA)

# Desenha todos os círculos detectados
for (x, y, r) in circles:
    cv2.circle(annot, (x, y), r, (0, 255, 0), 2)

# Escreve o resultado próximo ao canto (ajuste conforme layout)
for idx, (q, ans) in enumerate(sorted(results.items()), start=1):
    cv2.putText(annot, f"{q}:{ans}", (650, 120 + 30 * idx),
                font, 0.8, (0, 0, 255), 2)

cv2.imwrite(out_annot, annot)
print("Imagem anotada salva em", out_annot)

# Criar DataFrame
df = pd.DataFrame([{
    "Nome": name,
    "Turma": turma,
    "Respostas": question_offset
}])

print(df)