import numpy as np

class DriftMonitor:
    def __init__(self, threshold=0.2):
        self.threshold = threshold

    def psi(self, base, current, bins=10):
        base = np.array(base); current = np.array(current)
        q = np.linspace(0, 1, bins+1)
        cuts = np.quantile(base, q)
        def _hist(x):
            h,_ = np.histogram(x, bins=cuts)
            h = h / (h.sum() + 1e-9)
            return h
        b = _hist(base); c = _hist(current)
        return np.sum((c-b)*np.log((c+1e-9)/(b+1e-9)))

    def is_drift(self, base, current):
        return self.psi(base, current) > self.threshold
