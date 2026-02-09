import time
from .eta import ETAState

symbols = ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN"]
eta = ETAState(alpha=0.4)

for s in symbols:
    start = time.time()
    time.sleep(0.1)
    eta.update(s, time.time() - start)
    remaining = symbols[symbols.index(s)+1:]
    print(s, "ETA", round(eta.estimate(remaining),2))
