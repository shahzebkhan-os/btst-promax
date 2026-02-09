import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

class Calibrator:
    def __init__(self, method="isotonic"):
        self.method = method
        self.iso = None
        self.platt = None

    def fit(self, probs, y):
        probs = np.asarray(probs).reshape(-1, 1)
        y = np.asarray(y)
        if self.method == "platt":
            self.platt = LogisticRegression(solver="lbfgs")
            self.platt.fit(probs, y)
        else:
            self.iso = IsotonicRegression(out_of_bounds="clip")
            self.iso.fit(probs.ravel(), y)
        return self

    def transform(self, probs):
        probs = np.asarray(probs).reshape(-1, 1)
        if self.method == "platt" and self.platt is not None:
            return self.platt.predict_proba(probs)[:, 1]
        if self.iso is None:
            return probs.ravel()
        return self.iso.predict(probs.ravel())


class RegimeCalibrator:
    """Fit separate calibrators per regime."""
    def __init__(self, method_by_regime=None, default="isotonic"):
        self.method_by_regime = method_by_regime or {}
        self.default = default
        self.models = {}

    def fit(self, regimes, probs, y):
        regimes = np.asarray(regimes)
        probs = np.asarray(probs)
        y = np.asarray(y)
        for r in np.unique(regimes):
            mask = regimes == r
            method = self.method_by_regime.get(r, self.default)
            calib = Calibrator(method=method)
            calib.fit(probs[mask], y[mask])
            self.models[r] = calib
        return self

    def transform(self, regimes, probs):
        regimes = np.asarray(regimes)
        probs = np.asarray(probs)
        out = np.zeros_like(probs, dtype=float)
        for r in np.unique(regimes):
            mask = regimes == r
            calib = self.models.get(r)
            if calib is None:
                out[mask] = probs[mask]
            else:
                out[mask] = calib.transform(probs[mask])
        return out
