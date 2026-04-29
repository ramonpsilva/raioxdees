import streamlit as st

st.set_page_config(
    page_title="Dashboard DEES",
    layout="wide",
    page_icon="📊"
)
st.markdown(
    "<style>div.block-container { padding-top: 1rem; }</style>",
    unsafe_allow_html=True,
)

pg = st.navigation([
    st.Page("evolucao.py",    title="Evolução Docente",  icon="📈"),
    st.Page("participacao.py", title="Participação na Graduação",      icon="📊"),
    st.Page("contribuicao.py", title="Percentual de Encargos",      icon="📉"),
    st.Page("dashboarddees.py", title="Dashboard DEES",      icon="📉"),
])
pg.run()
