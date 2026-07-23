import numpy as np
import pandas as pd

def evaluate_scenario(df, route, selected_stops, demand_adjustment=0, added_minutes=0):
    effective = df[
        (df["jornada"] == "TARDE")
        & (df["estado_operativo"] == "EFECTIVO")
        & (df["recorrido"] == route)
    ].copy()
    selected = [stop.upper() for stop in selected_stops]
    exact = effective[
        effective["combinacion_paradas"].map(
            lambda value: all(stop in value for stop in selected)
        )
    ]
    evidence_n = len(exact)
    base = exact if evidence_n >= 3 else effective
    expected = base["trayecto"].mean() + added_minutes if len(base) else np.nan
    p90 = base["trayecto"].quantile(.90) + added_minutes if len(base) else np.nan
    expected_users = max(0, base["usuarios"].mean() * (1 + demand_adjustment / 100)) if len(base) else np.nan
    evidence = "Alta" if evidence_n >= 20 else "Media" if evidence_n >= 5 else "Baja"
    return {
        "ruta": route,
        "configuracion": " + ".join(selected),
        "observaciones_directas": evidence_n,
        "evidencia": evidence,
        "tiempo_esperado": expected,
        "p90": p90,
        "usuarios_esperados": expected_users,
        "nota": "Estimación exploratoria; validar mediante piloto cuando la evidencia sea baja.",
    }
