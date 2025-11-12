import streamlit as st
import pandas as pd
import re
import plotly.express as px

# ----------------------------
# Função para extrair dados de um bimestre
# ----------------------------
def extract_bimestre_data(file, bimestre_label):
    try:
        df = pd.read_excel(file, header=None)
    except Exception as e:
        st.error(f"Erro ao ler {file.name}: {e}")
        return pd.DataFrame(columns=["Bimestre", "Turma", "Aluno", "Disciplina", "Nota"])

    # Identificar turma (linha contendo "Turma:")
    turma_info = ""
    for i in range(0, 15):
        linha = " ".join(str(x) for x in df.iloc[i].dropna().values)
        if "Turma:" in linha:
            turma_info = linha.strip()
            break

    # Detectar automaticamente a linha do cabeçalho (que contém "ALUNO" ou "Disciplina")
    header_row_candidates = df.index[
        df.astype(str)
        .apply(lambda x: x.str.contains("ALUNO|Disciplina", case=False, na=False))
        .any(axis=1)
    ]
    header_row = header_row_candidates[0] if len(header_row_candidates) > 0 else 10
    data_start = header_row + 2

    # Construir cabeçalho completo
    disciplines = df.iloc[header_row].ffill()
    subheaders = df.iloc[header_row + 1].fillna("")
    columns = [f"{disc}_{sub}" if sub else str(disc) for disc, sub in zip(disciplines, subheaders)]

    df_data = df.iloc[data_start:].copy()
    df_data.columns = columns

    # Coluna de aluno
    possible_name_cols = [c for c in df_data.columns if re.search(r"aluno|nome", c, re.IGNORECASE)]
    if possible_name_cols:
        name_col = possible_name_cols[0]
    else:
        name_col = df_data.columns[0]

    df_data["Aluno"] = df_data[name_col]
    df_data = df_data.dropna(subset=["Aluno"])

    # Filtrar colunas de notas
    nota_cols = [c for c in df_data.columns if re.search(r"(MÉDIA|_M$|M$|NOTA)", c, re.IGNORECASE)]
    if not nota_cols:
        return pd.DataFrame(columns=["Turma", "Aluno", "Disciplina", "Nota", "Bimestre"])

    melted = df_data.melt(id_vars=["Aluno"], value_vars=nota_cols, var_name="Disciplina", value_name="Nota")

    # Limpeza de nomes
    melted["Disciplina"] = (
        melted["Disciplina"]
        .apply(lambda x: re.sub(r"(_M$|_MÉDIA|MÉDIA|NOTA)", "", x, flags=re.IGNORECASE))
        .apply(lambda x: x.split("\n")[0].strip())
    )

    melted["Bimestre"] = bimestre_label
    melted["Nota"] = pd.to_numeric(melted["Nota"], errors="coerce")
    melted["Turma"] = turma_info if turma_info else "Turma Desconhecida"

    return melted[["Turma", "Aluno", "Disciplina", "Nota", "Bimestre"]]


# ----------------------------
# Funções auxiliares
# ----------------------------
def highlight_by_grade(val):
    if pd.isna(val):
        return None
    elif val < 5:
        return "background-color: #b30000; color: white;"  # vermelho escuro
    elif val >= 7:
        return "background-color: #003366; color: white;"  # azul escuro
    return None


def plot_notas(df, titulo):
    fig = px.bar(
        df,
        x="Disciplina",
        y="Nota",
        color="Bimestre",
        barmode="group",
        text_auto=True,
        title=titulo,
    )
    fig.add_hline(
        y=5,
        line_dash="dash",
        line_color="red",
        annotation_text="Média 5.0",
        annotation_position="top left",
    )
    fig.update_layout(
        xaxis_tickangle=45,
        height=600,
        yaxis_title="Nota",
        legend_title_text="Bimestre",
        title_font_size=18,
    )
    return fig


# ----------------------------
# STREAMLIT APP
# ----------------------------
st.set_page_config(page_title="Dashboard", layout="wide")
st.title("PORPHYRIO DA PAZ GENERAL")
st.title("📊 Dashboard de Evolução das Notas - Conselho Bimestral")
st.markdown(
    """
Faça o upload dos arquivos XLSX dos bimestres (1º, 2º, 3º e 4º).
Você pode enviar **1**, **2**, **3** ou **4** arquivos — o app ajusta automaticamente a análise.
"""
)

uploaded_files = st.file_uploader(
    "📂 Envie os arquivos XLSX dos bimestres disponíveis",
    type=["xlsx"],
    accept_multiple_files=True,
)

if len(uploaded_files) > 0:
    uploaded_files = sorted(uploaded_files, key=lambda x: x.name)

    dados = []
    for i, file in enumerate(uploaded_files, start=1):
        with st.spinner(f"Processando {file.name}..."):
            bimestre_label = f"{i}º Bimestre"
            bimestre_data = extract_bimestre_data(file, bimestre_label)
            dados.append(bimestre_data)

    df = pd.concat(dados, ignore_index=True)

    # Segurança — verificar se há coluna Bimestre
    if "Bimestre" not in df.columns:
        st.error("❌ Nenhum arquivo válido encontrado com a coluna 'Bimestre'. Verifique o formato dos arquivos.")
        st.stop()

    # Corrigir numeração dos bimestres por turma
    df["Bimestre_Num"] = df["Bimestre"].str.extract(r"(\d+)").astype(float)
    df["Bimestre"] = df.groupby("Turma")["Bimestre_Num"].rank(method="dense").astype(int).astype(str) + "º Bimestre"

    turma_opcoes = sorted(df["Turma"].dropna().unique())
    turma_selecionada = st.selectbox("🏫 Selecione a sala (turma):", turma_opcoes)
    df_turma = df[df["Turma"] == turma_selecionada]

    # Abas
    tab_turma, tab_aluno = st.tabs(["📈 Por Disciplina (Turma)", "👩‍🎓 Por Aluno"])

    # ----------------------------
    # ABA 1 - POR DISCIPLINA
    # ----------------------------
    with tab_turma:
        df_media = df_turma.groupby(["Disciplina", "Bimestre"], as_index=False)["Nota"].mean().round(2)

        st.subheader("📊 Evolução das Médias da Turma por Disciplina")
        fig_turma = plot_notas(df_media, f"Médias da Turma {turma_selecionada} por Disciplina")
        st.plotly_chart(fig_turma, use_container_width=True)

        st.subheader("📋 Tabela de Médias por Disciplina")

        # CSS para reduzir o espaçamento
        st.markdown(
            """
            <style>
            .stDataFrame td, .stDataFrame th {
                padding-top: 2px !important;
                padding-bottom: 2px !important;
                padding-left: 6px !important;
                padding-right: 6px !important;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        pivot = df_media.pivot_table(index="Disciplina", columns="Bimestre", values="Nota")
        styled = pivot.style.format("{:.1f}").map(highlight_by_grade)
        st.dataframe(styled)

    # ----------------------------
    # ABA 2 - POR ALUNO
    # ----------------------------
    with tab_aluno:
        st.subheader("👩‍🎓 Comparativo: Aluno x Média da Turma")

        possible_name_cols = [c for c in df_turma.columns if re.search(r"aluno|nome", c, re.IGNORECASE)]
        nome_col = possible_name_cols[0] if possible_name_cols else "Aluno"

        alunos = sorted(df_turma[nome_col].dropna().unique())
        aluno_selecionado = st.selectbox("Selecione o aluno:", alunos)

        df_aluno = df_turma[df_turma[nome_col] == aluno_selecionado]

        # Gráfico média da turma
        df_media_turma = df_turma.groupby(["Disciplina", "Bimestre"], as_index=False)["Nota"].mean().round(2)
        st.markdown("#### 📘 Média da Turma por Disciplina")
        fig_turma_media = plot_notas(df_media_turma, f"Média da Turma {turma_selecionada}")
        st.plotly_chart(fig_turma_media, use_container_width=True)

        # Gráfico do aluno
        st.markdown(f"#### 👩‍🎓 Notas do Aluno: {aluno_selecionado}")
        fig_aluno = plot_notas(df_aluno, f"Evolução das Notas - {aluno_selecionado}")
        st.plotly_chart(fig_aluno, use_container_width=True)

        # Tabela do aluno
        st.subheader("📋 Tabela de Notas do Aluno")
        pivot_aluno = df_aluno.pivot_table(index="Disciplina", columns="Bimestre", values="Nota")
        styled_aluno = pivot_aluno.style.format("{:.1f}").map(highlight_by_grade)
        st.dataframe(styled_aluno)

    # ----------------------------
    # DOWNLOAD CSV
    # ----------------------------
    st.download_button(
        "📥 Baixar dados consolidados (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        "dados_conselho.csv",
        "text/csv",
    )

else:
    st.info("📎 Envie entre **1 e 4 arquivos XLSX**, um para cada bimestre disponível.")
