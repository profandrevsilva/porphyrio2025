import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
from pathlib import Path
import time
from tqdm import tqdm

# Get start time 
start_time = time.time()

# path to folders: csv and xlsx
path_folder_csv = 'csv/'

os.system('python3 read_names.py')

turmas = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

for turma in tqdm(turmas, desc="Processing Turma", unit="turma"):
    print(f"Turma: {turma}...")
    df = pd.read_csv(f'{path_folder_csv}/final_names_1{turma}.csv', sep=',')

    folder_name = f"pdfs/{turma}"

    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully!")

    else:
        print(f"Folder '{folder_name}' already exists.")
        #continue

    for index, row in df.iterrows():
        #print(f"{row['Nome']}")
        name = row['Nome']

        # 1. Read the existing PDF
        input_pdf_path = "main.pdf"
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
        overlay_pdf = PdfReader(packet)

        # 4. Merge the overlay onto the first page
        page = reader.pages[0]
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

        # Add remaining pages without changes
        for i in range(1, len(reader.pages)):
            writer.add_page(reader.pages[i])

        # add underline to space to avoid error 
        name_normalized = name.replace(" ", "_")
        name = name_normalized

        # 5. Save the result
        output_pdf_path = f"pdfs/{turma}/{name}_1{turma}.pdf"
        with open(output_pdf_path, "wb") as f:
            writer.write(f)

        print(f"Name: {name} added successfully!")

    # merge files
    folder_path = Path(f"{folder_name}")

    pdf_files = df['Nome'].tolist()

    #print(pdf_files)

    writer = PdfWriter()

    output_file = f"allpdfs/1-Serie-{turma}.pdf"

    for pdf in pdf_files:
        pdf = pdf.replace(" ", "_")
        pdf = pdf + f"_1{turma}.pdf"
        out_pdf = f'pdfs/{turma}/{pdf}'
        #print(out_pdf)

        reader = PdfReader(out_pdf)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_file, "wb") as out_file:
        writer.write(out_file)

    print(f"All PDFs merged into {output_file}.pdf")

# remove files
os.remove('main.pdf')
os.remove('generate_gabarito_name.py')
os.remove('read_names.py')
os.remove('toolkit.py')

# time of execution in minutes
time_exec_min = round( (time.time() - start_time)/60, 4)

print(f'time of execution (preprocessing): {time_exec_min} minutes')
print('generate gabarito with names. Done!')