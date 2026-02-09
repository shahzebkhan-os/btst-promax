import numpy as np
import pandas as pd

SUSPICIOUS = ("future", "lead", "t+", "next", "ahead")


def detect_leakage(df: pd.DataFrame, target_col: str, lookahead=1, max_abs_corr=0.995):
    """Basic leakage check: high corr with future target or suspicious names."""
    flags = []
    if target_col not in df.columns:
        return flags
    future = df[target_col].shift(-lookahead)
    numeric = df.select_dtypes(include="number")
    for col in numeric.columns:
        if col == target_col:
            continue
        name = str(col).lower()
        if any(k in name for k in SUSPICIOUS):
            flags.append(col)
            continue
        if future.isna().all():
            continue
        corr = pd.concat([numeric[col], future], axis=1).corr().iloc[0, 1]
        if corr is not None and abs(corr) >= max_abs_corr:
            flags.append(col)
    return sorted(set(flags))
