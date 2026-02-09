import argparse
import time
import os
import sys
from datetime import datetime
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.nse import fetch_option_chain, parse_chain_to_df
from src.universe import fetch_optionable_universe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sleep", type=float, default=0.8, help="Seconds between symbols")
    parser.add_argument("--out", default="data/intraday_snapshot.csv")
    args = parser.parse_args()

    try:
        universe = fetch_optionable_universe()["symbol"].tolist()
    except Exception:
        universe = ["NIFTY", "BANKNIFTY"]

    rows = []
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for sym in universe:
        try:
            is_index = sym in {"NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"}
            chain = fetch_option_chain(sym, is_index=is_index)
            df = parse_chain_to_df(chain)
            df["symbol"] = sym
            df["timestamp_utc"] = ts
            rows.append(df)
            time.sleep(args.sleep)
        except Exception:
            continue

    if rows:
        out = pd.concat(rows, ignore_index=True)
        out.to_csv(args.out, index=False)
        print("Saved", args.out)
    else:
        print("No data saved")


if __name__ == "__main__":
    main()
