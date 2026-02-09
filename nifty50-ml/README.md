# NIFTY50 Options ML Platform

**Disclaimer / RISK NOTICE:** This project is for research/educational use only. Not financial advice.

## Quickstart (pip)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.ingest.download_sample_data
python -m src.train --symbol RELIANCE --epochs 2 --demo
streamlit run src/ui/app.py
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

## Features
- NIFTY50 + components ingestion (OHLCV + option chain)
- Indicators: SMA/EMA/Hull, RSI, Stoch, ATR, HV, BB width, OBV, VWAP, MACD, ADX, candle patterns
- Options: IV surface fitting, PCR, ΔOI, Greeks (delta/gamma/vega)
- Models: LSTM, CNN, Transformer + LightGBM stacking
- ETA progress (EMA timing)
- Streamlit UI + CLI + JSON progress
- Backtester with slippage + fees
- MLflow tracking + Optuna HPO
- Drift monitoring + SHAP explainability (optional)

## Notes
- For real option-chain data, configure broker/Kite credentials in `.env`.
- Uses Asia/Kolkata timezone in examples.
