import argparse
import pandas as pd
import joblib
from .pipeline import PipelineConfig, train_pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to training CSV")
    parser.add_argument("--out", default="models.pkl", help="Output model bundle")
    parser.add_argument("--horizon", type=int, default=1)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    config = PipelineConfig(horizon_days=args.horizon)
    bundle = train_pipeline(df, config)

    joblib.dump(bundle, args.out)
    print("Saved:", args.out)
    print("Metrics:", bundle["metrics"])


if __name__ == "__main__":
    main()
