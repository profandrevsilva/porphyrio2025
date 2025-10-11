import cv2
import numpy as np
from pathlib import Path
import pandas as pd
import sys
import os

# -------------------------------------------------------------
# Entradas
# -------------------------------------------------------------
name = sys.argv[1]
turma = sys.argv[2]

# -------------------------------------------------------------
# CONFIGURAÇÃO GERAL
# -------------------------------------------------------------
img_path = f"../respostas/screenshots/math/{turma}/{name}_{turma}_math.png"
out_annot = f"screenshots/corrected/math/{turma}/{name}_{turma}.png"

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
# 1) Carrega imagem e detecta círculos
# -------------------------------------------------------------
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
# 2) Divide em blocos de colunas (esquerda/direita) se houver
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
# 3) Para cada bloco, agrupa em linhas e colunas
# =============================================================
for block in blocks:
    if not block:
        continue
    block_xs = sorted([c[0] for c in block])
    col_centers = kmeans_1d(block_xs, k=K_COLUMNS, iters=20)
    if len(col_centers) != K_COLUMNS:
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
    # 4) Avalia cada linha
    # =========================================================
    for i, row in enumerate(rows, start=1):
        row_y = int(np.median([r[1] for r in row]))
        fill_scores = []

        for center_x in col_centers:
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
            fill_frac = 0.0
            if mask_area > 0:
                filled = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
                fill_frac = filled / float(mask_area)
            fill_scores.append(fill_frac)

        qnum = question_offset + i
        sorted_idx = sorted(range(len(fill_scores)), key=lambda idx: fill_scores[idx], reverse=True)
        top = sorted_idx[0]
        top_val = fill_scores[top]
        second_val = fill_scores[sorted_idx[1]] if len(sorted_idx) > 1 else 0.0
        marked = [j for j, v in enumerate(fill_scores) if v > FILL_THRESHOLD]

        # --- Nenhuma marcação ---
        if len(marked) == 0:
            results[qnum] = "BRANCO"
        # --- Uma marcação ---
        elif len(marked) == 1:
            results[qnum] = alternatives[marked[0]]
        # --- Múltiplas marcações ---
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

    question_offset += len(rows)

# =============================================================
# 5) Anotação final da imagem
# =============================================================
os.makedirs(os.path.dirname(out_annot), exist_ok=True)
annot = img_color.copy()
font = cv2.FONT_HERSHEY_SIMPLEX
color = (0, 0, 255)
cv2.putText(annot, name, (600, 60), font, 1, color, 2, cv2.LINE_AA)
cv2.putText(annot, 'Turma: ' + turma, (700, 100), font, 1, color, 2, cv2.LINE_AA)

for (x, y, r) in circles:
    cv2.circle(annot, (x, y), r, (0, 255, 0), 2)

for idx, (q, ans) in enumerate(sorted(results.items()), start=1):
    cv2.putText(annot, f"{q}:{ans}", (650, 120 + 30 * idx),
                font, 0.8, (0, 0, 255), 2)

cv2.imwrite(out_annot, annot)

# =============================================================
# 6) Criar CSV
# =============================================================
df = pd.DataFrame([{
    "Nome": name,
    "Turma": turma,
    "Respostas": results
}])

path_file = Path("csv/data_answer_math.csv")
path_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(path_file, mode="a" if path_file.exists() else "w",
          header=not path_file.exists(), index=False)