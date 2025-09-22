from pdf2image import convert_from_path

# Caminho do PDF
pdf_path = "circulos_preenchidos.pdf"

# Converter todas as páginas do PDF em imagens
pages = convert_from_path(pdf_path, dpi=300)  # retorna uma lista de imagens

# Processar cada página
for i, page in enumerate(pages):
    # page já é um objeto PIL Image, não precisa de Image.open()
    page.show()  # mostrar a imagem
    # ou salvar
    page.save(f'pagina_{i+1}.png', 'PNG')
