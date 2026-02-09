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
df = pd.DataFrame({"symbol": symbols, "p_up": [0.61,0.54,0.66,0.58]})
st.dataframe(df, use_container_width=True)
