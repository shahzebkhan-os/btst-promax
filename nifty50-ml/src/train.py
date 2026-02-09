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
    args = p.parse_args()

    # demo data
    X = np.random.randn(200, 10, 5)
    y = np.random.randn(200, 1)

    ds = SeqDataset(X, y)
    dl = DataLoader(ds, batch_size=32, shuffle=True)
    model = LSTMModel(5)
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
