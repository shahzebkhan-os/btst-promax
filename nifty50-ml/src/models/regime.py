import numpy as np


def detect_regime(vol, low=0.15, high=0.35):
    if vol < low:
        return "low"
    if vol > high:
        return "high"
    return "mid"
