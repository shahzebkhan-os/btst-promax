# NIFTY50 Options ML Platform

**Disclaimer / RISK NOTICE:** This project is for research/educational use only. Not financial advice.

---

## What this is
A production‑style pipeline that:
- Ingests **NSE / Yahoo** data (OHLCV + option chain + historical FO)
- Builds features, trains models, and generates **option suggestions**
- Runs walk‑forward backtests with fees/slippage
- Shows results in a **Streamlit UI** with refresh + table filters

---

## Quickstart (pip)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.ingest.download_sample_data
python -m src.train --symbol RELIANCE --epochs 2 --demo
python3 -m streamlit run src/ui/app.py
```

## Demo Script
```bash
./sample_run.sh
```

## Progress API
```bash
uvicorn src.pipeline.progress_api:app --reload --port 9000
curl http://localhost:9000/progress
```

## End-to-end pipeline (demo)
```bash
python -m src.pipeline.run_pipeline
```

## Docker
```bash
docker compose up --build
```

---

## How it runs (end‑to‑end)

### 1) Data Ingestion
Files: `src/ingest/connectors.py`
- **Yahoo OHLCV**: `fetch_yahoo_ohlc(symbol, period, interval)`
- **NSE Option Chain**: `fetch_nse_option_chain(symbol)`
- **NSE Historical FO**: `fetch_historical_fo(...)`
- **Chunked FO fetch**: `fetch_historical_fo_range(...)` (NSE limits ~90 days)

The pipeline first tries historical FO. If it fails (e.g., 503), it falls back to live option‑chain data for option price/value.

### 2) Feature Prep
Files: `src/features/indicators.py`, `src/features/prune.py`
- Computes indicators (RSI, MACD, etc.)
- Prunes correlated features (threshold 0.95)

### 3) Regime Detection + Calibration
Files: `src/models/regime.py`, `src/models/calibration.py`
- Volatility‑based regime (low/mid/high)
- Calibrates probabilities on rolling validation data

### 4) Model & Ensemble
Files: `src/backtest/walkforward.py`, `src/models/random_forest.py`
- **RF + LSTM ensemble** in walk‑forward backtest
- Calibration + confidence thresholding
- Volatility‑adjusted position sizing

### 5) Option Suggestions
Files: `src/options/recommender.py`
- Uses model probability to rank options
- Outputs suggested option price/value to UI

### 6) Output + UI
Files: `src/pipeline/run_pipeline.py`, `src/ui/app.py`
- Pipeline writes: `data/features/latest.csv`
- UI reads that file, applies filters, and renders table
- Refresh button re‑runs the pipeline and reloads output

---

## Run the pipeline
```bash
cd nifty50-ml
python3 -m src.pipeline.run_pipeline
```

## Start the UI
```bash
cd nifty50-ml
python3 -m streamlit run src/ui/app.py
```

---

## Backtest (walk‑forward)
```bash
python3 scripts/run_walkforward.py
```

## Threshold sweep
```bash
python3 scripts/tune_thresholds.py
```

---

## Features
- NIFTY50 + components ingestion (OHLCV + option chain + historical FO)
- Indicators: SMA/EMA/Hull, RSI, Stoch, ATR, HV, BB width, OBV, VWAP, MACD, ADX, candle patterns
- Options: IV surface fitting, PCR, ΔOI, Greeks (delta/gamma/vega)
- Models: LSTM, CNN, Transformer + LightGBM stacking
- ETA progress (EMA timing)
- Streamlit UI + CLI + JSON progress
- Backtester with slippage + fees
- MLflow tracking + Optuna HPO
- Drift monitoring + SHAP explainability (optional)

---

## Notes
- For real option-chain data, configure broker/Kite credentials in `.env`.
- Uses Asia/Kolkata timezone in examples.
