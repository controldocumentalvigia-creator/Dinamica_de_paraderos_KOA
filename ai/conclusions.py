import numpy as np
from core.metrics import kpis, demand_summary, stop_frequency, monthly_summary

def generate_conclusions(df):
    result = kpis(df)
    demand = demand_summary(df)
    stops = stop_frequency(df)
    monthly = monthly_summary(df)
    conclusions = []

    if not demand.empty:
        low = demand.sort_values("usuarios").iloc[0]
        high = demand.sort_values("usuarios", ascending=False).iloc[0]
        conclusions.append(
            f"{high['recorrido']} concentra la mayor demanda de la tarde con {int(high['usuarios'])} usuarios, "
            f"mientras {low['recorrido']} registra la menor con {int(low['usuarios'])}."
        )
    if not stops.empty:
        top = stops.sort_values("frecuencia_efectiva", ascending=False).iloc[0]
        conclusions.append(
            f"{top['paradero']} es el paradero más utilizado en recorridos efectivos, "
            f"con una frecuencia de {top['frecuencia_efectiva']:.1%}."
        )
        heroes = stops[stops["paradero"] == "HEROES"]
        if not heroes.empty and heroes.iloc[0]["usos_efectivos"] < 5:
            conclusions.append(
                "HÉROES cuenta con evidencia histórica insuficiente en la tarde; cualquier cambio permanente debe probarse con un piloto controlado."
            )
    if not np.isnan(result["puntual_0_5"]):
        conclusions.append(
            f"La puntualidad oficial de 0 a 5 minutos es {result['puntual_0_5']:.1%}; "
            f"las salidas anticipadas representan {result['anticipadas']:.1%} y los retrasos superiores a 5 minutos {result['retrasos']:.1%}."
        )
    if len(monthly) >= 2:
        first, last = monthly.iloc[0], monthly.iloc[-1]
        if first["usuarios"] != 0:
            variation = (last["usuarios"] - first["usuarios"]) / first["usuarios"]
            conclusions.append(
                f"Entre {first['mes']} y {last['mes']}, el volumen de usuarios varió {variation:+.1%}."
            )
    if not np.isnan(result["tiempo_efectivo_promedio"]):
        conclusions.append(
            f"El tiempo medio de los recorridos efectivos de la tarde es {result['tiempo_efectivo_promedio']:.1f} minutos "
            f"y el P90 es {result['tiempo_efectivo_p90']:.1f} minutos."
        )
    return conclusions
