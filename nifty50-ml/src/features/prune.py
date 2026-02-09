import pandas as pd
import numpy as np


def prune_by_correlation(df: pd.DataFrame, threshold=0.95):
    corr = df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [c for c in upper.columns if any(upper[c] > threshold)]
    return df.drop(columns=to_drop, errors="ignore"), to_drop


def prune_by_l1(df: pd.DataFrame, target, C=0.1, max_features=50):
    """L1 logistic selection for sparse features."""
    from sklearn.linear_model import LogisticRegression

    X = df.fillna(0.0)
    y = np.asarray(target).ravel()
    if len(np.unique(y)) < 2:
        return X, []
    model = LogisticRegression(penalty="l1", solver="liblinear", C=C, max_iter=200)
    model.fit(X, y)
    coefs = np.abs(model.coef_).ravel()
    ranked = pd.Series(coefs, index=X.columns).sort_values(ascending=False)
    keep = ranked[ranked > 0].index.tolist()[:max_features]
    if not keep:
        keep = ranked.index.tolist()[:max_features]
    return X[keep], [c for c in X.columns if c not in keep]


def prune_by_shap(df: pd.DataFrame, target, max_features=50):
    """Tree + SHAP-based pruning (falls back to correlation if SHAP unavailable)."""
    try:
        import shap
        from sklearn.ensemble import RandomForestClassifier
        X = df.fillna(0.0)
        y = np.asarray(target).ravel()
        if len(np.unique(y)) < 2:
            return X, []
        model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1)
        model.fit(X, y)
        explainer = shap.TreeExplainer(model)
        vals = explainer.shap_values(X)
        if isinstance(vals, list):
            vals = vals[1] if len(vals) > 1 else vals[0]
        importance = np.abs(vals).mean(axis=0)
        ranked = pd.Series(importance, index=X.columns).sort_values(ascending=False)
        keep = ranked.index.tolist()[:max_features]
        return X[keep], [c for c in X.columns if c not in keep]
    except Exception:
        return prune_by_correlation(df, threshold=0.98)
