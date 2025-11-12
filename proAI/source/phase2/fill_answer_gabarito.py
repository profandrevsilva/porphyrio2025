import fitz  # PyMuPDF
from pdf2image import convert_from_path
import cv2
import numpy as np
import random
import sys

name = sys.argv[1]
turma = sys.argv[2]

# first matrix: 1
x1 = [106 + 25*i for i in range(5)]
y1 = [357 + 21*i for i in range(5)]

# first matrix: 2
x2 = [328 + 25*i for i in range(5)]
y2 = [357 + 21*i for i in range(5)]

# first matrix: 3
x3 = [106 + 25*i for i in range(5)]
y3 = [513 + 20*i for i in range(10)]

# first matrix: 4
x4 = [328 + 25*i for i in range(5)]
y4 = [513 + 20*i for i in range(10)]


# Converter PDF em imagens
path_pdf = f"../names/pdfs/{turma}/{name}_1{turma}.pdf"

pages = convert_from_path(path_pdf, dpi=300)
doc = fitz.open(path_pdf)  # ou fitz.open() para criar novo
page = doc[0]  # pega a primeira página, ou use doc.new_page() para PDF novo

min_radius_mm = 3
dpi = 300
px_per_mm = dpi / 25.4
min_radius_px = int(min_radius_mm * px_per_mm)  # ≈ 35 px

for page_num, img in enumerate(pages, start=1):
    img_cv = np.array(img)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    
    # Binarizar: círculos pretos = 255, fundo branco = 0
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Suavizar para reduzir ruído
    thresh = cv2.medianBlur(thresh, 5)

    circles = cv2.HoughCircles(
    thresh,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=min_radius_px*2,
    param1=50,  # threshold Canny
    param2=15,  # threshold de detecção de centro
    minRadius=min_radius_px,
    maxRadius=100
    )
    
    circles_list = []

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x, y, r = i
            #print(f"Página {page_num}: círculo preto x={x}, y={y}, r={r}px")
            #x = int(x)
            #y = int(y)
            #circles_list.append((x, y))  # adiciona apenas x, y


radius = 4.2  # em pont

circles = []

j = 0
for i in range(5):
    y = y1[j]
    x = random.choice(x1)
    j = j+1
    
    circles.append((x, y)) 

    # if student fills more than 1 circle
    #x1_ = random.choice(x1)
    #y1_ = y

    #circles.append((x1_, y1_)) 

j = 0
for i in range(5):
    y = y2[j]
    x = random.choice(x2)+ 1
    j = j+1
    
    circles.append((x, y)) 

j = 0
for i in range(10):
    y = y3[j]
    x = random.choice(x3)+ 1
    j = j+1

    circles.append((x, y))

    # if student fills more than 1 circle
    #x3_ = random.choice(x3)
    #y3_ = y

    #circles.append((x3_, y3_)) 

j = 0
for i in range(10):
    y = y4[j]
    x = random.choice(x4)+ 1
    j = j+1
    
    circles.append((x, y))
    
    # if student fills more than 1 circle
    #x4_ = random.choice(x4)
    #y4_ = y

    #circles.append((x4_, y4_)) 

for x, y in circles:
    # Draw filled circle
    shape = page.new_shape()
    shape.draw_circle((x, y), radius)
    shape.finish(fill=(0, 0, 0), color=None)  # preenchido amarelo, sem contorno
    shape.commit()


print(f"Turma: {turma} - Aluno: {name} - Círculos preenchidos: {len(circles)}")

# Salvar PDF
doc.save(f"pdfs/{turma}/{name}_1{turma}.pdf")