from fastapi import FastAPI
from .worker import WorkerPool

app = FastAPI()
state = {"total": 0, "done": 0, "eta": 0}

@app.get("/progress")
def progress():
    return state

@app.post("/simulate")
def simulate():
    pool = WorkerPool(workers=2)
    symbols = ["RELIANCE","TCS","INFY"]
    state["total"] = len(symbols)
    def fn(s):
        import time; time.sleep(0.2)
        return s
    pool.run(symbols, fn)
    state["done"] = len(symbols)
    state["eta"] = pool.get_eta([])
    return state
