import argparse
import time
from datetime import datetime
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=15, help="minutes")
    parser.add_argument("--cycles", type=int, default=4, help="number of retrain cycles")
    args = parser.parse_args()

    Path("data/snapshots").mkdir(parents=True, exist_ok=True)

    for i in range(args.cycles):
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        snapshot_path = f"data/snapshots/{ts}.csv"

        # collect snapshot
        subprocess.run(["python3", "scripts/collect_intraday_snapshot.py", "--out", snapshot_path], check=False)

        # build dataset
        subprocess.run(["python3", "scripts/build_dataset_from_snapshots.py"], check=False)

        # retrain model
        if Path("data/train_live.csv").exists():
            subprocess.run(["python3", "-m", "src.train", "--data", "data/train_live.csv", "--out", "models_live.pkl", "--horizon", "1"], check=False)

        if i < args.cycles - 1:
            time.sleep(args.interval * 60)


if __name__ == "__main__":
    main()
