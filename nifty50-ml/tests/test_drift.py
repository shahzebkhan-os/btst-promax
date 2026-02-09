from src.monitoring.drift import DriftMonitor

def test_drift():
    m = DriftMonitor()
    assert m.psi([1,2,3],[1,2,3]) >= 0
