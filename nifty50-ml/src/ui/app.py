import streamlit as st
import pandas as pd
from src.pipeline.eta import ETAState

st.set_page_config(page_title="NIFTY50 ML", layout="wide")

st.title("NIFTY50 Options ML Dashboard")
st.caption("Research/Educational only — Not financial advice")

symbols = [
    "ADANIPORTS","ASIANPAINT","AXISBANK","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV",
    "BPCL","BHARTIARTL","BRITANNIA","CIPLA","COALINDIA","DIVISLAB","DRREDDY",
    "EICHERMOT","GRASIM","HCLTECH","HDFCBANK","HDFCLIFE","HEROMOTOCO",
    "HINDALCO","HINDUNILVR","ICICIBANK","INDUSINDBK","INFY","ITC",
    "JSWSTEEL","KOTAKBANK","LT","M&M","MARUTI","NESTLEIND",
    "NTPC","ONGC","POWERGRID","RELIANCE","SBIN","SHREECEM",
    "SUNPHARMA","TATAMOTORS","TATASTEEL","TCS","TECHM","TITAN",
    "ULTRACEMCO","UPL","WIPRO","ADANIENT","APOLLOHOSP"
]
eta = ETAState()

st.subheader("Progress")
progress = st.progress(0)
status = st.empty()

for i, s in enumerate(symbols, 1):
    eta.update(s, 0.2)
    progress.progress(i/len(symbols))
    status.write(f"Processed {s} · ETA {eta.estimate(symbols[i:], workers=2):.2f}s")

st.subheader("Predictions")

st.info("RISK NOTICE: Educational only. Not financial advice.")
# demo predictions (same length as symbols)
probs = [0.5 + (i % 10) * 0.01 for i in range(len(symbols))]
df = pd.DataFrame({
    "symbol": symbols,
    "price": [100 + i for i in range(len(symbols))],
    "return_1d": [0.01*((i%5)-2) for i in range(len(symbols))],
    "rsi": [40 + (i%20) for i in range(len(symbols))],
    "macd": [0.1*((i%7)-3) for i in range(len(symbols))],
    "iv": [0.2 + (i%10)*0.01 for i in range(len(symbols))],
    "pcr": [0.8 + (i%5)*0.05 for i in range(len(symbols))],
    "d_oi": [1000 + (i%10)*50 for i in range(len(symbols))],
    "delta": [0.4 + (i%6)*0.05 for i in range(len(symbols))],
    "gamma": [0.01 + (i%5)*0.002 for i in range(len(symbols))],
    "vega": [0.12 + (i%5)*0.03 for i in range(len(symbols))],
    "suggested_option": ["CALL" if i%2==0 else "PUT" for i in range(len(symbols))],
    "confidence": probs,
    "eta_sec": [round(5 - (i%5)*0.5,2) for i in range(len(symbols))],
    "last_update": ["2026-02-10 02:40" for _ in range(len(symbols))]
})
st.dataframe(df, use_container_width=True)
