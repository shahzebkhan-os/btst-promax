import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .eta import ETAState

class WorkerPool:
    def __init__(self, workers=4):
        self.workers = workers
        self.eta = ETAState()
        self.progress = {}

    def process_symbol(self, symbol, fn):
        start = time.time()
        result = fn(symbol)
        self.eta.update(symbol, time.time() - start)
        self.progress[symbol] = 100
        return result

    def run(self, symbols, fn):
        self.progress = {s: 0 for s in symbols}
        results = []
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futs = {ex.submit(self.process_symbol, s, fn): s for s in symbols}
            for f in as_completed(futs):
                results.append(f.result())
        return results

    def get_eta(self, remaining):
        return self.eta.estimate(remaining, self.workers)
