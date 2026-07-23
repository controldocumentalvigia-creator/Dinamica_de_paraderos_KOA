import plotly.express as px
import streamlit as st
from dashboard.common import chart

def render(df):
    st.subheader("Calidad operativa")
    afternoon = df[df["jornada"] == "TARDE"]
    status = afternoon["estado_operativo"].value_counts().rename_axis("estado").reset_index(name="registros")
    status["porcentaje"] = status["registros"] / status["registros"].sum()
    c1, c2 = st.columns(2)
    with c1:
        chart(px.pie(status, names="estado", values="registros", hole=.45,
                     title="Distribución de estados"), "quality-pie")
    with c2:
        fig = px.bar(status, x="estado", y="porcentaje", text_auto=".1%",
                     title="Participación por estado")
        fig.update_yaxes(tickformat=".0%")
        chart(fig, "quality-bar")
    monthly = afternoon.groupby(["mes", "estado_operativo"]).size().reset_index(name="registros")
    chart(px.bar(monthly, x="mes", y="registros", color="estado_operativo", barmode="stack",
                 title="Evolución mensual del estado operativo"), "quality-month")
