import argparse
from datetime import datetime
import pandas as pd
from src.nse import fetch_option_chain, parse_chain_to_df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True, help="NSE symbol (e.g., NIFTY)")
    parser.add_argument("--index", action="store_true", help="Use index chain endpoint")
    parser.add_argument("--expiry", default=None, help="Filter expiry (e.g., 28-Feb-2026)")
    parser.add_argument("--out", default=None, help="Output CSV path")
    args = parser.parse_args()

    chain = fetch_option_chain(args.symbol, is_index=args.index)
    df = parse_chain_to_df(chain)
    if args.expiry:
        df = df[df["expiry"] == args.expiry]

    out = args.out or f"data/live_chain_{args.symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(out, index=False)
    print("Saved", out)


if __name__ == "__main__":
    main()
