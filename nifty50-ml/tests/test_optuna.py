from src.hpo.optuna_search import run_search

def test_optuna():
    params = run_search(1)
    assert "hidden" in params
