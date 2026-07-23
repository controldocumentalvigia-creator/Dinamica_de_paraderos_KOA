import plotly.express as px
import streamlit as st
from core.metrics import monthly_summary, demand_summary
from ai.conclusions import generate_conclusions
from ai.recommendations import generate_recommendations
from dashboard.common import chart

def render(df):
    st.subheader("Resumen ejecutivo")
    monthly = monthly_summary(df)
    demand = demand_summary(df)
    c1, c2 = st.columns(2)
    with c1:
        chart(px.line(monthly, x="mes", y="usuarios", markers=True, title="Usuarios por mes"), "exec-users")
    with c2:
        chart(px.bar(demand, x="recorrido", y="usuarios", text_auto=True, title="Demanda acumulada por recorrido"), "exec-demand")

    st.markdown("#### Hallazgos automáticos")
    for conclusion in generate_conclusions(df):
        st.markdown(f"- {conclusion}")

    st.markdown("#### Plan de acción")
    st.dataframe(generate_recommendations(df), hide_index=True, use_container_width=True)
