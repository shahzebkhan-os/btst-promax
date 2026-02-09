import time
import pandas as pd
from src.ingest.connectors import fetch_yahoo_ohlc
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
    vol = float(pruned["Close"].pct_change().std() or 0)
    regime = detect_regime(vol)

    # dummy prediction + calibration
    raw_prob = 0.55 if regime == "low" else 0.6 if regime == "mid" else 0.65
    calib = Calibrator().fit([0.4,0.5,0.6,0.7],[0,0,1,1])
    prob = float(calib.transform([raw_prob])[0])

    # dummy options
    options = [{"strike": 100, "cost": 5, "payoff": 12}, {"strike": 110, "cost": 3, "payoff": 7}]
    recs = recommend(options, p_up=prob)
    top = recs[0]
    return {
        "symbol": symbol,
        "price": float(df["Close"].iloc[-1]) if "Close" in df.columns else 0.0,
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
