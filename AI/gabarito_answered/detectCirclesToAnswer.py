from PIL import Image
import cv2
import easyocr
import numpy as np
from icecream import ic

OUT_IMG  = "gabarito_final_CNT_corrected.png"

img = cv2.imread("edf_cnt_gabarito.png", cv2.IMREAD_GRAYSCALE)

# Threshold image to get black areas
_, thresh = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)  
# THRESH_BINARY_INV because black circles will become white

# Optional: remove small noise
kernel = np.ones((3,3), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter for circular shapes
circles = []
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 10:  # ignore tiny spots
        continue
    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        continue
    circularity = 4 * np.pi * (area / (perimeter * perimeter))
    if 0.7 < circularity <= 1.2:  # 1.0 is a perfect circle
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if radius > 12:
            circles.append((int(x), int(y), int(radius)))

print(f"Detected {len(circles)} black circles:")
#for c in circles:
#    print(f"Center: ({c[0]}, {c[1]}), Radius: {c[2]}")

# Optional: draw detected circles
img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
for x, y, r in circles:
    cv2.circle(img_color, (x, y), r, (0, 0, 255), 2)

##############################################
    ## Block - 1
    x_alt = 141

    for icon in ['A', 'B', 'C', 'D', 'E']:
        # block 1 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (x_alt, 190)      # Starting coordinate
        end_point   = (x_alt, 1010)    # Ending coordinate
        color       = (255, 0, 0)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        x_alt = x_alt + 106

    y_alt = 237
    for q in range(11,21):
        # block 1 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (120, y_alt)      # Starting coordinate
        end_point   = (600, y_alt)    # Ending coordinate
        color       = (100,0,255)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        y_alt = y_alt + 83

    ##################################################################

    ##############################################
    ## Block - 2
    x_alt = 1068
    for icon in ['A', 'B', 'C', 'D', 'E']:
        # block 2 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (x_alt, 190)      # Starting coordinate
        end_point   = (x_alt, 1010)    # Ending coordinate
        color       = (255, 0, 0)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        x_alt = x_alt + 106

    y_alt = 238
    for q in range(11,21):
        # block 2 : Alternative: A, B, C, D, E
        # Draw a white line from point (x1, y1) to (x2, y2)
        start_point = (1040, y_alt)      # Starting coordinate
        end_point   = (1550, y_alt)    # Ending coordinate
        color       = (100,0,255)  # BGR color: white
        thickness   = 2            # Line thickness in pixels

        cv2.line(img_color, start_point, end_point, color, thickness)
        y_alt = y_alt + 83

    ##################################################################

    ## Fill matrix
    rows, cols = 10, 5
    
    # block 1
    matrix1 = np.empty((rows, cols), dtype=object)

    xcoor = 141
    ycoor = 237
    for y in range(rows):
        for x in range(cols):
            matrix1[y, x] = (xcoor, ycoor)
            xcoor = xcoor + 106
        ycoor = ycoor + 83
        xcoor = 141
    
    #ic(matrix1)

    # block 2
    matrix2 = np.empty((rows, cols), dtype=object)

    xcoor = 1068
    ycoor = 237
    for y in range(rows):
        for x in range(cols):
            matrix2[y, x] = (xcoor, ycoor)
            xcoor = xcoor + 106
        ycoor = ycoor + 83
        xcoor = 1068
    
    #ic(matrix2)

    # Cor e raio dos pontos
    color = (0, 225, 0)   # vermelho em BGR
    radius = 5
    thickness = -1        # -1 = círculo preenchido

    # Percorrer linhas e colunas
    for row in matrix1:
        for (x, y) in row:             # cada elemento é uma tupla (x, y)
            cv2.circle(img_color, (x, y), radius, color, thickness)

    # Percorrer linhas e colunas
    for row in matrix2:
        for (x, y) in row:             # cada elemento é uma tupla (x, y)
            cv2.circle(img_color, (x, y), radius, color, thickness)
    
        # Show the image in a window
        #cv2.imshow("Line Example", img_color)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

jalternative = ['A', 'B', 'C', 'D', 'E']
iquestion = 20

question_alter1 = {}

for icircle in circles:
    # loop de fora: cada linha
    for i, linha in enumerate(matrix1):
        for j, (x, y) in enumerate(linha):
            #print(f"{i} {j}: matrix: {x}, {y}, circle: {icircle[0]}, {icircle[1]}" )
            if  (x - 25 < icircle[0] < x + 25) and (y - 25 < icircle[1] < y + 25):
                #print(f"{iquestion}: {jalternative[j]}")
                question_alter1[iquestion] = jalternative[j]
                iquestion = iquestion - 1

question_alter1 = dict(sorted(question_alter1.items()))

iquestion = 30

question_alter2 = {}

for icircle in circles:
    # loop de fora: cada linha
    for i, linha in enumerate(matrix2):
        for j, (x, y) in enumerate(linha):
            #print(f"{i} {j}: matrix: {x}, {y}, circle: {icircle[0]}, {icircle[1]}" )
            if  (x - 25 < icircle[0] < x + 25) and (y - 25 < icircle[1] < y + 25):
                #print(f"{iquestion}: {jalternative[j]}")
                question_alter2[iquestion] = jalternative[j]
                iquestion = iquestion - 1

question_alter2 = dict(sorted(question_alter2.items()))

question_alternatives = question_alter1 | question_alter2
ic(question_alternatives)

# desenha círculos detectados e marcações
for q, alt in question_alternatives.items():
    # anotação simples: escreve texto próximo ao topo de cada row (não é a posição precisa)
    cv2.putText(img_color, f"{q}:{alt}", (750, 20 + 30 * q), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

#cv2.imshow("Detected Circles", img_color)
cv2.imwrite(OUT_IMG, img_color)
cv2.waitKey(0)
cv2.destroyAllWindows()