
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
$ tree .         
.
├── data
│   ├── names_1A.xlsx
│   ├── names_1B.xlsx
│   ├── names_1C.xlsx
│   ├── names_1D.xlsx
│   ├── names_1E.xlsx
│   ├── names_1F.xlsx
│   ├── names_1G.xlsx
│   └── names.xlsx
├── master.py
├── model
│   └── main.pdf
├── README.md
├── source
│   ├── phase1
│   │   ├── generate_gabarito_name.py
│   │   ├── read_names.py
│   │   └── toolkit.py
│   ├── phase2
│   │   ├── fill_answer_all.py
│   │   ├── fill_answer_gabarito.py
│   │   └── toolkit.py
│   ├── phase3
│   │   ├── get_answersALL.py
│   │   └── toolkit.py
│   └── phase4
│       ├── compareAnswerToRight.py
│       ├── detectCirclesToAnswerCNT_ALL.py
│       ├── detectCirclesToAnswerCNT.py
│       ├── detectCirclesToAnswerMATH_ALL.py
│       ├── detectCirclesToAnswerMATH.py
│       └── toolkit.py
└── toolkit.py

7 directories, 26 files
```

---

## 📊 Benefícios

✅ Redução do tempo de 

✅ Minimização de erros humanos

✅ Possibilidade de análises estatísticas detalhadas

✅ Escalabilidade para turmas grandes

---

## 🔮 Próximos Passos

* Implementar interface gráfica (GUI ou Web) para facilitar o uso.
* Integrar com banco de dados para armazenar resultados históricos.
* Criar dashboards interativos com **Power BI** ou **Streamlit**.

---
