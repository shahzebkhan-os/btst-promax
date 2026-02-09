import numpy as np

def sharpe(returns, rf=0.0):
    r = np.array(returns) - rf
    return r.mean() / (r.std() + 1e-9)


def max_drawdown(equity):
    peak = equity[0]
    dd = 0
    for x in equity:
        peak = max(peak, x)
        dd = min(dd, (x-peak)/peak)
    return dd
