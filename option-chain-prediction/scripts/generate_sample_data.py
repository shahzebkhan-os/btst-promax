import numpy as np
import pandas as pd

np.random.seed(42)

symbols = ["NIFTY","BANKNIFTY","RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","SBIN","ITC","KOTAKBANK","LT","MARUTI","SUNPHARMA","TITAN","HINDUNILVR"]
rows_per = 800
rows = rows_per * len(symbols)
underlying_close = np.cumsum(np.random.normal(0, 1, rows)) + 20000
underlying_volume = np.random.randint(5e6, 2e7, rows)

iv_atm = np.clip(np.random.normal(16, 2, rows), 8, 40)
iv_put_otm = iv_atm + np.random.normal(1.5, 0.5, rows)
iv_call_otm = iv_atm - np.random.normal(1.2, 0.5, rows)
iv_near = iv_atm + np.random.normal(0.5, 0.3, rows)
iv_next = iv_atm - np.random.normal(0.5, 0.3, rows)

oi_atm = np.random.randint(10000, 80000, rows)
oi_atm_prev = oi_atm - np.random.randint(-2000, 2000, rows)
oi_put = np.random.randint(8000, 60000, rows)
oi_call = np.random.randint(8000, 60000, rows)

mid_atm = np.clip(np.random.normal(220, 30, rows), 40, 600)
bid_atm = mid_atm - np.random.uniform(2, 8, rows)
ask_atm = mid_atm + np.random.uniform(2, 8, rows)

premium_atm = mid_atm + np.random.normal(0, 4, rows)
volume_atm = np.random.randint(500, 5000, rows)

sym_col = [s for s in symbols for _ in range(rows_per)]
sample = pd.DataFrame({
    "symbol": sym_col,
    "underlying_close": underlying_close,
    "underlying_volume": underlying_volume,
    "iv_atm": iv_atm,
    "iv_put_otm": iv_put_otm,
    "iv_call_otm": iv_call_otm,
    "iv_near": iv_near,
    "iv_next": iv_next,
    "oi_atm": oi_atm,
    "oi_atm_prev": oi_atm_prev,
    "oi_put": oi_put,
    "oi_call": oi_call,
    "ask_atm": ask_atm,
    "bid_atm": bid_atm,
    "mid_atm": mid_atm,
    "premium_atm": premium_atm,
    "volume_atm": volume_atm,
})

out = "data/sample_train.csv"
sample.to_csv(out, index=False)
print("Wrote", out)
