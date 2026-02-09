import lightgbm as lgb
import numpy as np

class StackedEnsemble:
    def __init__(self):
        self.model = lgb.LGBMRegressor(n_estimators=100)
    def fit(self, X, y):
        self.model.fit(X, y)
    def predict(self, X):
        return self.model.predict(X)
