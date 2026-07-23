from pathlib import Path
import pandas as pd
import streamlit as st

from config import APP_TITLE, APP_SUBTITLE, DEFAULT_WORKBOOK
from core.loader import load_workbook
from core.filters import apply_filters
from core.metrics import kpis
from core.validator import validate_dataset

from dashboard import executive, monthly_weekly, demand, stops, times, punctuality, returns, quality, scenario_simulator
from reports.report_center import render as render_reports

st.set_page_config(page_title="KOA Analytics V3", page_icon="🚌", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {background:#eef3f9;}
.koa-title {background:linear-gradient(90deg,#123d76,#1d5da7);color:white;
padding:18px 22px;border-radius:12px;margin-bottom:14px;}
.koa-title h1 {margin:0;font-size:29px;}
.koa-title p {margin:4px 0 0 0;opacity:.92;}
div[data-testid="stMetric"] {background:white;border:1px solid #dce4ed;border-radius:10px;padding:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="koa-title"><h1>{APP_TITLE}</h1><p>{APP_SUBTITLE}</p></div>', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def cached_load(path):
    return load_workbook(path)

upload = st.sidebar.file_uploader("Cargar base KOA (.xlsx)", type=["xlsx"])
try:
    if upload is not None:
        df = load_workbook(upload)
    else:
        path = Path(DEFAULT_WORKBOOK)
        if not path.exists():
            path = Path("data") / DEFAULT_WORKBOOK
        df = cached_load(str(path))
except Exception as exc:
    st.error(f"No fue posible cargar la base: {exc}")
    st.stop()

audit = validate_dataset(df)
if audit["issues"]:
    with st.sidebar.expander("Alertas de calidad"):
        for issue in audit["issues"]:
            st.warning(issue)

valid_dates = df["fecha"].dropna()
date_range = st.sidebar.date_input(
    "Periodo",
    value=(valid_dates.min().date(), valid_dates.max().date()),
    min_value=valid_dates.min().date(),
    max_value=valid_dates.max().date(),
)
start_date, end_date = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (date_range, date_range)

jornadas = st.sidebar.multiselect("Jornada", sorted(df["jornada"].dropna().unique()),
                                  default=sorted(df["jornada"].dropna().unique()))
rutas = st.sidebar.multiselect("Recorrido", sorted(df["recorrido"].dropna().unique()),
                               default=sorted(df["recorrido"].dropna().unique()))

filtered = apply_filters(df, start_date, end_date, jornadas, rutas)
if filtered.empty:
    st.warning("No hay registros para los filtros seleccionados.")
    st.stop()

m = kpis(filtered)
cols = st.columns(8)
values = [
    ("Registros", m["registros"]),
    ("Días", m["dias"]),
    ("Usuarios", m["usuarios"]),
    ("Puntual 0-5", f"{m['puntual_0_5']:.1%}"),
    ("Puntual ±5", f"{m['puntual_pm5']:.1%}"),
    ("Efectivos tarde", m["efectivos_tarde"]),
    ("Tiempo efectivo", f"{m['tiempo_efectivo_promedio']:.1f} min"),
    ("P90", f"{m['tiempo_efectivo_p90']:.1f} min"),
]
for column, (label, value) in zip(cols, values):
    column.metric(label, value)

tabs = st.tabs([
    "Resumen ejecutivo", "Mensual y semanal", "Demanda", "Paraderos",
    "Combinaciones y tiempos", "Puntualidad", "Retorno", "Calidad",
    "Simulador", "Informes", "Auditoría y detalle"
])

with tabs[0]: executive.render(filtered)
with tabs[1]: monthly_weekly.render(filtered)
with tabs[2]: demand.render(filtered)
with tabs[3]: stops.render(filtered)
with tabs[4]: times.render(filtered)
with tabs[5]: punctuality.render(filtered)
with tabs[6]: returns.render(filtered)
with tabs[7]: quality.render(filtered)
with tabs[8]: scenario_simulator.render(filtered)
with tabs[9]: render_reports(filtered)
with tabs[10]:
    st.subheader("Auditoría y detalle")
    st.json(audit)
    st.markdown("""
**Reglas vigentes**
- Puntualidad oficial: salida entre 0 y 5 minutos después de la hora programada.
- Tiempo efectivo: únicamente jornada tarde, usuarios mayores a cero y paradero válido.
- Frecuencia efectiva: usos del paradero / recorridos efectivos de la tarde.
- P90: percentil 90 de los tiempos válidos.
- El simulador es exploratorio y exige piloto cuando la evidencia sea baja.
""")
    st.dataframe(filtered, hide_index=True, use_container_width=True)
