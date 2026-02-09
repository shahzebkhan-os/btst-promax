import argparse
import pandas as pd
import joblib
from .pipeline import make_features


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to inference CSV")
    parser.add_argument("--model", required=True, help="Model bundle path")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    bundle = joblib.load(args.model)

    X = make_features(df)
    Xs = bundle["scaler"].transform(X)

    iv_pred = bundle["iv_model"].predict(Xs)
    oi_pred = bundle["oi_model"].predict(Xs)
    dir_prob = bundle["dir_model"].predict_proba(Xs)[:, 1]

    out = df.copy()
    out["pred_iv_delta"] = iv_pred
    out["pred_oi_delta"] = oi_pred
    out["pred_premium_up_prob"] = dir_prob

    out.to_csv("data/predictions.csv", index=False)
    out[["pred_iv_delta","pred_oi_delta","pred_premium_up_prob"]].tail(5).to_csv("data/predictions_tail.csv", index=False)
    print(out.tail(5))


if __name__ == "__main__":
    main()
