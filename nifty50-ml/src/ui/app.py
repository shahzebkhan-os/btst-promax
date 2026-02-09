import streamlit as st
import pandas as pd
import subprocess
from src.pipeline.eta import ETAState

st.set_page_config(page_title="NIFTY50 ML", layout="wide")

st.title("NIFTY50 Options ML Dashboard")
st.caption("Research/Educational only — Not financial advice")

try:
    from src.ingest.universe import fetch_optionable_universe
    symbols = fetch_optionable_universe()
except Exception:
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

if st.button("Refresh Live Data & Re-Analyze"):
    with st.spinner("Running pipeline..."):
        subprocess.run(["python3", "-m", "src.pipeline.run_pipeline"], check=False)
    st.success("Pipeline completed. Reloading data...")
    st.rerun()

st.subheader("Progress")
progress = st.progress(1.0)
status = st.empty()
status.write("Idle · run refresh to update live data")

show_all = st.checkbox("Show all symbols", value=True)

st.subheader("Predictions")

st.info("RISK NOTICE: Educational only. Not financial advice.")
import os
import datetime as dt

# QoL controls
query = st.text_input("Search symbol", "").upper().strip()
option_filter = st.selectbox("Filter", ["ALL", "CALL", "PUT"]) 
row_limit = st.slider("Rows", 10, 200, 50, 10)

now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if os.path.exists("data/features/latest.csv"):
    df = pd.read_csv("data/features/latest.csv")
    if "last_update" not in df.columns:
        df["last_update"] = now_str
else:
    # demo predictions (same length as display list)
    display = symbols if show_all else symbols[:50]
    probs = [0.5 + (i % 10) * 0.01 for i in range(len(display))]
    df = pd.DataFrame({
        "symbol": display,
        "price": [100 + i for i in range(len(display))],
        "suggested_option": ["CALL" if i%2==0 else "PUT" for i in range(len(display))],
        "option_price": [round(50 + (i%10)*2.5,2) for i in range(len(display))],
        "option_value": [round(100 + (i%10)*5.0,2) for i in range(len(display))],
        "confidence": probs,
        "eta_sec": [round(5 - (i%5)*0.5,2) for i in range(len(display))],
        "last_update": [now_str for _ in range(len(display))]
    })

# Filters
if query:
    df = df[df["symbol"].str.contains(query, na=False)]
if option_filter != "ALL" and "suggested_option" in df.columns:
    df = df[df["suggested_option"] == option_filter]

# Sort by confidence if present
if "confidence" in df.columns:
    df = df.sort_values("confidence", ascending=False)

# Limit rows
if not show_all:
    df = df.head(row_limit)

# Color CALL/PUT
if "suggested_option" in df.columns:
    def color_call_put(val):
        if val == "CALL":
            return "color: #00c853; font-weight: 700;"
        if val == "PUT":
            return "color: #d50000; font-weight: 700;"
        return ""
    styled = df.style.applymap(color_call_put, subset=["suggested_option"])
    st.dataframe(styled, use_container_width=True)
else:
    st.dataframe(df, use_container_width=True)

st.caption(f"Last render: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
