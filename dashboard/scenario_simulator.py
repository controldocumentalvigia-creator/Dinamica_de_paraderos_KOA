import streamlit as st
from config import STOPS, ROUTES
from core.scenarios import evaluate_scenario

def render(df):
    st.subheader("Simulador de escenarios")
    c1, c2 = st.columns(2)
    with c1:
        route = st.selectbox("Ruta", ROUTES)
        stops = st.multiselect("Paraderos", STOPS, default=["VIRREY"])
    with c2:
        demand = st.slider("Variación esperada de demanda (%)", -50, 100, 0)
        minutes = st.slider("Minutos adicionales estimados", 0, 30, 0)
    if not stops:
        st.warning("Seleccione al menos un paradero.")
        return
    result = evaluate_scenario(df, route, stops, demand, minutes)
    st.dataframe([result], hide_index=True, use_container_width=True)
    if result["evidencia"] == "Baja":
        st.warning(result["nota"])
