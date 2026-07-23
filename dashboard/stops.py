import pandas as pd
import plotly.express as px
import streamlit as st
from config import STOPS
from core.metrics import stop_frequency
from dashboard.common import chart, table

def render(df):
    st.subheader("Frecuencia de paraderos")
    freq = stop_frequency(df)
    table(freq, {
        "frecuencia_programada": "{:.1%}", "frecuencia_efectiva": "{:.1%}",
        "tiempo_promedio": "{:.1f}"
    })
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(freq, x="paradero", y=["frecuencia_programada", "frecuencia_efectiva"],
                     barmode="group", title="Frecuencia programada vs. efectiva")
        fig.update_yaxes(tickformat=".0%")
        chart(fig, "stops-frequency")
    with c2:
        chart(px.bar(freq, x="paradero", y="dias_uso_efectivo", text_auto=True,
                     title="Días con uso efectivo"), "stops-days")

    afternoon = df[df["jornada"] == "TARDE"]
    heat_rows = []
    for route, group in afternoon.groupby("recorrido"):
        for stop in STOPS:
            heat_rows.append({"recorrido": route, "paradero": stop,
                              "frecuencia": group[f"usa_{stop.lower()}"].mean()})
    heat = pd.DataFrame(heat_rows)
    chart(px.density_heatmap(heat, x="paradero", y="recorrido", z="frecuencia",
                             histfunc="avg", text_auto=".0%", color_continuous_scale="Blues",
                             title="Mapa de calor por recorrido"), "stops-heat")

    month_rows = []
    for month, group in afternoon.groupby("mes"):
        for stop in STOPS:
            month_rows.append({"mes": month, "paradero": stop,
                               "frecuencia": group[f"usa_{stop.lower()}"].mean()})
    monthly = pd.DataFrame(month_rows)
    fig = px.line(monthly, x="mes", y="frecuencia", color="paradero", markers=True,
                  title="Evolución mensual de paraderos")
    fig.update_yaxes(tickformat=".0%")
    chart(fig, "stops-month")
