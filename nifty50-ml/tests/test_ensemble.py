import numpy as np
from src.models.random_forest import RFModel

def test_ensemble_shapes():
    X = np.random.randn(20, 5)
    y = (np.random.rand(20) > 0.5).astype(int)
    rf = RFModel(n_estimators=5)
    rf.fit(X, y)
    p = rf.predict_proba(X)
    assert p.shape[0] == 20
