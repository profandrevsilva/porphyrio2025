import pdfplumber

pdf_path = "circulos_preenchidos.pdf"

full_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

# Salvar o texto em um arquivo .txt
#with open("output.txt", "w", encoding="utf-8") as f:
#    f.write(full_text)

# get name 
name = full_text.split("Aluno(a): ")[1].split("Turma:")[0]
print(name)


# get turma
turma = full_text.split("Turma: ")[1].split("Nome do Aluno(a)")[0]
print(turma)

print("Texto extraído do PDF:\n")
print(full_text)