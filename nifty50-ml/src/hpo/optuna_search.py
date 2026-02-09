import optuna
from src.models.lstm import LSTMModel
import torch

def objective(trial):
    hidden = trial.suggest_int("hidden", 16, 128)
    model = LSTMModel(5, hidden=hidden)
    # demo loss
    return 1.0 / hidden

def run_search(n_trials=10):
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    return study.best_params
