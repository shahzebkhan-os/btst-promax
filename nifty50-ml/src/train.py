import argparse
import pandas as pd
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

class SeqDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
    def __len__(self): return len(self.X)
    def __getitem__(self, i): return self.X[i], self.y[i]

class LSTMModel(nn.Module):
    def __init__(self, n_features, hidden=32):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, 1)
    def forward(self, x):
        o,_ = self.lstm(x)
        return self.fc(o[:,-1])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="RELIANCE")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--demo", action="store_true")
    p.add_argument("--min_stocks", type=int, default=25)
    args = p.parse_args()

    # real multi-stock data (Yahoo)
    from src.ingest.universe import fetch_optionable_universe
    from src.ingest.connectors import fetch_yahoo_ohlc

    symbols = fetch_optionable_universe()[:max(args.min_stocks, 25)]
    X_list, y_list = [], []
    window = 20
    for sym in symbols:
        df = fetch_yahoo_ohlc(sym, period="10y", interval="1d")
        if df.empty or "Close" not in df.columns:
            continue
        close = df["Close"].astype(float).to_numpy().squeeze()
        returns = np.diff(close) / close[:-1]
        for i in range(window, len(returns)-1):
            X_list.append(returns[i-window:i])
            y_list.append(returns[i+1])

    X = np.array(X_list)[:, :, None]
    y = np.array(y_list)[:, None]

    ds = SeqDataset(X, y)
    dl = DataLoader(ds, batch_size=64, shuffle=True)
    model = LSTMModel(1)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    for e in range(args.epochs):
        for xb,yb in dl:
            pred = model(xb)
            loss = loss_fn(pred, yb)
            opt.zero_grad(); loss.backward(); opt.step()
        print(f"epoch {e+1} loss {loss.item():.4f}")

if __name__ == "__main__":
    main()
