
---

# 📘 Projeto Avaliação Integrada – Automatização da Correção

## 📌 Descrição

O projeto **Avaliação Integrada** tem como objetivo automatizar o processo de correção de avaliações de múltipla escolha. Através de técnicas de **geração de PDFs, visão computacional e processamento de imagens**, é possível corrigir provas de forma **rápida, precisa e escalável**, reduzindo erros humanos e economizando tempo.

---

## 🚀 Etapas do Processo

### **1. Geração dos PDFs personalizados**

* Criação de provas em PDF com o nome de cada aluno e sua turma.
* Cada estudante recebe um arquivo individual.

### **2. Preenchimento pelos alunos**

* Os alunos respondem às provas impressas, preenchendo os círculos correspondentes às alternativas.

### **3. Recorte dos gabaritos**

* Após a digitalização, os gabaritos são isolados das provas (recorte das áreas de marcação).

### **4. Detecção e correção automática**

* Identificação das alternativas assinaladas usando **OpenCV** e **processamento de imagem**.
* Comparação das respostas dos alunos com o gabarito oficial.
* Geração de relatórios automáticos com os resultados.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **OpenCV** (processamento de imagens)
* **NumPy** (operações matriciais)
* **pdfplumber / reportlab** (manipulação de PDFs)
* **Pandas** (organização e análise de dados)

---

## 📂 Estrutura do Projeto

```
avaliacao-integrada/
│── data/                # PDFs e arquivos de entrada
│── gabaritos/           # Gabaritos oficiais
│── recortes/            # Recortes dos gabaritos digitalizados
│── resultados/          # Relatórios e correções
│── scripts/             # Códigos Python para cada etapa
│   │── etapa1_pdf.py
│   │── etapa2_preenchimento.py
│   │── etapa3_recorte.py
│   │── etapa4_correcao.py
│── README.md            # Documentação do projeto
```

---

## 📊 Benefícios

✅ Redução do tempo de correção
✅ Minimização de erros humanos
✅ Possibilidade de análises estatísticas detalhadas
✅ Escalabilidade para turmas grandes

---

## 🔮 Próximos Passos

* Implementar interface gráfica (GUI ou Web) para facilitar o uso.
* Integrar com banco de dados para armazenar resultados históricos.
* Criar dashboards interativos com **Power BI** ou **Streamlit**.

---
