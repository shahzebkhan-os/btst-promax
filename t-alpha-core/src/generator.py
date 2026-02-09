import uuid
from datetime import datetime, timezone

from .heatmap import build_heatmap_summary


def label_from_conf(conf):
    if conf >= 0.78:
        return "HIGH"
    if conf >= 0.55:
        return "MEDIUM"
    return "LOW"


def build_alert(symbol="AAPL", market="US"):
    ml_conf = 0.83
    heatmap = build_heatmap_summary()

    alert = {
        "alert_id": str(uuid.uuid4()),
        "mode": "SCAN",
        "symbol": symbol,
        "market": market,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "price": 185.25,
        "change_pct": 1.42,
        "trend": "STRONG_UPTREND",
        "key_level": 184.00,
        "volume_x": 2.1,
        "rsi": 61,
        "iv_percentile": 42,
        "ml_confidence": ml_conf,
        "ml_label": label_from_conf(ml_conf),
        "heatmap_summary": heatmap,
        "recommended_trade": {
            "strategy": "BUY_CALL",
            "strikes": [185],
            "expiry": "2026-03-20",
            "dte": 38,
            "entry_target": "2.40-2.65",
            "stop": 1.70,
            "capital": 300
        },
        "risk": {
            "max_loss": 300,
            "max_gain": 900,
            "breakeven": 187.65
        },
        "data_gaps": [],
        "model_version": "LGBM_v1.0",
        "model_hash": "abc123",
        "raw_metrics": {
            "top_features": ["volume_x", "rsi"],
            "sma_20": 183.2,
            "sma_50": 180.4,
            "sma_200": 170.1,
            "macd_hist": 0.8,
            "hv_30d": 0.22
        }
    }

    return alert
