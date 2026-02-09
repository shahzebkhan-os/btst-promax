from dataclasses import dataclass
from typing import Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, roc_auc_score
from xgboost import XGBRegressor, XGBClassifier


@dataclass
class PipelineConfig:
    horizon_days: int = 1
    intraday_minutes: int = 60
    test_size: float = 0.2
    random_state: int = 42


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering for NSE option chains."""
    f = pd.DataFrame(index=df.index)
    f["underlying_return_1"] = df["underlying_close"].pct_change(1)
    f["underlying_return_5"] = df["underlying_close"].pct_change(5)
    f["rv_5"] = df["underlying_close"].pct_change().rolling(5).std()
    f["rv_20"] = df["underlying_close"].pct_change().rolling(20).std()
    f["volume_x"] = df["underlying_volume"] / df["underlying_volume"].rolling(30).mean()

    f["iv_atm"] = df["iv_atm"]
    f["iv_skew"] = df["iv_put_otm"] - df["iv_call_otm"]
    f["iv_term"] = df["iv_near"] - df["iv_next"]

    f["oi_atm"] = df["oi_atm"]
    f["oi_change"] = (df["oi_atm"] - df["oi_atm_prev"]) / df["oi_atm_prev"].replace(0, np.nan)
    f["pcr"] = df["oi_put"] / df["oi_call"].replace(0, np.nan)

    f["spread_atm"] = (df["ask_atm"] - df["bid_atm"]) / df["mid_atm"].replace(0, np.nan)

    return f.replace([np.inf, -np.inf], np.nan).fillna(method="ffill").fillna(method="bfill")


def make_targets(df: pd.DataFrame, horizon_days: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Targets: ΔIV, premium direction, ΔOI for next day."""
    iv_delta = df["iv_atm"].shift(-horizon_days) - df["iv_atm"]
    prem_dir = (df["premium_atm"].shift(-horizon_days) > df["premium_atm"]).astype(int)
    oi_delta = df["oi_atm"].shift(-horizon_days) - df["oi_atm"]
    return iv_delta, prem_dir, oi_delta


def train_pipeline(df: pd.DataFrame, config: PipelineConfig):
    X = make_features(df)
    y_iv, y_dir, y_oi = make_targets(df, config.horizon_days)

    valid = y_iv.notna() & y_dir.notna() & y_oi.notna()
    X, y_iv, y_dir, y_oi = X[valid], y_iv[valid], y_dir[valid], y_oi[valid]

    X_train, X_test, y_iv_train, y_iv_test, y_dir_train, y_dir_test, y_oi_train, y_oi_test = train_test_split(
        X, y_iv, y_dir, y_oi, test_size=config.test_size, random_state=config.random_state
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    iv_model = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9)
    oi_model = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9)
    dir_model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9)

    iv_model.fit(X_train_s, y_iv_train)
    oi_model.fit(X_train_s, y_oi_train)
    dir_model.fit(X_train_s, y_dir_train)

    iv_pred = iv_model.predict(X_test_s)
    oi_pred = oi_model.predict(X_test_s)
    dir_pred = dir_model.predict_proba(X_test_s)[:, 1]

    metrics = {
        "iv_mae": float(mean_absolute_error(y_iv_test, iv_pred)),
        "oi_mae": float(mean_absolute_error(y_oi_test, oi_pred)),
        "dir_auc": float(roc_auc_score(y_dir_test, dir_pred)) if len(set(y_dir_test)) > 1 else None,
    }

    return {
        "scaler": scaler,
        "iv_model": iv_model,
        "oi_model": oi_model,
        "dir_model": dir_model,
        "metrics": metrics,
    }
