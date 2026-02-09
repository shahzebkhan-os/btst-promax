import pandas as pd

POS_WORDS = {"beat","surge","up","bullish","strong","upgrade","record","optimistic","growth","outperform"}
NEG_WORDS = {"miss","drop","down","bearish","weak","downgrade","warn","cut","slow","underperform"}


def score_news(headlines: pd.Series) -> float:
    if headlines is None or headlines.empty:
        return 0.0
    score = 0
    for h in headlines.dropna().astype(str):
        tokens = {t.strip(".,:;!?()").lower() for t in h.split()}
        score += len(tokens & POS_WORDS)
        score -= len(tokens & NEG_WORDS)
    return score / max(len(headlines), 1)


def score_price_action(df: pd.DataFrame) -> float:
    if df is None or df.empty:
        return 0.0
    ret = df["close"].pct_change().dropna()
    if ret.empty:
        return 0.0
    return float(ret.tail(20).mean() / (ret.tail(20).std() + 1e-8))
