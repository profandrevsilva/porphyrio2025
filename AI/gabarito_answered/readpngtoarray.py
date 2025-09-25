import cv2
import numpy as np
from pathlib import Path
import pdfplumber

pdf_path = "circulos_preenchidos.pdf"

full_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

# get name 
name = full_text.split("Aluno(a): ")[1].split("Turma:")[0]
print(name)


# get turma
turma = full_text.split("Turma: ")[1].split("Nome do Aluno(a)")[0]
print(turma)

# ---------- parâmetros ----------
img_path = "math_gabarito.png"    # ajuste aqui
out_annot = "gabarito_final.png"
FILL_THRESHOLD = 0.25             # limiar para considerar uma bolha preenchida
K_COLUMNS = 5                     # A, B, C, D, E
# Hough params
HOUGH_DP = 1.2
HOUGH_MIN_DIST = 25
HOUGH_PARAM1 = 50
HOUGH_PARAM2 = 28
HOUGH_MIN_RADIUS = 10
HOUGH_MAX_RADIUS = 40
TOP_MARGIN_FRAC = 0.12
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
median_r = float(np.median(all_r)) if len(all_r) > 0 else 20.0
inner_r = max(3, int(median_r * 0.45))  # máscara interna (evita borda)

# split em blocos (colunas à esquerda / direita) por gap grande em X
xs = sorted([c[0] for c in circles])
if len(xs) > 1:
    diffs = np.diff(xs)
    max_gap_idx = int(np.argmax(diffs))
    max_gap = diffs[max_gap_idx]
    median_gap = np.median(diffs)
    if max_gap > median_gap * 2.0:
        split_x = (xs[max_gap_idx] + xs[max_gap_idx + 1]) / 2.0
        left = [c for c in circles if c[0] <= split_x]
        right = [c for c in circles if c[0] > split_x]
        blocks = [left, right]
    else:
        blocks = [circles]
else:
    blocks = [circles]

# k-means 1D simples para achar centros de coluna (x)
def kmeans_1d(xs, k=5, iters=20):
    xs = np.array(xs, dtype=float)
    if len(xs) == 0:
        return []
    centers = np.linspace(xs.min(), xs.max(), k)
    for _ in range(iters):
        # assign
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
                # reinit empty center
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
    # xs do block para achar colunas
    block_xs = sorted([c[0] for c in block])
    col_centers = kmeans_1d(block_xs, k=K_COLUMNS, iters=20)
    if len(col_centers) != K_COLUMNS:
        # fallback: agrupar por gaps grandes
        # tenta dividir em K_COLUMNS grupos por diffs
        diffs = np.diff(block_xs) if len(block_xs) > 1 else np.array([])
        tol = np.median(diffs) * 3 if len(diffs) > 0 else 50
        groups = []
        current = [block_xs[0]]
        for didx in range(len(diffs)):
            if diffs[didx] < tol:
                current.append(block_xs[didx+1])
            else:
                groups.append(current); current = [block_xs[didx+1]]
        groups.append(current)
        col_centers = [int(np.median(g)) for g in groups]
        # if still wrong, evenly space
        if len(col_centers) != K_COLUMNS:
            col_centers = list(np.linspace(min(block_xs), max(block_xs), K_COLUMNS))
    # agrupar por linhas (y)
    block_sorted = sorted(block, key=lambda t: t[1])
    ys = np.array([b[1] for b in block_sorted])
    diffs_y = np.diff(ys) if len(ys) > 1 else np.array([])
    candidate = diffs_y[diffs_y > 5] if len(diffs_y) > 0 else np.array([])
    row_spacing = float(np.median(candidate)) if len(candidate) > 0 else 60.0
    tol_y = max(8.0, row_spacing * 0.5)
    rows = []
    current = [block_sorted[0]]
    for c in block_sorted[1:]:
        if abs(c[1] - current[-1][1]) <= tol_y:
            current.append(c)
        else:
            rows.append(current)
            current = [c]
    rows.append(current)

    # para cada row, avaliar cada coluna (usar circle se existir perto, senão amostrar no centro)
    for i, row in enumerate(rows, start=1):
        row_y = int(np.median([r[1] for r in row]))
        # construímos um dicionário de pontos do bloco por (aprox) posição para consulta rápida
        # para cada coluna center procuramos um círculo com cy próximo de row_y e cx próximo de center
        fill_scores = []
        for center_x in col_centers:
            # procura candidato no block com condição vertical
            candidates = [c for c in block if abs(c[1] - row_y) <= tol_y and abs(c[0] - center_x) <= median_r*1.2]
            if candidates:
                # usa o mais próximo em x
                c = min(candidates, key=lambda t: abs(t[0] - center_x))
                cx, cy, cr = c
                mask_cx, mask_cy = int(cx), int(cy)
                mask_r = max(3, int(cr * 0.45))
            else:
                # sem candidato direto: amostra no centro estimado
                mask_cx, mask_cy = int(center_x), int(row_y)
                mask_r = max(3, int(median_r * 0.45))
            mask = np.zeros_like(thresh)
            cv2.circle(mask, (mask_cx, mask_cy), mask_r, 255, -1)
            mean_val = cv2.mean(thresh, mask=mask)[0]
            fill_scores.append(mean_val / 255.0)
        # escolhe melhor alternativa na linha
        best_idx = int(np.argmax(fill_scores))
        best_val = fill_scores[best_idx]
        if best_val > FILL_THRESHOLD:
            qnum = question_offset + i
            results[qnum] = alternatives[best_idx]
    question_offset += len(rows)

# imprime resultado ordenado
if not results:
    print("Gabarito vazio — reveja parâmetros (FILL_THRESHOLD / HOUGH_PARAM2 / radii).")
else:
    for q in sorted(results.keys()):
        print(f"Questão {q}: alternativa {results[q]}")

# salva image anotada (bolhas e preenchidas)
annot = img_color.copy()
# desenha todos os centros de coluna (opcional)
for block in blocks:
    if not block: continue
    block_xs = sorted([c[0] for c in block])
    col_centers = kmeans_1d(block_xs, k=K_COLUMNS, iters=20)
    for cx in col_centers:
        cv2.line(annot, (int(cx), 0), (int(cx), h), (200, 200, 200), 1)

# desenha círculos detectados e marcações
for (x, y, r) in circles:
    cv2.circle(annot, (x, y), r, (0, 255, 0), 2)
for q, alt in results.items():
    # anotação simples: escreve texto próximo ao topo de cada row (não é a posição precisa)
    cv2.putText(annot, f"{q}:{alt}", (10, 20 + 20 * q), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

# font
font = cv2.FONT_HERSHEY_SIMPLEX

# org
org = (600, 60)

# fontScale
fontScale = 1
 
# Red color in BGR
color = (0, 0, 255)

# Line thickness of 2 px
thickness = 2

# Using cv2.putText() method
image = cv2.putText(annot, name, org, font, fontScale, 
                 color, thickness, cv2.LINE_AA, False)

turma = turma[:-1]

turma = 'Turma: ' + turma

print(str(turma))

# org
org = (700, 100)

# Using cv2.putText() method
image = cv2.putText(annot, turma, org, font, fontScale, 
                 color, thickness, cv2.LINE_AA, False)


cv2.imwrite(out_annot, annot)
print("Imagem anotada salva em", out_annot)
