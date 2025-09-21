from pathlib import Path
from PyPDF2 import PdfReader
import re

# Caminho do PDF
pdf_path = Path("../gabarito_name/pdfs/A/ANA CLARA JUVENTINO_1A.pdf")

# Lendo o PDF
reader = PdfReader(str(pdf_path))
texto = ""
for page in reader.pages:
    texto += page.extract_text() + "\n"

# Extraindo o gabarito (ex: "1. A", "2. C")
padrao = r"(\d+)\.\s*([A-E])"
respostas = re.findall(padrao, texto)

# Transformando em lista de strings "⬤ A"
gabarito_circulo = [f"{num}. ⬤ {resp}" for num, resp in respostas]

# Mostrando o resultado
for linha in gabarito_circulo:
    print(linha)
