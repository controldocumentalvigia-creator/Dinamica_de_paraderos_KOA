from core.metrics import demand_summary, punctuality_summary, stop_frequency

def generate_recommendations(df):
    recs = []
    demand = demand_summary(df)
    punctual = punctuality_summary(df)
    stops = stop_frequency(df)

    if not demand.empty:
        low = demand.sort_values("usuarios").iloc[0]
        recs.append({
            "prioridad": "Alta",
            "accion": f"Revisar la configuración y necesidad operativa de {low['recorrido']}.",
            "motivo": "Es el recorrido con menor demanda acumulada en la jornada tarde.",
            "plazo": "30 días",
        })
    if not punctual.empty and punctual["puntual_0_5"].mean() < 0.8:
        recs.append({
            "prioridad": "Alta",
            "accion": "Implementar seguimiento semanal de puntualidad por ruta y causa de desviación.",
            "motivo": "La puntualidad se encuentra por debajo del umbral gerencial del 80%.",
            "plazo": "Inmediato",
        })
    heroes = stops[stops["paradero"] == "HEROES"]
    if not heroes.empty and heroes.iloc[0]["usos_efectivos"] < 5:
        recs.append({
            "prioridad": "Media",
            "accion": "Realizar piloto controlado antes de incorporar HÉROES de forma permanente.",
            "motivo": "La base histórica no ofrece una muestra suficiente para estimar el impacto.",
            "plazo": "2 semanas",
        })
    recs.append({
        "prioridad": "Media",
        "accion": "Completar obligatoriamente la columna PARADAS y documentar la causa de los recorridos no ejecutados.",
        "motivo": "Mejora la trazabilidad y evita sesgos en los indicadores.",
        "plazo": "Inmediato",
    })
    return recs
