import argparse
from .data import load_option_chain, load_underlying_ohlc
from .features import compute_features


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--expiry", required=True)
    args = parser.parse_args()

    chain = load_option_chain(args.symbol, args.expiry)
    underlying = load_underlying_ohlc(args.symbol)
    features = compute_features(chain, underlying)

    if features.empty:
        print("No data. Plug in real data sources.")
        return

    print(features.head())


if __name__ == "__main__":
    main()
