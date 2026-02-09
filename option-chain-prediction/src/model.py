from dataclasses import dataclass
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


@dataclass
class ModelConfig:
    n_estimators: int = 300
    max_depth: int = 12
    min_samples_split: int = 4


class OptionChainModel:
    def __init__(self, config: ModelConfig):
        self.model = RandomForestClassifier(
            n_estimators=config.n_estimators,
            max_depth=config.max_depth,
            min_samples_split=config.min_samples_split,
            random_state=42,
        )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict_proba(self, X: pd.DataFrame):
        return self.model.predict_proba(X)
