from src.paper_exec.paper_exec import simulate_order

def test_sim():
    r = simulate_order(100, 10)
    assert r["cost"] > 0
