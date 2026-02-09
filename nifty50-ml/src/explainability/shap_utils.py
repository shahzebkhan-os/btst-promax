try:
    import shap
except Exception:
    shap = None

def explain(model, X):
    if shap is None:
        return None
    explainer = shap.Explainer(model, X)
    return explainer(X)
