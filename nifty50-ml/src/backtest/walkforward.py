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


def walk_forward(returns, window=20, train_size=500, test_size=100, conf=0.55, fees=0.0005,
                 vol_target=0.01, slippage_bps=2, purge=5):
    # build sequences
    X = []
    Y = []
    for i in range(window, len(returns)-1):
        X.append(returns[i-window:i])
        Y.append(returns[i+1])
    X = np.array(X)[:, :, None]
    Y = np.array(Y)[:, None]

    all_strat = []
    step = test_size
    for start in range(0, len(X)-train_size-test_size-purge, step):
        train_end = start + train_size
        test_start = train_end + purge
        test_end = test_start + test_size
        X_train, y_train = X[start:train_end], Y[start:train_end]
        X_test, y_test = X[test_start:test_end], Y[test_start:test_end]

        # RandomForest on flattened features (baseline boost)
        from src.models.random_forest import RFModel
        rf = RFModel(n_estimators=300, max_depth=6)
        Xtr = X_train.reshape(len(X_train), -1)
        Xte = X_test.reshape(len(X_test), -1)
        y_cls = (y_train.flatten() > 0).astype(int)
        rf.fit(Xtr, y_cls)
        rf_preds = rf.predict_proba(Xte)

        # LSTM on sequences
        model = LSTM()
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
        loss_fn = nn.MSELoss()
        loader = DataLoader(SeqDataset(X_train, y_train), batch_size=64, shuffle=True)
        for _ in range(5):
            for xb,yb in loader:
                pred = model(xb)
                loss = loss_fn(pred, yb)
                opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad():
            lstm_preds = model(torch.tensor(X_test, dtype=torch.float32)).numpy().flatten()
        # scale LSTM preds to 0-1
        lmin, lmax = lstm_preds.min(), lstm_preds.max()
        lstm_probs = (lstm_preds - lmin) / (lmax - lmin + 1e-9)

        # ensemble: average probs
        preds = (rf_preds + lstm_probs) / 2

        # calibrate using train preds
        train_rf = rf.predict_proba(Xtr)
        with torch.no_grad():
            train_lstm = model(torch.tensor(X_train, dtype=torch.float32)).numpy().flatten()
        tmin, tmax = train_lstm.min(), train_lstm.max()
        train_lstm = (train_lstm - tmin) / (tmax - tmin + 1e-9)
        train_preds = (train_rf + train_lstm) / 2
        calib = Calibrator().fit(train_preds, y_cls)
        probs = calib.transform(preds)

        # temperature scaling to spread confidence
        temp = 0.8
        probs = np.clip((probs ** (1/temp)), 0, 1)

        signals = (probs >= conf).astype(int)
        # volatility-adjusted sizing
        realized = y_test.flatten()
        vol = np.std(realized) + 1e-9
        size = min(1.0, vol_target / vol)
        cost = slippage_bps/10000
        strat = realized * signals * size - cost*signals
        all_strat.extend(strat)

    equity = backtest(all_strat, fees=fees)
    return {
        "final_equity": float(np.round(equity[-1], 4)),
        "sharpe": float(np.round(sharpe(all_strat), 4)),
        "max_drawdown": float(np.round(max_drawdown(equity), 4)),
        "trades": int(np.sum(np.array(all_strat)!=0))
    }
