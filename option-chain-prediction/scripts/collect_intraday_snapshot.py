import argparse
import time
from datetime import datetime
import pandas as pd
from src.nse import fetch_option_chain, parse_chain_to_df
from src.universe import fetch_optionable_universe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", action="store_true", help="Use index chain endpoint")
    parser.add_argument("--sleep", type=float, default=0.6, help="Seconds between symbols")
    parser.add_argument("--out", default="data/intraday_snapshot.csv")
    args = parser.parse_args()

    universe = fetch_optionable_universe()["symbol"].tolist()
    rows = []
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for sym in universe:
        try:
            chain = fetch_option_chain(sym, is_index=args.index)
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
