import pandas as pd


from .nse import fetch_option_chain, parse_chain_to_df


def load_option_chain(symbol: str, expiry: str, is_index: bool = True) -> pd.DataFrame:
    """Load option chain from NSE public endpoint."""
    chain = fetch_option_chain(symbol, is_index=is_index)
    df = parse_chain_to_df(chain)
    if expiry:
        df = df[df["expiry"] == expiry]
    return df


def load_underlying_ohlc(symbol: str) -> pd.DataFrame:
    """Placeholder for OHLC; NSE quote endpoint can be wired next."""
    return pd.DataFrame()
