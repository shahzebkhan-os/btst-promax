import numpy as np


def detect_regime(vol, low=0.15, high=0.35):
    if vol < low:
        return "low"
    if vol > high:
        return "high"
    return "mid"


def detect_regime_series(vol_series, low=0.15, high=0.35):
    return np.where(vol_series < low, "low", np.where(vol_series > high, "high", "mid"))
