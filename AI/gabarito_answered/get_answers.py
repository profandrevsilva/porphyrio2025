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
edf_cnt_crop = image[1900:2950, 300:1900]  # example for answers area

# Save cropped images if you want
cv2.imwrite("math_gabarito.png", math_crop)
cv2.imwrite("edf_cnt_gabarito.png", edf_cnt_crop)