import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Dashboard de Entregas", layout="wide")

arquivo = "Planilha Anual HF.xlsx"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main-title {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 17px;
    color: #666;
    margin-bottom: 25px;
}

.metric-card {
    background-color: rgba(240, 242, 246, 0.65);
    border-radius: 14px;
    padding: 18px;
    border: 1px solid rgba(180, 180, 180, 0.25);
}

.metric-label {
    font-size: 15px;
    color: #666;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
}

.section-text {
    color: #666;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

def carregar_dados():
    abas = pd.ExcelFile(arquivo).sheet_names
    registros = []

    for mes in abas:
        tabela = pd.read_excel(arquivo, sheet_name=mes, header=None)

        for i in range(3, len(tabela)):
            data = tabela.iloc[i, 0]

            for j in range(1, len(tabela.columns), 4):
                motoboy = tabela.iloc[i, j] if j < len(tabela.columns) else None
                loja = tabela.iloc[i, j + 1] if j + 1 < len(tabela.columns) else None
                nota = tabela.iloc[i, j + 2] if j + 2 < len(tabela.columns) else None

                if pd.notna(motoboy) and pd.notna(loja):
                    registros.append({
                        "DATA": data,
                        "MES": mes,
                        "MOTOBOY": str(motoboy).strip().title(),
                        "LOJA": str(loja).strip().title(),
                        "NOTA": nota
                    })

    df = pd.DataFrame(registros)
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df["NOTA"] = pd.to_numeric(df["NOTA"], errors="coerce")
    df = df.dropna(subset=["DATA"])

    return df

df = carregar_dados()

st.markdown('<div class="main-title">Dashboard de Entregas</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Acompanhe as entregas registradas durante o ano de forma simples e visual.</div>',
    unsafe_allow_html=True
)

st.sidebar.title("Filtros do painel")
st.sidebar.write("Use os filtros abaixo para explorar os dados com mais facilidade.")

meses_disponiveis = sorted(df["MES"].unique())
lojas_disponiveis = sorted(df["LOJA"].unique())
motoboys_disponiveis = sorted(df["MOTOBOY"].unique())

meses = st.sidebar.multiselect(
    "📅 Escolha os meses",
    options=meses_disponiveis,
    default=meses_disponiveis
)

loja = st.sidebar.selectbox(
    "🏪 Filtrar por loja",
    ["Todas"] + lojas_disponiveis
)

motoboy = st.sidebar.selectbox(
    "🏍️ Filtrar por motoboy",
    ["Todos"] + motoboys_disponiveis
)

data_inicio = df["DATA"].min()
data_fim = df["DATA"].max()

periodo = st.sidebar.date_input(
    "🗓️ Escolha o período",
    value=(data_inicio, data_fim),
    min_value=data_inicio,
    max_value=data_fim
)

top_n = st.sidebar.number_input(
    "⭐ Quantos itens mostrar no ranking?",
    min_value=1,
    max_value=50,
    value=10,
    step=1
)

st.sidebar.info("Dica: altere os filtros para comparar meses, lojas e motoboys.")

df_filtrado = df[df["MES"].isin(meses)]

if loja != "Todas":
    df_filtrado = df_filtrado[df_filtrado["LOJA"] == loja]

if motoboy != "Todos":
    df_filtrado = df_filtrado[df_filtrado["MOTOBOY"] == motoboy]

if len(periodo) == 2:
    inicio = pd.to_datetime(periodo[0])
    fim = pd.to_datetime(periodo[1])
    df_filtrado = df_filtrado[
        (df_filtrado["DATA"] >= inicio) &
        (df_filtrado["DATA"] <= fim)
    ]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

st.subheader("Resumo geral")
st.markdown('<div class="section-text">Uma visão rápida dos dados selecionados nos filtros.</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Entregas</div>
            <div class="metric-value">{len(df_filtrado)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Meses</div>
            <div class="metric-value">{df_filtrado['MES'].nunique()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Lojas</div>
            <div class="metric-value">{df_filtrado['LOJA'].nunique()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Motoboys</div>
            <div class="metric-value">{df_filtrado['MOTOBOY'].nunique()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

aba1, aba2, aba3 = st.tabs(["Visão geral", "Rankings", "Dados"])

with aba1:
    st.subheader("Entregas por mês")
    st.markdown('<div class="section-text">Compare a movimentação mensal de entregas.</div>', unsafe_allow_html=True)

    entregas_mes = df_filtrado["MES"].value_counts().reindex(meses_disponiveis).dropna()

    fig1, ax1 = plt.subplots(figsize=(6, 3))
    entregas_mes.plot(kind="bar", ax=ax1)

    ax1.set_title("Quantidade de entregas por mês")
    ax1.set_xlabel("Mês")
    ax1.set_ylabel("Entregas")
    ax1.tick_params(axis="x", rotation=35)

    plt.tight_layout()
    st.pyplot(fig1, use_container_width=False)

    st.subheader("Evolução das entregas")
    st.markdown('<div class="section-text">Veja como as entregas variaram ao longo do período filtrado.</div>', unsafe_allow_html=True)

    entregas_dia = df_filtrado.groupby("DATA").size()

    fig2, ax2 = plt.subplots(figsize=(6, 3))
    entregas_dia.plot(kind="line", marker="o", ax=ax2)

    ax2.set_title("Entregas por dia")
    ax2.set_xlabel("Data")
    ax2.set_ylabel("Entregas")

    plt.tight_layout()
    st.pyplot(fig2, use_container_width=False)

    st.subheader("Participação das principais lojas")
    st.markdown('<div class="section-text">Veja quais lojas mais aparecem dentro dos filtros selecionados.</div>', unsafe_allow_html=True)

    coluna_pizza, coluna_texto = st.columns([1, 2])

    with coluna_pizza:
        lojas_pizza = df_filtrado["LOJA"].value_counts().head(5)

        fig3, ax3 = plt.subplots(figsize=(3.2, 3.2))
        lojas_pizza.plot(kind="pie", autopct="%1.1f%%", ax=ax3)

        ax3.set_ylabel("")
        ax3.set_title("Lojas")

        plt.tight_layout()
        st.pyplot(fig3, use_container_width=False)

    with coluna_texto:
        st.write("As lojas abaixo representam as maiores participações no período selecionado.")

        tabela_lojas = lojas_pizza.reset_index()
        tabela_lojas.columns = ["Loja", "Entregas"]

        st.dataframe(tabela_lojas, use_container_width=True)

with aba2:
    st.subheader("Rankings")
    st.markdown('<div class="section-text">Acompanhe quem mais movimentou entregas dentro dos filtros escolhidos.</div>', unsafe_allow_html=True)

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        lojas_top = df_filtrado["LOJA"].value_counts().head(top_n)

        fig4, ax4 = plt.subplots(figsize=(5, 3))
        lojas_top.sort_values().plot(kind="barh", ax=ax4)

        ax4.set_title(f"Top {top_n} lojas")
        ax4.set_xlabel("Entregas")
        ax4.set_ylabel("Loja")

        plt.tight_layout()
        st.pyplot(fig4, use_container_width=True)

    with col_graf2:
        motoboys_top = df_filtrado["MOTOBOY"].value_counts().head(top_n)

        fig5, ax5 = plt.subplots(figsize=(5, 3))
        motoboys_top.sort_values().plot(kind="barh", ax=ax5)

        ax5.set_title(f"Top {top_n} motoboys")
        ax5.set_xlabel("Entregas")
        ax5.set_ylabel("Motoboy")

        plt.tight_layout()
        st.pyplot(fig5, use_container_width=True)

    st.subheader("Entregas por motoboy e loja")
    st.markdown('<div class="section-text">Tabela cruzada para entender a relação entre motoboys e lojas.</div>', unsafe_allow_html=True)

    tabela_cruzada = pd.crosstab(df_filtrado["MOTOBOY"], df_filtrado["LOJA"])

    st.dataframe(tabela_cruzada, use_container_width=True)

with aba3:
    st.subheader("Dados filtrados")
    st.markdown('<div class="section-text">Aqui aparecem os registros conforme os filtros aplicados.</div>', unsafe_allow_html=True)

    st.dataframe(df_filtrado, use_container_width=True)