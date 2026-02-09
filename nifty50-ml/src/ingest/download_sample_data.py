import pandas as pd
from pathlib import Path

Path("data/raw").mkdir(parents=True, exist_ok=True)

# tiny sample dataset for CI/demo
sample = pd.DataFrame({
    "symbol": ["RELIANCE","TCS"],
    "close": [2500, 3400],
    "volume": [1_000_000, 800_000]
})

sample.to_csv("data/raw/sample.csv", index=False)
print("Wrote data/raw/sample.csv")
