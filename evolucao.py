from pathlib import Path
from io import BytesIO

import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.title("Evolução Docente por Departamento da EE")


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path)


def build_svg_plot(data: pd.DataFrame, departments: list[str], year_ticks: list[int]) -> bytes:
	fig, ax = plt.subplots(figsize=(11, 6))

	for department in departments:
		ax.plot(
			data.index.astype(int),
			data[department].astype(float),
			marker="o",
			label=department,
		)

	ax.set_xlabel("Ano")
	ax.set_ylabel("# docentes")
	ax.set_xticks(year_ticks)
	ax.set_xticklabels([str(year) for year in year_ticks], rotation=90)
	ax.legend(loc="best")
	ax.grid(alpha=0.3)
	fig.tight_layout()

	svg_buffer = BytesIO()
	fig.savefig(svg_buffer, format="svg")
	plt.close(fig)
	return svg_buffer.getvalue()


data_file = Path(__file__).with_name("evolucao_docente.xlsx")

if not data_file.exists():
	st.error("Arquivo evolucao_docente.xlsx não encontrado na pasta do projeto.")
	st.stop()

df = load_data(str(data_file))

# A coluna "ENG" é criada como a soma das colunas de departamentos, ignorando valores não numéricos das colunas 
# "Ano" e "UFMG". Se a coluna "ENG" já existir, ela será sobrescrita.
df["ENG"] = df.drop(columns=["Ano", "UFMG"], errors="ignore").apply(
    pd.to_numeric, errors="coerce"
).sum(axis=1)   

if df.shape[1] < 3:
	st.error(
		"O arquivo precisa ter pelo menos 3 colunas: Ano e duas colunas de departamentos."
	)
	st.stop()

if "Ano" not in df.columns:
	st.error("A coluna Ano não foi encontrada no arquivo.")
	st.stop()

ano_col = "Ano"
departments = [col for col in df.columns if col != ano_col]

if not departments:
	st.error("Nenhuma coluna de departamento foi encontrada além de Ano.")
	st.stop()

df[ano_col] = pd.to_numeric(df[ano_col], errors="coerce")
valid_years = df[ano_col].dropna()

if valid_years.empty:
	st.error("A coluna de Ano não possui valores numéricos válidos.")
	st.stop()

year_min = int(valid_years.min())
year_max = int(valid_years.max())

st.sidebar.header("Filtros")
selected_departments = st.sidebar.multiselect(
	"Selecione os departamentos para plotar",
	options=sorted(departments),
	default=departments[: min(5, len(departments))],
)

if year_min == year_max:
	selected_year_range = (year_min, year_max)
	st.sidebar.caption(f"Ano disponível: {year_min}")
else:
	selected_year_range = st.sidebar.slider(
		"Intervalo de anos",
		min_value=year_min,
		max_value=year_max,
		value=(year_min, year_max),
	)

if not selected_departments:
	st.info("Selecione pelo menos um departamento para visualizar o gráfico.")
	st.stop()

filtered = df[[ano_col] + selected_departments].copy()
filtered = filtered.dropna(subset=[ano_col])
filtered = filtered[
	(filtered[ano_col] >= selected_year_range[0])
	& (filtered[ano_col] <= selected_year_range[1])
]

if filtered.empty:
	st.warning("Não há dados válidos para os filtros selecionados.")
	st.stop()

filtered[ano_col] = filtered[ano_col].astype("Int64")

for department in selected_departments:
	filtered[department] = (
		pd.to_numeric(filtered[department], errors="coerce")
		.round(0)
		.astype("Int64")
	)

plot_data = filtered.set_index(ano_col).sort_index()

if plot_data[selected_departments].dropna(how="all").empty:
	st.warning("As colunas selecionadas não possuem valores numéricos válidos para plotagem.")
	st.stop()

# st.subheader("Gráfico de linhas")
plot_data_long = (
	plot_data[selected_departments]
	.reset_index()
	.melt(id_vars=[ano_col], var_name="Departamento", value_name="Valor")
	.dropna(subset=["Valor"])
)
plot_data_long["Valor"] = plot_data_long["Valor"].astype("Int64")
year_ticks = list(range(selected_year_range[0], selected_year_range[1] + 1))

selection = alt.selection_point(fields=["Departamento"], bind="legend")

chart = (
	alt.Chart(plot_data_long)
	.mark_line(point=True)
	.encode(
		x=alt.X(f"{ano_col}:Q", axis=alt.Axis(format="d", values=year_ticks)),
		y=alt.Y("Valor:Q", title="# docentes", axis=alt.Axis(format="d")),
		color=alt.Color("Departamento:N", title="Departamento"),
		opacity=alt.condition(selection, alt.value(1.0), alt.value(0.1)),
		tooltip=[
			alt.Tooltip(f"{ano_col}:Q", format="d"),
			alt.Tooltip("Departamento:N"),
			alt.Tooltip("Valor:Q", format="d"),
		],
	)
	.properties(height=450)
	.add_params(selection)
	.interactive()
)

st.altair_chart(chart, use_container_width=True)

svg_data = build_svg_plot(plot_data[selected_departments], selected_departments, year_ticks)
st.sidebar.download_button(
	label="Baixar gráfico (SVG)",
	data=svg_data,
	file_name="evolucao_docente_grafico.svg",
	mime="image/svg+xml",
)

filtered_sorted = filtered.sort_values([ano_col])
csv_data = filtered_sorted.to_csv(index=False).encode("utf-8-sig")
st.sidebar.download_button(
	label="Baixar dados filtrados (CSV)",
	data=csv_data,
	file_name="evolucao_docente_filtrada.csv",
	mime="text/csv",
)

with st.expander("Visualizar dados filtrados"):
	st.dataframe(filtered_sorted, use_container_width=True)