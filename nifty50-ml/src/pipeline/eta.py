from dataclasses import dataclass
import time
from typing import Dict, List

@dataclass
class ETAState:
    alpha: float = 0.3
    timings: Dict[str, float] = None

    def __post_init__(self):
        if self.timings is None:
            self.timings = {}

    def update(self, symbol: str, measured: float):
        prev = self.timings.get(symbol, measured)
        self.timings[symbol] = self.alpha * measured + (1 - self.alpha) * prev

    def estimate(self, remaining: List[str], workers: int = 1) -> float:
        total = sum(self.timings.get(s, 1.0) for s in remaining)
        return total / max(workers, 1)
