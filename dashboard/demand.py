import plotly.express as px
import streamlit as st
from core.metrics import demand_summary
from dashboard.common import chart, table

def render(df):
    st.subheader("Demanda")
    summary = demand_summary(df)
    table(summary, {"promedio_usuarios": "{:.2f}"})
    afternoon = df[df["jornada"] == "TARDE"]
    daily = afternoon.groupby(["fecha", "recorrido"], as_index=False)["usuarios"].sum()
    c1, c2 = st.columns(2)
    with c1:
        chart(px.bar(summary, x="recorrido", y="usuarios", text_auto=True, title="Usuarios acumulados"), "demand-total")
    with c2:
        chart(px.bar(summary, x="recorrido", y=["efectivos", "sin_usuarios"], barmode="group",
                     title="Recorridos efectivos vs. sin usuarios"), "demand-status")
    chart(px.line(daily, x="fecha", y="usuarios", color="recorrido", markers=True,
                  title="Evolución diaria de usuarios"), "demand-daily")
