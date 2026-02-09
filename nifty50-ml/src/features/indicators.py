import pandas as pd
import numpy as np

try:
    import ta
except Exception:
    ta = None


def add_indicators(df: pd.DataFrame):
    d = df.copy()
    close = d["Close"]
    if hasattr(close, "values"):
        close = pd.Series(close.values.squeeze(), index=d.index)
    if ta:
        d["rsi"] = ta.momentum.rsi(close, window=14)
        d["macd"] = ta.trend.macd(close)
    else:
        d["rsi"] = d["Close"].diff().rolling(14).mean()
        d["macd"] = d["Close"].ewm(span=12).mean() - d["Close"].ewm(span=26).mean()
    return d
