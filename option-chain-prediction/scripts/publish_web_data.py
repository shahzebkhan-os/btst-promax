import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
landing = root / "landing" / "data"
landing.mkdir(parents=True, exist_ok=True)

files = [
    root / "data" / "predictions.csv",
    root / "data" / "sentiment.json",
]

for f in files:
    if f.exists():
        shutil.copy(f, landing / f.name)
        print("Copied", f, "->", landing / f.name)
    else:
        print("Missing", f)
