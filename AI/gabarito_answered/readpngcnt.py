import cv2
import numpy as np
from pathlib import Path

# ---------- parâmetros ----------
img_path = "edf_cnt_gabarito.png"
out_annot = "gabarito_final_adaptado.png"
FILL_THRESHOLD = 0.4             # limiar ajustado para bolhas preenchidas
K_COLUMNS = 5                     # A, B, C, D, E
# Hough params
HOUGH_DP = 1.2
HOUGH_MIN_DIST = 25
HOUGH_PARAM1 = 50
HOUGH_PARAM2 = 25                 # mais baixo para capturar bolhas menores
HOUGH_MIN_RADIUS = 10
HOUGH_MAX_RADIUS = 25
TOP_MARGIN_FRAC = 0.05             # reduzido se não houver cabeçalho
# ---------------------------------

img_path = Path(img_path)
if not img_path.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {img_path}")

img_color = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
h, w = img_gray.shape

# Detecta círculos com Hough
blur = cv2.medianBlur(img_gray, 5)
circles_raw = cv2.HoughCircles(
    blur, cv2.HOUGH_GRADIENT, dp=HOUGH_DP, minDist=HOUGH_MIN_DIST,
    param1=HOUGH_PARAM1, param2=HOUGH_PARAM2,
    minRadius=HOUGH_MIN_RADIUS, maxRadius=HOUGH_MAX_RADIUS
)
if circles_raw is None:
    raise RuntimeError("HoughCircles não encontrou círculos — ajuste parâmetros.")

circles = np.uint16(np.round(circles_raw[0, :]))
circles = sorted([(int(x), int(y), int(r)) for x, y, r in circles], key=lambda t: (t[1], t[0]))

# descarta cabecalho
y_thresh = int(h * TOP_MARGIN_FRAC)
circles = [(x, y, r) for (x, y, r) in circles if y >= y_thresh]

# imagem binária (inversa: preenchido -> branco)
_, thresh = cv2.threshold(cv2.GaussianBlur(img_gray, (5, 5), 0), 0, 255,
                          cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

# informações úteis
all_r = np.array([r for (_, _, r) in circles])
median_r = float(np.median(all_r)) if len(all_r) > 0 else 15.0
inner_r = max(3, int(median_r * 0.45))  # máscara interna (evita borda)

# split em blocos por gap grande em X
xs = sorted([c[0] for c in circles])
blocks = [circles]  # neste caso, todos juntos funcionam

# k-means 1D simples para achar centros de coluna (x)
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
            if len(groups[i]) > 0:
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

for block in blocks:
    if not block:
        continue
    block_xs = sorted([c[0] for c in block])
    col_centers = kmeans_1d(block_xs, k=K_COLUMNS, iters=20)
    block_sorted = sorted(block, key=lambda t: t[1])
    ys = np.array([b[1] for b in block_sorted])
    diffs_y = np.diff(ys) if len(ys) > 1 else np.array([])
    row_spacing = float(np.median(diffs_y)) if len(diffs_y) > 0 else 40.0
    tol_y = max(5.0, row_spacing * 0.5)
    rows = []
    current = [block_sorted[0]]
    for c in block_sorted[1:]:
        if abs(c[1] - current[-1][1]) <= tol_y:
            current.append(c)
        else:
            rows.append(current)
            current = [c]
    rows.append(current)

    for i, row in enumerate(rows, start=1):
        row_y = int(np.median([r[1] for r in row]))
        fill_scores = []
        for center_x in col_centers:
            candidates = [c for c in block if abs(c[1] - row_y) <= tol_y and abs(c[0] - center_x) <= median_r*1.2]
            if candidates:
                c = min(candidates, key=lambda t: abs(t[0] - center_x))
                cx, cy, cr = c
                mask_cx, mask_cy = int(cx), int(cy)
                mask_r = max(3, int(cr * 0.45))
            else:
                mask_cx, mask_cy = int(center_x), int(row_y)
                mask_r = max(3, int(median_r * 0.45))
            mask = np.zeros_like(thresh)
            cv2.circle(mask, (mask_cx, mask_cy), mask_r, 255, -1)
            mean_val = cv2.mean(thresh, mask=mask)[0]
            fill_scores.append(mean_val / 255.0)
        best_idx = int(np.argmax(fill_scores))
        best_val = fill_scores[best_idx]
        if best_val > FILL_THRESHOLD:
            qnum = question_offset + i
            results[qnum] = alternatives[best_idx]
    question_offset += len(rows)

# imprime resultado
for q in sorted(results.keys()):
    print(f"Questão {q}: alternativa {results[q]}")

# salva imagem anotada
annot = img_color.copy()
for (x, y, r) in circles:
    cv2.circle(annot, (x, y), r, (0, 255, 0), 2)
for q, alt in results.items():
    # aproximação para desenho perto do círculo
    row = rows[q-1] if q-1 < len(rows) else rows[0]
    cx, cy, _ = row[0]
    cv2.putText(annot, f"{alt}", (cx-10, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
cv2.imwrite(out_annot, annot)
print("Imagem anotada salva em", out_annot)
