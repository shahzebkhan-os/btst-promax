import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from src.backtest.engine import backtest
from src.backtest.analytics import sharpe, max_drawdown
from src.models.calibration import Calibrator

class SeqDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
    def __len__(self): return len(self.X)
    def __getitem__(self, i): return self.X[i], self.y[i]

class LSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(1, 32, batch_first=True)
        self.fc = nn.Linear(32, 1)
    def forward(self, x):
        o,_ = self.lstm(x)
        return self.fc(o[:,-1])


def walk_forward(returns, window=20, train_size=500, test_size=100, conf=0.6, fees=0.0005, vol_target=0.01):
    # build sequences
    X = []
    Y = []
    for i in range(window, len(returns)-1):
        X.append(returns[i-window:i])
        Y.append(returns[i+1])
    X = np.array(X)[:, :, None]
    Y = np.array(Y)[:, None]

    all_strat = []
    for start in range(0, len(X)-train_size-test_size, test_size):
        X_train, y_train = X[start:start+train_size], Y[start:start+train_size]
        X_test, y_test = X[start+train_size:start+train_size+test_size], Y[start+train_size:start+train_size+test_size]

        model = LSTM()
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
        loss_fn = nn.MSELoss()
        loader = DataLoader(SeqDataset(X_train, y_train), batch_size=64, shuffle=True)
        for _ in range(2):
            for xb,yb in loader:
                pred = model(xb)
                loss = loss_fn(pred, yb)
                opt.zero_grad(); loss.backward(); opt.step()

        with torch.no_grad():
            preds = model(torch.tensor(X_test, dtype=torch.float32)).numpy().flatten()

        # calibrate using train preds
        with torch.no_grad():
            train_preds = model(torch.tensor(X_train, dtype=torch.float32)).numpy().flatten()
        train_y = (y_train.flatten() > 0).astype(int)
        calib = Calibrator().fit(train_preds, train_y)
        probs = calib.transform(preds)

        signals = (probs >= conf).astype(int)
        # volatility-adjusted sizing
        realized = y_test.flatten()
        vol = np.std(realized) + 1e-9
        size = min(1.0, vol_target / vol)
        strat = realized * signals * size
        all_strat.extend(strat)

    equity = backtest(all_strat, fees=fees)
    return {
        "final_equity": float(np.round(equity[-1], 4)),
        "sharpe": float(np.round(sharpe(all_strat), 4)),
        "max_drawdown": float(np.round(max_drawdown(equity), 4)),
        "trades": int(np.sum(np.array(all_strat)!=0))
    }
