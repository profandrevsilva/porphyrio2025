from pdf2image import convert_from_path
import cv2
import numpy as np
import pandas as pd
import toolkit as tool

turmas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

print("Processing Turma... Get Answers.")
for turma in turmas:
    df_names = pd.read_csv(f'../names/csv/final_names_1{turma}.csv', sep=',')
    for name in df_names['Nome']:
        print(f"Turma: {turma} - Aluno: {name}")
        name = name.replace(" ", "_")
        pdf_path = f"../preenchidos/pdfs/{turma}/{name}_1{turma}.pdf"
        pages = convert_from_path(pdf_path, dpi=300)

        # Get the first page as a PIL Image
        page = pages[0]

        image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)

        # Crop rectangle: [y1:y2, x1:x2]
        # Adjust these coordinates to match the PDF layout
        math_crop = image[1260:1910, 300:1900]   # y1:y2, x1:x2
        edf_cnt_crop = image[1900:2950, 300:1900]  # example for answers area

        # folder for each turma to screenshots
        tool.create_folder(f"screenshots/math/{turma}")
        tool.create_folder(f"screenshots/cnt/{turma}")

        # Save cropped images if you want
        cv2.imwrite(f"screenshots/math/{turma}/{name}_{turma}_math.png", math_crop)
        cv2.imwrite(f"screenshots/cnt/{turma}/{name}_{turma}_cnt.png", edf_cnt_crop)