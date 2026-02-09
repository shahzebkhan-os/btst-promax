import numpy as np
import pandas as pd


def label_option_pnl(df: pd.DataFrame, price_col="Close", horizons=(1, 3), no_trade_threshold=0.01):
    """Label option P&L for given horizons with no-trade class.

    Returns df with pnl_{h} and label_{h} columns where label:
      1 = profit, -1 = loss, 0 = no-trade (abs(pnl) < threshold)
    """
    out = df.copy()
    price = out[price_col]
    if isinstance(price, pd.DataFrame):
        price = price.iloc[:, 0]
    price = price.astype(float)
    for h in horizons:
        future = price.shift(-h)
        pnl = (future - price) / (price + 1e-9)
        label = np.where(pnl >= no_trade_threshold, 1, np.where(pnl <= -no_trade_threshold, -1, 0))
        out[f"pnl_{h}"] = pnl
        out[f"label_{h}"] = label
    return out
