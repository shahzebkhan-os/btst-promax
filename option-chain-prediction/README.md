# Option Chain Prediction (ML)

End‑to‑end ML project scaffold for predicting option‑chain outcomes (e.g., IV move, OI change, next‑day option premium direction).

## Goals (customize)
- Predict **next‑day IV change** for ATM options
- Predict **directional premium move** (up/down) for near‑term contracts
- Score **probability of gamma/oi hotspots** shifting

## Project Layout
```
option-chain-prediction/
  configs/            # yaml configs
  data/               # raw/processed
  notebooks/          # exploration
  src/                # pipeline code
  tests/              # unit tests
```

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m src.cli --symbol NIFTY --expiry 2026-03-19
```

## Features (examples)
- Underlying: returns, realized vol, trend, RSI, MACD
- Chain: IV term structure, skew, OI, volume, bid‑ask spread
- Derived: gamma exposure, OI change rates, IV percentile

## Targets (examples)
- Regression: ΔIV (t+1), ΔOI (t+1)
- Classification: option premium up/down (t+1)

## Notes
- Data connectors are placeholders. Integrate NSE/US feeds as needed.
