from src.backtest.engine import backtest

def test_backtest():
    eq = backtest([0.01, -0.005])
    assert len(eq) == 3
