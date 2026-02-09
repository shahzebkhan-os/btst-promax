import optuna
import numpy as np
from src.models.lstm import LSTMModel
import torch
from src.backtest.walkforward import walk_forward


def objective(trial, returns=None):
    hidden = trial.suggest_int("hidden", 16, 128)
    conf = trial.suggest_float("conf", 0.5, 0.7)
    purge = trial.suggest_int("purge", 2, 10)
    model = LSTMModel(5, hidden=hidden)
    _ = model  # placeholder for future integration
    if returns is None:
        return 1.0 / hidden
    stats = walk_forward(returns, conf=conf, purge=purge)
    return -stats["sharpe"]


def run_search(n_trials=10, returns=None):
    study = optuna.create_study(direction="minimize")
    study.optimize(lambda t: objective(t, returns=returns), n_trials=n_trials)
    best = study.best_params
    best["best_value"] = study.best_value
    return best
