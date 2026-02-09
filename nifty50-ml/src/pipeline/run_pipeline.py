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


def process_symbol(symbol: str):
    df = fetch_yahoo_ohlc(symbol + ".NS", period="60d", interval="15m")
    df = add_indicators(df.rename(columns=str.title))
    # dummy options
    options = [{"strike": 100, "cost": 5, "payoff": 12}, {"strike": 110, "cost": 3, "payoff": 7}]
    recs = recommend(options, p_up=0.6)
    return {"symbol": symbol, "rows": len(df), "recs": recs[:1]}


def main():
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

    print("Done", results)

if __name__ == "__main__":
    main()
