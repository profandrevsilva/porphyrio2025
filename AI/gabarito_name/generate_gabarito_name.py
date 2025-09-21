import pandas as pd

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
from pathlib import Path

turmas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

for turma in turmas:
    
    df = pd.read_csv(f'classes_names/final_names_1{turma}.csv', sep=',')

    folder_name = f"pdfs/{turma}"

    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully!")

    else:
        print(f"Folder '{folder_name}' already exists.")
        continue

    for index, row in df.iterrows():
        #print(f"{row['Nome']}")
        name = row['Nome']

        # 1. Read the existing PDF
        input_pdf_path = "../texgabarito/main.pdf"
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        # 2. Create a PDF with the text you want to add
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(143, 657, f"{name}")  # x=100, y=500
        can.drawString(490, 657, f"{turma}")  # x=100, y=500
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # 3. Read the overlay PDF
        from PyPDF2 import PdfReader
        overlay_pdf = PdfReader(packet)

        # 4. Merge the overlay onto the first page
        page = reader.pages[0]
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

        # Add remaining pages without changes
        for i in range(1, len(reader.pages)):
            writer.add_page(reader.pages[i])

        # 5. Save the result
        output_pdf_path = f"pdfs/{turma}/{name}_1{turma}.pdf"
        with open(output_pdf_path, "wb") as f:
            writer.write(f)

        print(f"Name: {name} added successfully!")