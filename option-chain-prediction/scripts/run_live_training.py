import subprocess
from pathlib import Path

# one-shot live training
Path("data/snapshots").mkdir(parents=True, exist_ok=True)

subprocess.run(["python3", "scripts/collect_intraday_snapshot.py", "--out", "data/snapshots/latest.csv"], check=False)
subprocess.run(["python3", "scripts/build_dataset_from_snapshots.py"], check=False)

if Path("data/train_live.csv").exists():
    subprocess.run(["python3", "-m", "src.train", "--data", "data/train_live.csv", "--out", "models_live.pkl", "--horizon", "1"], check=False)
