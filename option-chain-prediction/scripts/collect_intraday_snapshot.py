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
    parser.add_argument("--sleep", type=float, default=1.5, help="Seconds between symbols")
    parser.add_argument("--out", default="data/intraday_snapshot.csv")
    parser.add_argument("--limit", type=int, default=0, help="Process first N symbols only")
    parser.add_argument("--symbols", default="", help="Comma-separated symbols to process")
    args = parser.parse_args()

    if args.symbols:
        universe = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    else:
        try:
            universe = fetch_optionable_universe()["symbol"].tolist()
        except Exception:
            universe = ["NIFTY", "BANKNIFTY"]

    if args.limit and args.limit > 0:
        universe = universe[: args.limit]

    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    first_write = True

    for sym in universe:
        try:
            is_index = sym in {"NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"}
            chain = fetch_option_chain(sym, is_index=is_index)
            df = parse_chain_to_df(chain)
            df["symbol"] = sym
            df["timestamp_utc"] = ts
            df.to_csv(args.out, mode="w" if first_write else "a", header=first_write, index=False)
            first_write = False
            time.sleep(args.sleep)
        except Exception:
            continue

    if not first_write:
        print("Saved", args.out)
    else:
        print("No data saved")


if __name__ == "__main__":
    main()
