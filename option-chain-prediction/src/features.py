import pandas as pd
import numpy as np


def compute_features(chain: pd.DataFrame, underlying: pd.DataFrame) -> pd.DataFrame:
    """Compute feature set from option chain + underlying."""
    if chain.empty or underlying.empty:
        return pd.DataFrame()

    df = chain.copy()
    # Example features (placeholders)
    df['iv_skew'] = df.get('iv_put', np.nan) - df.get('iv_call', np.nan)
    df['oi_change_rate'] = (df.get('oi', 0) - df.get('oi_prev', 0)) / df.get('oi_prev', 1)
    df['bid_ask_spread'] = (df.get('ask', 0) - df.get('bid', 0)) / df.get('mid', 1)
    return df
