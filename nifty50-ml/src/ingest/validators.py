import pandas as pd

def validate_ohlc(df: pd.DataFrame) -> bool:
    required = {"Open","High","Low","Close"}
    return required.issubset(set(df.columns))
