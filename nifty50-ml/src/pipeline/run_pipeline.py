import time
import pandas as pd
import numpy as np
from src.ingest.connectors import fetch_yahoo_ohlc, fetch_historical_fo
from src.features.indicators import add_indicators
from src.models.lstm import LSTMModel
from src.options.recommender import recommend
from src.options.iv_surface import fit_iv_surface, greeks_black_scholes
from src.backtest.engine import backtest
from src.backtest.analytics import sharpe, max_drawdown
from src.pipeline.worker import WorkerPool
from src.experiment.mlflow_utils import log_params_metrics
import mlflow
import torch
from src.models.calibration import Calibrator
from src.features.prune import prune_by_correlation
from src.models.regime import detect_regime


def process_symbol(symbol: str):
    df = fetch_yahoo_ohlc(symbol + ".NS", period="60d", interval="15m")
    df = add_indicators(df.rename(columns=str.title))

    # feature pruning (demo: numeric cols only)
    num = df.select_dtypes(include="number").fillna(0)
    pruned, dropped = prune_by_correlation(num, threshold=0.95)

    # regime detection (volatility proxy)
    close_series = pruned["Close"]
    if hasattr(close_series, "values") and getattr(close_series, "ndim", 1) > 1:
        close_series = close_series.iloc[:, 0]
    vol = float(close_series.pct_change().std() or 0)
    regime = detect_regime(vol)

    # regime-specific model proxy (placeholder for real models)
    if regime == "low":
        raw_prob = 0.52
    elif regime == "mid":
        raw_prob = 0.6
    else:
        raw_prob = 0.68

    # fit calibrator on a rolling validation window (next-return > 0)
    returns = pruned["Close"].pct_change().fillna(0).values.squeeze()
    x = returns[:-1]
    y = (returns[1:] > 0).astype(int)
    if len(x) > 10:
        denom = x.ptp()
        if denom == 0:
            x_norm = np.zeros_like(x)
        else:
            x_norm = (x - x.min()) / (denom + 1e-9)
        mask = (~np.isnan(x_norm)) & (~np.isnan(y))
        x_norm = x_norm[mask]
        y = y[mask]
        if len(x_norm) > 10:
            calib = Calibrator().fit(x_norm, y)
            prob = float(calib.transform([raw_prob])[0])
        else:
            prob = raw_prob
    else:
        prob = raw_prob

    # pull latest historical FO (optional)
    option_price = 0.0
    option_value = 0.0
    try:
        from src.ingest.connectors import fetch_historical_fo_range
        ranges = [("01-01-2024","31-03-2024"),("01-04-2024","30-06-2024"),("01-07-2024","30-09-2024"),("01-10-2024","31-12-2024")]
        data = fetch_historical_fo_range(symbol, instrument="OPTSTK", ranges=ranges)
        if data:
            last = data[-1]
            option_price = float(last.get("Close", 0))
            option_value = float(last.get("Turnover", 0))
    except Exception:
        pass

    options = [{"strike": 100, "cost": max(1, option_price), "payoff": max(1, option_value)}]
    recs = recommend(options, p_up=prob)
    top = recs[0]
    return {
        "symbol": symbol,
        "price": float(df["Close"].iloc[-1, 0]) if "Close" in df.columns and hasattr(df["Close"], "ndim") and df["Close"].ndim > 1 else float(df["Close"].iloc[-1]) if "Close" in df.columns else 0.0,
        "confidence": prob,
        "suggested_option": "CALL" if prob >= 0.5 else "PUT",
        "option_price": float(top.get("cost", 0)),
        "option_value": float(top.get("payoff", 0)),
        "regime": regime,
        "dropped_features": len(dropped)
    }


def main():
    try:
        from src.ingest.universe import fetch_optionable_universe
        symbols = fetch_optionable_universe()
    except Exception:
        symbols = [
            "ADANIPORTS","ASIANPAINT","AXISBANK","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV",
            "BPCL","BHARTIARTL","BRITANNIA","CIPLA","COALINDIA","DIVISLAB","DRREDDY",
            "EICHERMOT","GRASIM","HCLTECH","HDFCBANK","HDFCLIFE","HEROMOTOCO",
            "HINDALCO","HINDUNILVR","ICICIBANK","INDUSINDBK","INFY","ITC",
            "JSWSTEEL","KOTAKBANK","LT","M&M","MARUTI","NESTLEIND",
            "NTPC","ONGC","POWERGRID","RELIANCE","SBIN","SHREECEM",
            "SUNPHARMA","TATAMOTORS","TATASTEEL","TCS","TECHM","TITAN",
            "ULTRACEMCO","UPL","WIPRO","ADANIENT","APOLLOHOSP"
        ]
    pool = WorkerPool(workers=2)

    with mlflow.start_run():
        results = pool.run(symbols, process_symbol)
        log_params_metrics({"symbols": len(symbols)}, {"processed": len(results)})

    df = pd.DataFrame(results)
    df.to_csv("data/features/latest.csv", index=False)
    print("Wrote data/features/latest.csv")

if __name__ == "__main__":
    main()
