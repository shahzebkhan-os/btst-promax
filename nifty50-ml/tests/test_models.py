import torch
from src.models.lstm import LSTMModel

def test_lstm_forward():
    m = LSTMModel(5)
    x = torch.randn(2,10,5)
    y = m(x)
    assert y.shape[0] == 2
