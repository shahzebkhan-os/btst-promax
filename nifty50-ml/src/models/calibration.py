import numpy as np
from sklearn.isotonic import IsotonicRegression

class Calibrator:
    def __init__(self):
        self.iso = IsotonicRegression(out_of_bounds="clip")

    def fit(self, probs, y):
        self.iso.fit(probs, y)
        return self

    def transform(self, probs):
        return self.iso.predict(probs)
