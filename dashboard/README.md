
---

# 📊 Porphyrio 2025 – Dashboard Acadêmico

Este dashboard foi desenvolvido em **Python + Streamlit** para análise de desempenho escolar, comparação entre turmas, análise por disciplina, engajamento dos alunos e cálculo automático de métricas bimestrais.

O sistema utiliza arquivos Excel fornecidos pelas escolas e transforma os dados em **visualizações interativas**, relatórios e comparativos individuais e coletivos.

---

## 🚀 Funcionalidades Principais

### 🔐 1. Login com Senha

Acesso protegido via senha definida no arquivo `secrets.toml`.

### 📁 2. Upload de Arquivos XLSX

Envie as planilhas originais da escola e o sistema processa automaticamente:

* Nomes dos alunos
* Notas por disciplina
* Médias
* Engajamento (EP, ES, EI etc.)
* Frequência
* Dados por bimestre

### 📊 3. Dashboard Geral

Inclui:

* Comparativo entre salas
* Médias gerais
* Métricas resumidas
* Tabelas e gráficos interativos

### 🏫 4. Análise por Disciplina

Veja rapidamente:

* Médias por turma
* Heatmap (cores invertidas: verde = bom, vermelho = baixo)
* Comparação entre salas para uma disciplina específica

### 👩‍🎓 5. Análise Individual do Aluno

Cada aluno possui um painel com:

* Comparativo **Aluno x Média da Turma**
* Desempenho por bimestre
* Engajamento e frequência
* Tabela de notas organizada

### 📌 6. Bimestres Organizados

Selecione qualquer bimestre com menus intuitivos:

* 1º Bimestre
* 2º Bimestre
* 3º Bimestre
* 4º Bimestre

---

## 📦 Estrutura da Pasta `dashboard/`

```
dashboard/
│
├── app.py                 # Aplicação principal Streamlit
├── utils.py               # Funções auxiliares
├── requirements.txt       # Dependências do projeto
├── sample_files/          # Exemplos de planilhas
├── .streamlit/
│   └── secrets.toml       # Senha para acesso
│
└── README.md              # Este documento
```

---

## ▶️ Como Executar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/profandrevsilva/porphyrio2025.git
cd porphyrio2025/dashboard
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure a senha

Edite o arquivo:

```
dashboard/.streamlit/secrets.toml
```

Exemplo:

```
password = "minhasenha123"
```

### 4. Execute o dashboard

```bash
$ streamlit run app.py --server.address 0.0.0.0 --server.port 8501

```

```
https:ipadress:8501
```


## 🧠 Tecnologias Utilizadas

* **Python 3.10+**
* **Streamlit**
* **Pandas**
* **Plotly Express**
* **NumPy**
* **Cloudflare Tunnel (opcional)**

---

## 🤝 Contribuição

Sinta-se à vontade para abrir:

* Issues
* Pull requests
* Sugestões de melhoria

---

## 📬 Contato

**Professor André Vieira**
Email: *adicione aqui se quiser*

---

Se quiser, posso:

✅ adicionar um **logo**
✅ colocar **screenshots** do dashboard
✅ gerar uma **versão em inglês**
Basta pedir!
