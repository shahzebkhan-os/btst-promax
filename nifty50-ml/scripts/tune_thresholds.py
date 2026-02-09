import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.ingest.connectors import fetch_yahoo_ohlc
from src.backtest.walkforward import walk_forward

symbol = "RELIANCE"
print("Fetching 10y data...")
df = fetch_yahoo_ohlc(symbol + ".NS", period="60d", interval="15m")
close = df["Close"].astype(float).to_numpy().squeeze()
returns = (close[1:] / close[:-1] - 1.0)

for conf in [0.55, 0.6, 0.65, 0.7]:
    res = walk_forward(returns, conf=conf, fees=0.0005, vol_target=0.01)
    print(conf, res)
