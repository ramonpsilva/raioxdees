from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


st.title("Participação de departamento por curso de graduação")


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    df["semestre"] = df["semestre"].astype(str)
    return df


data_file = Path(__file__).with_name("data/percentualParticipacaoEncargosDepartamentosCurso_concatenados.xlsx")

if not data_file.exists():
    st.error(
        "Arquivo data/percentualParticipacaoEncargosDepartamentosCurso_concatenados.xlsx "
        "não encontrado na pasta do projeto."
    )
    st.stop()

df = load_data(str(data_file))

DEPTS_EE = {"EES", "EHR", "ELE", "ELT", "EMA", "EMC", "EMN", "EMT", "ENU", "EPD", "EQM", "ESA", "ETG"}

todos_departamentos = sorted(df["departamento"].dropna().unique().tolist())

st.sidebar.header("Filtros")

escopo = st.sidebar.radio(
    "Escopo",
    options=["Todos", "Escola de Engenharia"],
    index=1,
)

if escopo == "Escola de Engenharia":
    departamentos = sorted(d for d in todos_departamentos if d in DEPTS_EE)
else:
    departamentos = todos_departamentos

departamento_sel = st.sidebar.radio(
    "Selecione o departamento",
    options=departamentos,
)

# Resetar a seleção de cursos quando o departamento muda
if st.session_state.get("departamento_anterior") != departamento_sel:
    st.session_state["departamento_anterior"] = departamento_sel
    st.session_state["cursos_sel"] = None

df_dept = df[df["departamento"] == departamento_sel]

cursos_ativos = (
    df_dept.groupby("curso")["participacao"].sum()
    .loc[lambda s: s > 0]
    .index.tolist()
)
cursos = sorted(cursos_ativos)

if st.session_state.get("cursos_sel") is None:
    st.session_state["cursos_sel"] = cursos

cursos_sel = st.sidebar.multiselect(
    "Selecione os cursos",
    options=cursos,
    default=st.session_state["cursos_sel"],
    key="cursos_sel",
)

if not cursos_sel:
    st.info("Selecione ao menos um curso para exibir o gráfico.")
    st.stop()

df_dept_cursos = df_dept[df_dept["curso"].isin(cursos_sel)]

semestres_all = sorted(df_dept_cursos["semestre"].unique().tolist())
sem_min = semestres_all[0]
sem_max = semestres_all[-1]

if sem_min == sem_max:
    selected_sem_range = (sem_min, sem_max)
    st.sidebar.caption(f"Semestre disponível: {sem_min}")
else:
    selected_sem_range = st.sidebar.select_slider(
        "Intervalo de semestres",
        options=semestres_all,
        value=(sem_min, sem_max),
    )

df_plot = df_dept_cursos[
    (df_dept_cursos["semestre"] >= selected_sem_range[0])
    & (df_dept_cursos["semestre"] <= selected_sem_range[1])
]

semestres_order = sorted(df_plot["semestre"].unique().tolist())

selection = alt.selection_point(fields=["curso"], bind="legend")

chart = (
    alt.Chart(df_plot)
    .mark_line(point=True)
    .encode(
        x=alt.X("semestre:O", sort=semestres_order, title="Semestre", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("participacao:Q", title="Participação (%)"),
        color=alt.Color("curso:N", title="Curso"),
        opacity=alt.condition(selection, alt.value(1.0), alt.value(0.1)),
        tooltip=["semestre", "departamento", "codigo", "curso", "participacao"],
    )
    .properties(
        height=600,
        title=f"Participação do departamento do departamento {departamento_sel} por curso ao longo dos semestres",
    )
    .add_params(selection)
    .interactive()
)

st.altair_chart(chart, use_container_width=True)

