import numpy as np

def rank_options(candidates, p_up=0.6):
    scored = []
    for c in candidates:
        score = (p_up*c.get("payoff",1)) - c.get("cost",1)
        scored.append((score,c))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _,c in scored]
