from src.models.random_forest import RFModel
import numpy as np

def test_rf():
    X = np.random.randn(50, 5)
    y = (np.random.rand(50) > 0.5).astype(int)
    m = RFModel(n_estimators=10)
    m.fit(X, y)
    p = m.predict_proba(X)
    assert len(p) == 50
