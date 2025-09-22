#import pdfplumber
#
#pdf_path = "circulos_preenchidos.pdf"
#
#full_text = ""
#
#with pdfplumber.open(pdf_path) as pdf:
#    for page in pdf.pages:
#        text = page.extract_text()
#        if text:
#            full_text += text + "\n"
#
## Salvar o texto em um arquivo .txt
#with open("output.txt", "w", encoding="utf-8") as f:
#    f.write(full_text)
#
#print("Texto extraído do PDF:\n")
#print(full_text)

from pdf2image import convert_from_path
import cv2
import numpy as np

pdf_path = "circulos_preenchidos.pdf"
pages = convert_from_path(pdf_path, dpi=300)

# Get the first page as a PIL Image
page = pages[0]

image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)

# Crop rectangle: [y1:y2, x1:x2]
# Adjust these coordinates to match the PDF layout
math_crop = image[1260:1910, 300:1900]   # y1:y2, x1:x2
edf_cnt_crop = image[1900:2700, 300:2200]  # example for answers area

# Save cropped images if you want
cv2.imwrite("math_gabarito.png", math_crop)
cv2.imwrite("edf_cnt_gabarito.png", edf_cnt_crop)