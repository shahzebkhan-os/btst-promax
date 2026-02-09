import pandas as pd
import numpy as np

try:
    import ta
except Exception:
    ta = None


def add_indicators(df: pd.DataFrame):
    d = df.copy()
    close = d["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    if hasattr(close, "values"):
        close = pd.Series(close.values.squeeze(), index=d.index)
    if ta:
        d["rsi"] = ta.momentum.rsi(close, window=14)
        d["macd"] = ta.trend.macd(close)
    else:
        d["rsi"] = d["Close"].diff().rolling(14).mean()
        d["macd"] = d["Close"].ewm(span=12).mean() - d["Close"].ewm(span=26).mean()

    # regime-aware volatility features
    returns = close.pct_change()
    d["ret_1d"] = returns
    d["vol_20"] = returns.rolling(20).std()
    d["vol_60"] = returns.rolling(60).std()
    d["vol_z"] = (d["vol_20"] - d["vol_60"]) / (d["vol_60"] + 1e-9)
    return d
