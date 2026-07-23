import pandas as pd

def apply_filters(df, start_date, end_date, jornadas, rutas):
    return df[
        df["jornada"].isin(jornadas)
        & df["recorrido"].isin(rutas)
        & (df["fecha"] >= pd.Timestamp(start_date))
        & (df["fecha"] <= pd.Timestamp(end_date))
    ].copy()
