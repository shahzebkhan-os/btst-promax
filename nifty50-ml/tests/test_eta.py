from src.pipeline.eta import ETAState

def test_eta():
    eta = ETAState(alpha=0.5)
    eta.update("A", 2.0)
    assert eta.estimate(["A"]) > 0
