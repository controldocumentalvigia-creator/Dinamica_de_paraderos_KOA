import plotly.express as px
import streamlit as st
from core.metrics import punctuality_summary
from dashboard.common import chart, table

def render(df):
    st.subheader("Puntualidad")
    summary = punctuality_summary(df)
    table(summary, {
        "puntual_0_5": "{:.1%}", "puntual_pm5": "{:.1%}",
        "anticipadas": "{:.1%}", "retraso_mayor_5": "{:.1%}",
        "desviacion_promedio": "{:.1f}", "desviacion_p90": "{:.1f}",
    })
    valid = df.dropna(subset=["desv_min"])
    c1, c2 = st.columns(2)
    with c1:
        chart(px.histogram(valid, x="desv_min", color="recorrido", facet_row="jornada",
                           nbins=35, title="Distribución de desviaciones"), "punct-hist")
    with c2:
        fig = px.bar(summary, x="recorrido", y="puntual_0_5", color="jornada",
                     barmode="group", text_auto=".1%", title="Puntualidad oficial")
        fig.update_yaxes(tickformat=".0%")
        chart(fig, "punct-bar")
