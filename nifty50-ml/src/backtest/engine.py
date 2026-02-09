import numpy as np

def backtest(returns, fees=0.0005):
    equity = [1.0]
    for r in returns:
        equity.append(equity[-1]*(1+r-fees))
    return equity
