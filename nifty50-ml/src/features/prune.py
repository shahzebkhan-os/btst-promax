import pandas as pd
import numpy as np


def prune_by_correlation(df: pd.DataFrame, threshold=0.95):
    corr = df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [c for c in upper.columns if any(upper[c] > threshold)]
    return df.drop(columns=to_drop, errors="ignore"), to_drop
