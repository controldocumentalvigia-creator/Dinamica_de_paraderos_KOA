from pathlib import Path
import numpy as np
import pandas as pd
from config import DEFAULT_SHEET, STOPS
from core.utils import norm, to_minutes, canonical_stops

REQUIRED_COLUMNS = [
    "DIA DEL SERVICIO", "RECORRIDO", "JORNADA", "USUARIOS", "PARADAS",
    "HORARIO-P1-REAL DE INICIO", "Hora de inicio R1P1",
    "Hora de llegada a KOA  P2", "Tiempo  de trayecto ida -regreso",
    "tiempo de espera vehiculo",
]

def _find_column(columns, expected):
    for column in columns:
        if norm(column) == norm(expected):
            return column
    raise KeyError(f"No se encontró la columna requerida: {expected}")

def load_workbook(source, sheet_name=DEFAULT_SHEET) -> pd.DataFrame:
    raw = pd.read_excel(source, sheet_name=sheet_name, engine="openpyxl")
    raw.columns = [str(c).strip() for c in raw.columns]
    mapping = {name: _find_column(raw.columns, name) for name in REQUIRED_COLUMNS}

    out = pd.DataFrame()
    raw_date = raw[mapping["DIA DEL SERVICIO"]]
    numeric_date = pd.to_numeric(raw_date, errors="coerce")
    out["fecha"] = pd.to_datetime(numeric_date, unit="D", origin="1899-12-30", errors="coerce")
    out["fecha"] = out["fecha"].fillna(pd.to_datetime(raw_date, dayfirst=True, errors="coerce"))
    out["recorrido"] = raw[mapping["RECORRIDO"]].map(norm)
    out["jornada"] = raw[mapping["JORNADA"]].map(norm)
    out["usuarios"] = pd.to_numeric(raw[mapping["USUARIOS"]], errors="coerce").fillna(0)
    out["paradas"] = raw[mapping["PARADAS"]].fillna("").astype(str)
    out["paradas_n"] = out["paradas"].map(norm)
    out["combinacion_paradas"] = out["paradas"].map(canonical_stops)

    time_mapping = {
        "prog": "HORARIO-P1-REAL DE INICIO",
        "inicio": "Hora de inicio R1P1",
        "llegada": "Hora de llegada a KOA  P2",
        "trayecto": "Tiempo  de trayecto ida -regreso",
        "espera": "tiempo de espera vehiculo",
    }
    for target, source_name in time_mapping.items():
        out[target] = to_minutes(raw[mapping[source_name]])

    deviation = out["inicio"] - out["prog"]
    out["desv_min"] = np.where(
        deviation > 720, deviation - 1440,
        np.where(deviation < -720, deviation + 1440, deviation)
    )
    out["puntual_0_5"] = out["desv_min"].between(0, 5, inclusive="both")
    out["puntual_pm5"] = out["desv_min"].abs().le(5)
    out["anticipada"] = out["desv_min"] < 0
    out["retraso_mayor_5"] = out["desv_min"] > 5

    def operational_status(row):
        text = row["paradas_n"]
        users = row["usuarios"]
        if "NO SE ALCANZO" in text:
            return "NO EJECUTADO"
        if "VALIDAR" in text:
            return "VALIDAR"
        if "NO SALIERON" in text:
            return "SIN USUARIOS"
        if not text:
            return "SIN REGISTRO PARADAS"
        valid_stop = any(stop in text for stop in STOPS)
        if valid_stop and users > 0:
            return "EFECTIVO"
        if valid_stop and users <= 0:
            return "PARADA REGISTRADA SIN USUARIOS"
        return "OTRO"

    out["estado_operativo"] = out.apply(operational_status, axis=1)
    for stop in STOPS:
        out[f"usa_{stop.lower()}"] = out["paradas_n"].str.contains(stop, na=False).astype(int)

    out["mes"] = out["fecha"].dt.to_period("M").astype(str)
    out["numero_semana_mes"] = ((out["fecha"].dt.day - 1) // 7 + 1).astype("Int64")
    out["semana_mes"] = out["numero_semana_mes"].map(
        lambda value: f"Semana {int(value)}" if pd.notna(value) else "SIN FECHA"
    )
    out["mes_semana"] = out["mes"] + " | " + out["semana_mes"]
    out["dia_semana"] = out["fecha"].dt.day_name()
    out["dia"] = out["fecha"].dt.strftime("%d/%m/%Y")
    return out
