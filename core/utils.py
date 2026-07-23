import re
import unicodedata
import numpy as np
import pandas as pd

def norm(value) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text.upper().strip())

def to_minutes(series: pd.Series) -> pd.Series:
    def convert(value):
        if pd.isna(value):
            return np.nan
        if isinstance(value, pd.Timedelta):
            return value.total_seconds() / 60
        if hasattr(value, "hour"):
            return value.hour * 60 + value.minute + getattr(value, "second", 0) / 60
        try:
            number = float(value)
            return number * 1440 if abs(number) <= 2 else number
        except Exception:
            parts = str(value).strip().split(":")
            if len(parts) >= 2:
                try:
                    return float(parts[0]) * 60 + float(parts[1]) + (
                        float(parts[2]) / 60 if len(parts) > 2 else 0
                    )
                except Exception:
                    return np.nan
            return np.nan
    return series.map(convert)

def safe_div(numerator, denominator):
    return numerator / denominator if denominator else np.nan

def canonical_stops(value) -> str:
    text = norm(value)
    if not text:
        return "SIN REGISTRO"
    if "NO SALIERON" in text:
        return "NO USUARIOS"
    if "NO SE ALCANZO" in text:
        return "NO EJECUTADO"
    if "VALIDAR" in text:
        return "VALIDAR"
    order = ["OXXO", "VIRREY", "HEROES", "POLO", "KOA"]
    found = [stop for stop in order if stop in text]
    return " + ".join(found) if found else "OTRO"
