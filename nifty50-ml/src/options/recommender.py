import numpy as np
from .suggestion import rank_options


def recommend(options, p_up, risk_limit=0.02):
    ranked = rank_options(options, p_up=p_up)
    # simple position size
    for r in ranked:
        r["size"] = max(1, int(risk_limit*100))
    return ranked
