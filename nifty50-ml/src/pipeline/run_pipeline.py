import time
import os
import pandas as pd
import numpy as np
from pathlib import Path
from src.ingest.connectors import fetch_yahoo_ohlc, fetch_historical_fo, fetch_kite_ltp
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
from src.models.calibration import RegimeCalibrator
from src.features.prune import prune_by_correlation, prune_by_l1, prune_by_shap
from src.models.regime import detect_regime, detect_regime_series
from src.options.labeling import label_option_pnl
from src.utils.leakage import detect_leakage
from src.models.random_forest import RFModel
from sklearn.metrics import accuracy_score


KITE_LTP_CACHE = {}


def _load_env_file(path: str):
    try:
        if not path or not os.path.exists(path):
            return
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


def process_symbol(symbol: str):
    # use intraday for fresher prices
    df = fetch_yahoo_ohlc(symbol, period="5d", interval="15m")
    if df is None or len(df) == 0:
        return {
            "symbol": symbol,
            "price": 0.0,
            "confidence": 0.5,
            "suggested_option": "CALL",
            "option_price": 0.0,
            "option_value": 0.0,
            "regime": "low",
            "dropped_features": 0,
            "leakage_flags": ""
        }
    df = add_indicators(df.rename(columns=str.title))

    # label option P&L (proxy on close for T+1/T+3)
    df = label_option_pnl(df, price_col="Close", horizons=(1, 3), no_trade_threshold=0.003)

    # feature pruning (numeric cols only)
    num = df.select_dtypes(include="number").fillna(0)
    pruned, dropped = prune_by_correlation(num, threshold=0.95)

    # L1 + SHAP pruning to tighten feature set
    close_for_target = df["Close"]
    if isinstance(close_for_target, pd.DataFrame):
        close_for_target = close_for_target.iloc[:, 0]
    target = (close_for_target.pct_change().shift(-1) > 0).fillna(0).astype(int)
    l1_pruned, l1_dropped = prune_by_l1(pruned.drop(columns=["label_1", "label_3"], errors="ignore"), target, C=0.2)
    shap_pruned, shap_dropped = prune_by_shap(l1_pruned, target, max_features=40)

    # leakage checks
    leak_flags = detect_leakage(df, target_col="label_1", lookahead=1)

    # regime detection (volatility proxy)
    close_series = pruned["Close"]
    if hasattr(close_series, "values") and getattr(close_series, "ndim", 1) > 1:
        close_series = close_series.iloc[:, 0]
    vol_series = close_series.pct_change().rolling(60).std().fillna(0)
    if len(vol_series) == 0:
        regime = "low"
    else:
        regime = detect_regime(float(vol_series.iloc[-1] or 0))

    # regime-specific model proxy (placeholder for real models)
    if regime == "low":
        raw_prob = 0.52
    elif regime == "mid":
        raw_prob = 0.6
    else:
        raw_prob = 0.68

    # train a real model (time-split) for probability + accuracy
    prob = raw_prob
    model_acc = 0.0
    try:
        features = pruned.drop(columns=["label_1", "label_3"], errors="ignore")
        target = (close_for_target.pct_change().shift(-1) > 0).fillna(0).astype(int)
        # align lengths
        min_len = min(len(features), len(target))
        features = features.iloc[:min_len]
        target = target.iloc[:min_len]
        # time-based split
        split = int(len(features) * 0.8)
        if split > 30:
            X_train = features.iloc[:split].fillna(0)
            y_train = target.iloc[:split].values
            X_test = features.iloc[split:].fillna(0)
            y_test = target.iloc[split:].values
            rf = RFModel(n_estimators=400, max_depth=8)
            rf.fit(X_train, y_train)
            # probability for latest row
            prob = float(rf.predict_proba(features.tail(1).fillna(0))[0])
            # accuracy on test
            proba_test = rf.predict_proba(X_test)
            y_pred = (proba_test >= 0.5).astype(int)
            # high-confidence accuracy (more realistic for trading signals)
            mask = (proba_test >= 0.6) | (proba_test <= 0.4)
            if mask.sum() > 0:
                model_acc = float(accuracy_score(y_test[mask], y_pred[mask]))
                model_cov = float(mask.mean())
            else:
                model_acc = float(accuracy_score(y_test, y_pred))
                model_cov = 1.0
        else:
            model_acc = 0.0
            model_cov = 0.0
    except Exception:
        prob = raw_prob
        model_acc = 0.0
        model_cov = 0.0
    except Exception:
        prob = raw_prob
        model_acc = 0.0

    # pull latest live option chain snapshot (best‑effort)
    option_price = 0.0
    option_value = 0.0
    try:
        from src.ingest.connectors import fetch_nse_option_chain
        chain = fetch_nse_option_chain(symbol)
        records = chain.get("records", {})
        data = records.get("data", []) or []
        underlying = records.get("underlyingValue")
        if underlying is None and data:
            sample = data[0].get("CE") or data[0].get("PE") or {}
            underlying = sample.get("underlyingValue")
        if data and underlying is not None:
            # pick nearest strike to underlying
            nearest = min(data, key=lambda d: abs((d.get("strikePrice") or 0) - underlying))
            leg = nearest.get("CE") or nearest.get("PE") or {}
            option_price = float(leg.get("lastPrice") or leg.get("ltp") or 0)
            option_value = float(leg.get("openInterest") or leg.get("oi") or 0)
    except Exception:
        pass

    price_override = None
    # primary: Kite live LTP if available
    try:
        if symbol in KITE_LTP_CACHE and KITE_LTP_CACHE[symbol] is not None:
            price_override = float(KITE_LTP_CACHE[symbol])
    except Exception:
        pass

    # fallback: use browser-scraped bulk CSV if present
    if option_price <= 0 or option_value <= 0 or not price_override:
        try:
            bulk_path = "/Users/aayan/.openclaw/workspace/nse_fno_bulk_option_chain.csv"
            if os.path.exists(bulk_path):
                df_bulk = pd.read_csv(bulk_path)
                df_sym = df_bulk[df_bulk["symbol"] == symbol]
                if not df_sym.empty:
                    # choose row with max OI around ATM
                    df_sym = df_sym.copy()
                    df_sym["ce_openInterest"] = pd.to_numeric(df_sym["ce_openInterest"], errors="coerce")
                    df_sym["pe_openInterest"] = pd.to_numeric(df_sym["pe_openInterest"], errors="coerce")
                    df_sym["score"] = df_sym["ce_openInterest"].fillna(0) + df_sym["pe_openInterest"].fillna(0)
                    row = df_sym.sort_values("score", ascending=False).iloc[0]
                    option_price = float(row.get("ce_lastPrice") or row.get("pe_lastPrice") or 0)
                    option_value = float(row.get("ce_openInterest") or row.get("pe_openInterest") or 0)
                    if not price_override:
                        try:
                            price_override = float(row.get("underlying") or 0)
                        except Exception:
                            price_override = None
        except Exception:
            pass

    option_price = option_price if option_price > 0 else 0.0
    option_value = option_value if option_value > 0 else 0.0

    options = [{"strike": 100, "cost": option_price, "payoff": option_value}]
    recs = recommend(options, p_up=prob)
    top = recs[0]

    # stricter thresholds to surface real PUT opportunities
    if prob >= 0.55:
        side = "CALL"
    elif prob <= 0.45:
        side = "PUT"
    else:
        side = "NEUTRAL"

    return {
        "symbol": symbol,
        "price": float(price_override) if price_override else (float(df["Close"].iloc[-1, 0]) if "Close" in df.columns and hasattr(df["Close"], "ndim") and df["Close"].ndim > 1 else float(df["Close"].iloc[-1]) if "Close" in df.columns else 0.0),
        "confidence": prob,
        "suggested_option": side,
        "option_price": float(top.get("cost", 0)),
        "option_value": float(top.get("payoff", 0)),
        "regime": regime,
        "model_accuracy": model_acc,
        "model_coverage": model_cov,
        "dropped_features": len(dropped) + len(l1_dropped) + len(shap_dropped),
        "leakage_flags": ";".join(leak_flags) if leak_flags else ""
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

    # load .env (if present) for Kite creds
    env_path = os.path.join(os.getcwd(), ".env")
    _load_env_file(env_path)

    # warm Kite LTP cache (best-effort)
    global KITE_LTP_CACHE
    try:
        KITE_LTP_CACHE = fetch_kite_ltp(symbols)
    except Exception:
        KITE_LTP_CACHE = {}

    with mlflow.start_run():
        results = pool.run(symbols, process_symbol)
        log_params_metrics({"symbols": len(symbols)}, {"processed": len(results)})

    df = pd.DataFrame(results)
    if "symbol" in df.columns:
        df = df.sort_values("confidence", ascending=False).drop_duplicates(subset=["symbol"], keep="first")
    df.to_csv("data/features/latest.csv", index=False)
    print("Wrote data/features/latest.csv")

if __name__ == "__main__":
    main()
