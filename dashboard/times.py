import plotly.express as px
import streamlit as st
from core.metrics import combinations
from dashboard.common import chart, table

def render(df):
    st.subheader("Combinaciones y tiempos")
    combo = combinations(df)
    table(combo, {
        "usuarios_promedio": "{:.2f}", "tiempo_promedio": "{:.1f}",
        "mediana": "{:.1f}", "p90": "{:.1f}", "p95": "{:.1f}",
        "minimo": "{:.1f}", "maximo": "{:.1f}", "desviacion": "{:.1f}",
    })
    effective = df[(df["jornada"] == "TARDE") & (df["estado_operativo"] == "EFECTIVO")]
    c1, c2 = st.columns(2)
    with c1:
        chart(px.box(effective, x="recorrido", y="trayecto", points="outliers",
                     title="Distribución de tiempos por recorrido"), "time-box")
    with c2:
        chart(px.scatter(combo, x="tiempo_promedio", y="usuarios_promedio",
                         size="recorridos", color="combinacion_paradas",
                         facet_col="recorrido", hover_data=["p90", "p95"],
                         title="Tiempo vs. demanda por combinación"), "time-demand")
