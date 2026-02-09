import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.ingest.connectors import fetch_yahoo_ohlc
from src.backtest.walkforward import walk_forward

symbol = "RELIANCE"
print("Fetching 10y data...")
df = fetch_yahoo_ohlc(symbol + ".NS", period="60d", interval="15m")
close = df["Close"].astype(float).to_numpy().squeeze()
returns = (close[1:] / close[:-1] - 1.0)

res = walk_forward(returns, conf=0.6, fees=0.0005, vol_target=0.01)
print(f"Walk-forward backtest {symbol} 60d 15m")
print(res)
