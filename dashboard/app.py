import streamlit as st
import pandas as pd
import re
import plotly.express as px

# -----------------------------------------------------------
# LOGIN SYSTEM (com botão e tela de login bonita)
# -----------------------------------------------------------
def check_password():

    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    # Se já logou, permite o acesso
    if st.session_state.password_correct:
        return True

    # TELA DE LOGIN
    st.markdown(
        """
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            height: 70vh;
        ">
            <div style="
                width: 420px;
                padding: 30px;
                border-radius: 12px;
                background: #7398ED;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                text-align: center;
            ">
                <h2>🔐 Login</h2>
                <p>Insira a senha para acessar o sistema</p>
        """,
        unsafe_allow_html=True,
    )

    password = st.text_input("Senha:", type="password", key="login_password")
    login_button = st.button("Entrar")

    if login_button:
        if "password" not in st.secrets:
            st.error("Nenhuma senha configurada no secrets.toml")
        else:
            if password == st.secrets["password"]:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ Senha incorreta.")

    st.markdown("</div></div>", unsafe_allow_html=True)

    return False


# -----------------------------------------------------------
# FUNÇÃO PARA EXTRAIR UM BIMESTRE
# -----------------------------------------------------------
def extract_bimestre_data(file, bimestre_label):
    try:
        df = pd.read_excel(file, header=None)
    except Exception as e:
        st.error(f"Erro ao ler {file.name}: {e}")
        return pd.DataFrame(columns=["Bimestre", "Turma", "Aluno", "Disciplina", "Nota"])

    # Identificar turma
    turma_info = ""
    for i in range(0, 15):
        linha = " ".join(str(x) for x in df.iloc[i].dropna().values)
        if "Turma:" in linha:
            turma_info = linha.strip()
            break

    # Identificar cabeçalho
    header_row_candidates = df.index[
        df.astype(str)
        .apply(lambda x: x.str.contains("ALUNO|Disciplina", case=False, na=False))
        .any(axis=1)
    ]
    header_row = header_row_candidates[0] if len(header_row_candidates) > 0 else 10
    data_start = header_row + 2

    # Construir cabeçalho
    disciplines = df.iloc[header_row].ffill()
    subheaders = df.iloc[header_row + 1].fillna("")
    columns = [f"{disc}_{sub}" if sub else str(disc) for disc, sub in zip(disciplines, subheaders)]
    df_data = df.iloc[data_start:].copy()
    df_data.columns = columns

    # -----------------------------------------------------------
    # DETECTAR COLUNA DE ALUNO
    # -----------------------------------------------------------
    forbidden = ["EP", "ES", "EI", "EE", "ENGAJAMENTO", "PARCIAL", "PRESENÇA", "FALTA"]

    possible_name_cols = [
        c for c in df_data.columns
        if re.search(r"aluno|nome", c, re.IGNORECASE)
        and all(f not in c.upper() for f in forbidden)
    ]

    if len(possible_name_cols) == 0:
        text_ratio = df_data.apply(lambda col: col.astype(str).str.contains(r"[A-Za-z]", regex=True).mean())
        name_col = text_ratio.idxmax()
    else:
        name_col = possible_name_cols[0]

    df_data["Aluno"] = df_data[name_col]
    df_data = df_data.dropna(subset=["Aluno"])

    # -----------------------------------------------------------
    # Filtrar notas
    # -----------------------------------------------------------
    nota_cols = [c for c in df_data.columns if re.search(r"(MÉDIA|_M$|M$|NOTA)", c, re.IGNORECASE)]
    if not nota_cols:
        return pd.DataFrame(columns=["Turma", "Aluno", "Disciplina", "Nota", "Bimestre"])

    melted = df_data.melt(id_vars=["Aluno"], value_vars=nota_cols,
                          var_name="Disciplina", value_name="Nota")

    melted["Disciplina"] = (
        melted["Disciplina"]
        .apply(lambda x: re.sub(r"(_M$|_MÉDIA|MÉDIA|NOTA)", "", x, flags=re.IGNORECASE))
        .apply(lambda x: x.split("\n")[0].strip())
    )

    melted["Bimestre"] = bimestre_label

    # -----------------------------------------------------------
    # SISTEMA SEM FUTUREWARNING:
    # 1. converte números
    # 2. converte conceitos ET/ES/EP
    # 3. aplica apenas a disciplinas específicas
    # -----------------------------------------------------------

    # Tentativa inicial de número (gera NaN quando é conceito)
    melted["Nota_num"] = pd.to_numeric(melted["Nota"], errors="coerce")

    conceitos = {"ET": 10, "ES": 5, "EP": 4}
    disciplinas_conceito = ["ESPORTE-MÚSICA-ARTE"]

    mask = melted["Disciplina"].str.upper().isin(disciplinas_conceito)

    melted.loc[mask, "Nota"] = (
        melted.loc[mask, "Nota"]
        .astype(str)
        .str.upper()
        .map(conceitos)
        .fillna(melted.loc[mask, "Nota_num"])
    )

    # Nota final numérica
    melted["Nota"] = pd.to_numeric(melted["Nota"], errors="coerce")
    melted.drop(columns=["Nota_num"], inplace=True)

    melted["Turma"] = turma_info if turma_info else "Turma Desconhecida"

    return melted[["Turma", "Aluno", "Disciplina", "Nota", "Bimestre"]]


# -----------------------------------------------------------
# FUNÇÃO DE COR PARA TABELAS
# -----------------------------------------------------------
def highlight_by_grade(val):
    if pd.isna(val):
        return None
    elif val < 5:
        return "background-color: #b30000; color: white;"
    elif val >= 7:
        return "background-color: #003366; color: white;"
    return None


# -----------------------------------------------------------
# FUNÇÃO DE GRÁFICO
# -----------------------------------------------------------
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


# -----------------------------------------------------------
# INÍCIO DO APP (Só roda se logado!)
# -----------------------------------------------------------
if not check_password():
    st.stop()

# -----------------------------------------------------------
# LAYOUT DO APP
# -----------------------------------------------------------
st.set_page_config(page_title="Dashboard", layout="wide")
st.title("PORPHYRIO DA PAZ GENERAL")
st.title("📊 Dashboard de Evolução das Notas - Conselho Bimestral")

st.markdown(
    """
Faça o upload dos arquivos XLSX dos bimestres (1º, 2º, 3º e 4º).
Você pode enviar **1**, **2**, **3** ou **4** arquivos.
"""
)

uploaded_files = st.file_uploader(
    "📂 Envie os arquivos XLSX",
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

    if "Bimestre" not in df.columns:
        st.error("❌ Arquivo inválido: falta coluna Bimestre.")
        st.stop()

    # Recalcular ordem dos bimestres por turma
    df["Bimestre_Num"] = df["Bimestre"].str.extract(r"(\d+)").astype(float)
    df["Bimestre"] = df.groupby("Turma")["Bimestre_Num"].rank(method="dense").astype(int).astype(str) + "º Bimestre"

    turma_opcoes = sorted(df["Turma"].dropna().unique())
    turma_selecionada = st.selectbox("🏫 Selecione a sala:", turma_opcoes)
    df_turma = df[df["Turma"] == turma_selecionada]

    # -----------------------------------------------------------
    # ABAS
    # -----------------------------------------------------------
    tab_turma, tab_aluno, tab_heat = st.tabs([
        "📈 Por Disciplina (Turma)",
        "👩‍🎓 Por Aluno",
        "🔥 Comparativo entre Salas (Heatmap)"
    ])

    # -----------------------------------------------------------
    # ABA 1 - POR DISCIPLINA
    # -----------------------------------------------------------
    with tab_turma:
        st.subheader("📊 Evolução das Médias da Turma por Disciplina")

        bimestres_disponiveis_turma = sorted(df_turma["Bimestre"].unique())
        bimestre_turma_sel = st.selectbox(
            "Selecione o Bimestre:",
            options=["Todos os Bimestres"] + bimestres_disponiveis_turma,
            index=0,
        )

        if bimestre_turma_sel != "Todos os Bimestres":
            df_turma_filtrado = df_turma[df_turma["Bimestre"] == bimestre_turma_sel]
        else:
            df_turma_filtrado = df_turma

        df_media = (
            df_turma_filtrado.groupby(["Disciplina", "Bimestre"], as_index=False)["Nota"]
            .mean()
            .round(2)
        )

        titulo = (
            f"Médias da Turma {turma_selecionada} - {bimestre_turma_sel}"
            if bimestre_turma_sel != "Todos os Bimestres"
            else f"Médias da Turma {turma_selecionada} por Disciplina"
        )

        st.plotly_chart(plot_notas(df_media, titulo), use_container_width=True)

        st.subheader("📋 Tabela de Médias por Disciplina")

        pivot = df_media.pivot_table(index="Disciplina", columns="Bimestre", values="Nota")
        styled = pivot.style.format("{:.1f}").map(highlight_by_grade)
        st.dataframe(styled)

    # -----------------------------------------------------------
    # ABA 2 - POR ALUNO
    # -----------------------------------------------------------
    with tab_aluno:
        st.subheader("👩‍🎓 Comparativo: Aluno x Média da Turma")

        alunos = sorted(df_turma["Aluno"].dropna().unique())
        aluno_selecionado = st.selectbox("Selecione o aluno:", alunos)

        df_aluno = df_turma[df_turma["Aluno"] == aluno_selecionado]
        df_media_turma = df_turma.groupby(["Disciplina", "Bimestre"], as_index=False)["Nota"].mean().round(2)

        st.plotly_chart(plot_notas(df_media_turma, f"Média da Turma {turma_selecionada}"), use_container_width=True)
        st.plotly_chart(plot_notas(df_aluno, f"Evolução das Notas - {aluno_selecionado}"), use_container_width=True)

        pivot_aluno = df_aluno.pivot_table(index="Disciplina", columns="Bimestre", values="Nota")
        styled_aluno = pivot_aluno.style.format("{:.1f}").map(highlight_by_grade)
        st.dataframe(styled_aluno)

    # -----------------------------------------------------------
    # ABA 3 - HEATMAP ENTRE SALAS
    # -----------------------------------------------------------
    with tab_heat:
        st.subheader("🔥 Comparativo entre Salas")

        bimestres_disponiveis = sorted(df["Bimestre"].unique())
        bimestre_selecionado = st.selectbox("Selecione o Bimestre:", bimestres_disponiveis)

        df_bim = df[df["Bimestre"] == bimestre_selecionado].copy()

        df_bim["Turma"] = (
            df_bim["Turma"]
            .str.replace(r"INTEGRAL 9H ANUAL", "", case=False, regex=True)
            .str.strip()
        )

        todas_disciplinas = sorted(df["Disciplina"].dropna().unique())
        todas_turmas = sorted(df_bim["Turma"].dropna().unique())

        heatmap_data = (
            df_bim.groupby(["Disciplina", "Turma"])["Nota"]
            .mean()
            .unstack("Turma")
            .reindex(todas_disciplinas)
            .reindex(columns=todas_turmas)
        )

        fig_heat = px.imshow(
            heatmap_data,
            color_continuous_scale=[
                (0.0, "#8B0000"),
                (0.4, "#A16D63"),
                (0.5, "#7398ED"),
                (0.6, "#4F6DB2"),
                (1.0, "#006400"),
            ],
            zmin=0,
            zmax=10,
            aspect="auto",
            title=f"Comparativo de Médias - {bimestre_selecionado}",
        )

        fig_heat.update_layout(height=900, width=1600, xaxis_tickangle=45)
        st.plotly_chart(fig_heat, use_container_width=True)

    # -----------------------------------------------------------
    # DOWNLOAD
    # -----------------------------------------------------------
    st.download_button(
        "📥 Baixar dados consolidados (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        "dados_conselho.csv",
        "text/csv",
    )

else:
    st.info("📎 Envie entre **1 e 4 arquivos XLSX**.")
