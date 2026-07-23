import plotly.express as px
import streamlit as st
from core.metrics import monthly_summary, weekly_summary
from dashboard.common import chart, table

PCT = {
    "puntual_0_5": "{:.1%}", "puntual_pm5": "{:.1%}",
    "anticipadas": "{:.1%}", "retrasos": "{:.1%}",
    "efectividad_tarde": "{:.1%}", "tiempo_promedio": "{:.1f}", "p90": "{:.1f}"
}

def render(df):
    st.subheader("Análisis mensual y semanal")
    monthly = monthly_summary(df)
    table(monthly, PCT)

    c1, c2 = st.columns(2)
    with c1:
        chart(px.bar(monthly, x="mes", y="usuarios_tarde", text_auto=True, title="Usuarios de la tarde por mes"), "month-users")
    with c2:
        fig = px.line(monthly, x="mes", y="puntual_0_5", markers=True, title="Puntualidad mensual")
        fig.update_yaxes(tickformat=".0%")
        chart(fig, "month-punctual")

    available = sorted(df["mes"].dropna().unique())
    selected = st.selectbox("Mes para análisis semanal", available, index=len(available)-1)
    weekly = weekly_summary(df, selected)
    table(weekly, PCT)

    c3, c4 = st.columns(2)
    with c3:
        chart(px.bar(weekly, x="semana", y="usuarios_tarde", text_auto=True, title=f"Usuarios semanales - {selected}"), "week-users")
    with c4:
        fig = px.line(weekly, x="semana", y="puntual_0_5", markers=True, title=f"Puntualidad semanal - {selected}")
        fig.update_yaxes(tickformat=".0%")
        chart(fig, "week-punctual")

    selected_df = df[df["mes"] == selected]
    users_route = selected_df[selected_df["jornada"] == "TARDE"].groupby(
        ["semana_mes", "recorrido"], as_index=False
    )["usuarios"].sum()
    chart(px.bar(users_route, x="semana_mes", y="usuarios", color="recorrido", barmode="group",
                 title=f"Usuarios por recorrido y semana - {selected}"), "week-route")
