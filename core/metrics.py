import numpy as np
import pandas as pd
from config import STOPS

def kpis(df):
    afternoon = df[df["jornada"] == "TARDE"]
    effective = afternoon[afternoon["estado_operativo"] == "EFECTIVO"]
    punctual = df.dropna(subset=["desv_min"])
    return {
        "registros": len(df),
        "dias": int(df["fecha"].nunique()),
        "usuarios": int(df["usuarios"].sum()),
        "puntual_0_5": punctual["puntual_0_5"].mean() if len(punctual) else np.nan,
        "puntual_pm5": punctual["puntual_pm5"].mean() if len(punctual) else np.nan,
        "anticipadas": punctual["anticipada"].mean() if len(punctual) else np.nan,
        "retrasos": punctual["retraso_mayor_5"].mean() if len(punctual) else np.nan,
        "efectivos_tarde": len(effective),
        "sin_usuarios_tarde": (afternoon["estado_operativo"] == "SIN USUARIOS").mean() if len(afternoon) else np.nan,
        "tiempo_efectivo_promedio": effective["trayecto"].mean(),
        "tiempo_efectivo_p90": effective["trayecto"].quantile(.90) if effective["trayecto"].notna().any() else np.nan,
    }

def monthly_summary(df):
    rows = []
    for month, group in df.groupby("mes"):
        punctual = group.dropna(subset=["desv_min"])
        afternoon = group[group["jornada"] == "TARDE"]
        effective = afternoon[afternoon["estado_operativo"] == "EFECTIVO"]
        rows.append({
            "mes": month,
            "registros": len(group),
            "dias": group["fecha"].nunique(),
            "usuarios": group["usuarios"].sum(),
            "usuarios_tarde": afternoon["usuarios"].sum(),
            "puntual_0_5": punctual["puntual_0_5"].mean() if len(punctual) else np.nan,
            "puntual_pm5": punctual["puntual_pm5"].mean() if len(punctual) else np.nan,
            "anticipadas": punctual["anticipada"].mean() if len(punctual) else np.nan,
            "retrasos": punctual["retraso_mayor_5"].mean() if len(punctual) else np.nan,
            "efectivos_tarde": len(effective),
            "sin_usuarios": int((afternoon["estado_operativo"] == "SIN USUARIOS").sum()),
            "efectividad_tarde": len(effective) / len(afternoon) if len(afternoon) else np.nan,
            "tiempo_promedio": effective["trayecto"].mean(),
            "p90": effective["trayecto"].quantile(.90) if effective["trayecto"].notna().any() else np.nan,
        })
    return pd.DataFrame(rows)

def weekly_summary(df, month=None):
    source = df[df["mes"] == month] if month else df
    rows = []
    for key, group in source.groupby(["mes", "numero_semana_mes", "semana_mes"], dropna=False):
        punctual = group.dropna(subset=["desv_min"])
        afternoon = group[group["jornada"] == "TARDE"]
        effective = afternoon[afternoon["estado_operativo"] == "EFECTIVO"]
        rows.append({
            "mes": key[0], "numero_semana": key[1], "semana": key[2],
            "registros": len(group), "dias": group["fecha"].nunique(),
            "usuarios": group["usuarios"].sum(), "usuarios_tarde": afternoon["usuarios"].sum(),
            "puntual_0_5": punctual["puntual_0_5"].mean() if len(punctual) else np.nan,
            "anticipadas": punctual["anticipada"].mean() if len(punctual) else np.nan,
            "retrasos": punctual["retraso_mayor_5"].mean() if len(punctual) else np.nan,
            "efectivos_tarde": len(effective),
            "sin_usuarios": int((afternoon["estado_operativo"] == "SIN USUARIOS").sum()),
            "efectividad_tarde": len(effective) / len(afternoon) if len(afternoon) else np.nan,
            "tiempo_promedio": effective["trayecto"].mean(),
            "p90": effective["trayecto"].quantile(.90) if effective["trayecto"].notna().any() else np.nan,
        })
    return pd.DataFrame(rows).sort_values(["mes", "numero_semana"])

def demand_summary(df):
    afternoon = df[df["jornada"] == "TARDE"]
    return afternoon.groupby("recorrido").agg(
        salidas=("recorrido", "size"),
        usuarios=("usuarios", "sum"),
        promedio_usuarios=("usuarios", "mean"),
        efectivos=("estado_operativo", lambda x: (x == "EFECTIVO").sum()),
        sin_usuarios=("estado_operativo", lambda x: (x == "SIN USUARIOS").sum()),
    ).reset_index()

def stop_frequency(df):
    afternoon = df[df["jornada"] == "TARDE"]
    effective = afternoon[afternoon["estado_operativo"] == "EFECTIVO"]
    rows = []
    for stop in STOPS:
        all_uses = int(afternoon[f"usa_{stop.lower()}"].sum())
        effective_uses = int(effective[f"usa_{stop.lower()}"].sum())
        rows.append({
            "paradero": stop,
            "usos_programados": all_uses,
            "frecuencia_programada": all_uses / len(afternoon) if len(afternoon) else np.nan,
            "usos_efectivos": effective_uses,
            "frecuencia_efectiva": effective_uses / len(effective) if len(effective) else np.nan,
            "dias_uso_efectivo": effective.loc[effective[f"usa_{stop.lower()}"] == 1, "fecha"].nunique(),
            "tiempo_promedio": effective.loc[effective[f"usa_{stop.lower()}"] == 1, "trayecto"].mean(),
        })
    return pd.DataFrame(rows)

def combinations(df):
    effective = df[(df["jornada"] == "TARDE") & (df["estado_operativo"] == "EFECTIVO")]
    return effective.groupby(["recorrido", "combinacion_paradas"]).agg(
        recorridos=("recorrido", "size"),
        usuarios=("usuarios", "sum"),
        usuarios_promedio=("usuarios", "mean"),
        tiempo_promedio=("trayecto", "mean"),
        mediana=("trayecto", "median"),
        p90=("trayecto", lambda x: x.dropna().quantile(.90) if x.notna().any() else np.nan),
        p95=("trayecto", lambda x: x.dropna().quantile(.95) if x.notna().any() else np.nan),
        minimo=("trayecto", "min"),
        maximo=("trayecto", "max"),
        desviacion=("trayecto", "std"),
    ).reset_index()

def punctuality_summary(df):
    valid = df.dropna(subset=["desv_min"])
    return valid.groupby(["jornada", "recorrido"]).agg(
        registros_validos=("desv_min", "size"),
        puntual_0_5=("puntual_0_5", "mean"),
        puntual_pm5=("puntual_pm5", "mean"),
        anticipadas=("anticipada", "mean"),
        retraso_mayor_5=("retraso_mayor_5", "mean"),
        desviacion_promedio=("desv_min", "mean"),
        desviacion_p90=("desv_min", lambda x: x.quantile(.90)),
    ).reset_index()

def return_margin(df):
    afternoon = df[df["jornada"] == "TARDE"]
    rows = []
    for date, group in afternoon.groupby("fecha"):
        route_map = {row["recorrido"]: row for _, row in group.iterrows()}
        for first, second in [("R1", "R2"), ("R2", "R3")]:
            if first in route_map and second in route_map:
                current = route_map[first]
                nxt = route_map[second]
                if current["estado_operativo"] == "EFECTIVO" and pd.notna(current["llegada"]) and pd.notna(nxt["prog"]):
                    margin = nxt["prog"] - current["llegada"]
                    if margin > 720:
                        margin -= 1440
                    if margin < -720:
                        margin += 1440
                    rows.append({"fecha": date, "tramo": f"{first}->{second}", "margen_min": margin})
    return pd.DataFrame(rows)


def weekly_punctuality_by_route(df, month=None):
    """
    Puntualidad semanal por recorrido.
    Puntualidad oficial: salida entre 0 y 5 minutos después de la hora programada.
    Denominador: registros con hora programada e inicio real válidos.
    """
    source = df[df["mes"] == month].copy() if month else df.copy()
    valid = source.dropna(subset=["desv_min"]).copy()
    if valid.empty:
        return pd.DataFrame(columns=[
            "mes", "numero_semana", "semana", "recorrido",
            "registros_validos", "puntual_0_5", "puntual_pm5",
            "anticipadas", "retrasos_mayor_5"
        ])

    return (
        valid.groupby(
            ["mes", "numero_semana_mes", "semana_mes", "recorrido"],
            dropna=False
        )
        .agg(
            registros_validos=("desv_min", "size"),
            puntual_0_5=("puntual_0_5", "mean"),
            puntual_pm5=("puntual_pm5", "mean"),
            anticipadas=("anticipada", "mean"),
            retrasos_mayor_5=("retraso_mayor_5", "mean"),
        )
        .reset_index()
        .rename(columns={
            "numero_semana_mes": "numero_semana",
            "semana_mes": "semana",
        })
        .sort_values(["mes", "numero_semana", "recorrido"])
    )


def weekly_route_usage(df, month=None):
    """
    Uso semanal de rutas de la jornada tarde.

    Incluye dos lecturas:
    1. Utilización operativa: recorridos efectivos / salidas programadas de esa ruta.
    2. Participación de demanda: usuarios de la ruta / usuarios totales de la semana.
    """
    source = df[df["mes"] == month].copy() if month else df.copy()
    afternoon = source[source["jornada"] == "TARDE"].copy()
    if afternoon.empty:
        return pd.DataFrame(columns=[
            "mes", "numero_semana", "semana", "recorrido",
            "salidas_programadas", "recorridos_efectivos",
            "utilizacion_operativa", "usuarios",
            "participacion_usuarios", "promedio_usuarios_salida"
        ])

    grouped = (
        afternoon.groupby(
            ["mes", "numero_semana_mes", "semana_mes", "recorrido"],
            dropna=False
        )
        .agg(
            salidas_programadas=("recorrido", "size"),
            recorridos_efectivos=("estado_operativo", lambda x: (x == "EFECTIVO").sum()),
            usuarios=("usuarios", "sum"),
            promedio_usuarios_salida=("usuarios", "mean"),
        )
        .reset_index()
        .rename(columns={
            "numero_semana_mes": "numero_semana",
            "semana_mes": "semana",
        })
    )

    grouped["utilizacion_operativa"] = (
        grouped["recorridos_efectivos"] / grouped["salidas_programadas"]
    )

    weekly_users = (
        grouped.groupby(["mes", "numero_semana"], dropna=False)["usuarios"]
        .transform("sum")
    )
    grouped["participacion_usuarios"] = np.where(
        weekly_users > 0,
        grouped["usuarios"] / weekly_users,
        np.nan,
    )

    return grouped.sort_values(["mes", "numero_semana", "recorrido"])
