import argparse
import json
from pathlib import Path

from .generator import build_alert
from .validator import validate_alert


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", default="US")
    parser.add_argument("--symbol", default="AAPL")
    args = parser.parse_args()

    alert = build_alert(symbol=args.symbol, market=args.market)

    schema_path = Path(__file__).parents[1] / "schema" / "alert_schema.json"
    validate_alert(alert, schema_path)

    output_dir = Path(__file__).parents[1] / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "sample_alert.json"

    with open(out_path, "w") as f:
        json.dump(alert, f, indent=2)

    print(f"[SCANNING: {args.market}] → [FOUND: 1 SETUPS] → [TOP ALERT: {args.symbol}]")
    print(json.dumps(alert, indent=2))


if __name__ == "__main__":
    main()
