import glob
import pandas as pd
import numpy as np
from datetime import datetime


def build_feature_row(df: pd.DataFrame) -> dict:
    # pick expiry with max OI
    df = df.copy()
    if df.empty:
        return {}

    underlying = df["underlying"].dropna().iloc[0] if df["underlying"].notna().any() else np.nan
    df["dist"] = (df["strike"] - underlying).abs()
    atm = df.sort_values("dist").head(1)
    if atm.empty:
        return {}

    atm_strike = atm["strike"].iloc[0]
    ce_atm = df[(df["type"] == "CE") & (df["strike"] == atm_strike)]
    pe_atm = df[(df["type"] == "PE") & (df["strike"] == atm_strike)]

    # OTM: next strikes
    ce_otm = df[(df["type"] == "CE") & (df["strike"] > atm_strike)].sort_values("strike").head(1)
    pe_otm = df[(df["type"] == "PE") & (df["strike"] < atm_strike)].sort_values("strike", ascending=False).head(1)

    iv_atm = pd.concat([ce_atm["iv"], pe_atm["iv"]]).mean()
    iv_call_otm = ce_otm["iv"].mean() if not ce_otm.empty else np.nan
    iv_put_otm = pe_otm["iv"].mean() if not pe_otm.empty else np.nan

    oi_atm = pd.concat([ce_atm["oi"], pe_atm["oi"]]).mean()
    oi_atm_prev = oi_atm
    oi_put = df[df["type"] == "PE"]["oi"].sum()
    oi_call = df[df["type"] == "CE"]["oi"].sum()

    ask_atm = pd.concat([ce_atm["ask"], pe_atm["ask"]]).mean()
    bid_atm = pd.concat([ce_atm["bid"], pe_atm["bid"]]).mean()
    mid_atm = pd.concat([ce_atm["ltp"], pe_atm["ltp"]]).mean()
    volume_atm = pd.concat([ce_atm["volume"], pe_atm["volume"]]).mean()

    return {
        "underlying_close": underlying,
        "underlying_volume": np.nan,
        "iv_atm": iv_atm,
        "iv_put_otm": iv_put_otm,
        "iv_call_otm": iv_call_otm,
        "iv_near": iv_atm,
        "iv_next": iv_atm,
        "oi_atm": oi_atm,
        "oi_atm_prev": oi_atm_prev,
        "oi_put": oi_put,
        "oi_call": oi_call,
        "ask_atm": ask_atm,
        "bid_atm": bid_atm,
        "mid_atm": mid_atm,
        "premium_atm": mid_atm,
        "volume_atm": volume_atm,
    }


def main():
    files = sorted(glob.glob("data/snapshots/*.csv"))
    rows = []
    for f in files:
        df = pd.read_csv(f)
        if "symbol" not in df.columns:
            continue
        for sym, grp in df.groupby("symbol"):
            row = build_feature_row(grp)
            if row:
                row["symbol"] = sym
                row["timestamp"] = f.split("/")[-1].replace(".csv", "")
                rows.append(row)

    if rows:
        out = pd.DataFrame(rows)
        out.to_csv("data/train_live.csv", index=False)
        print("Saved data/train_live.csv")
    else:
        print("No rows built")


if __name__ == "__main__":
    main()
