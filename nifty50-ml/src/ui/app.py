import streamlit as st
import pandas as pd
import subprocess
import os
import datetime as dt
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

# Override prices from NSE bulk option-chain CSV if available
bulk_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "nse_fno_bulk_option_chain.csv"))
if os.path.exists(bulk_path):
    try:
        bulk = pd.read_csv(bulk_path)
        if not bulk.empty and "symbol" in bulk.columns and "underlying" in bulk.columns:
            if "timestamp" in bulk.columns:
                bulk["timestamp"] = pd.to_datetime(bulk["timestamp"], errors="coerce")
                bulk = bulk.sort_values("timestamp")
            latest_underlying = bulk.groupby("symbol", as_index=False).tail(1)[["symbol", "underlying"]]
            price_map = dict(zip(latest_underlying["symbol"], latest_underlying["underlying"]))
            df["price_nse"] = df["symbol"].map(price_map)
            df["price"] = df["price_nse"].fillna(df.get("price"))
    except Exception:
        pass

# Filters
if query:
    df = df[df["symbol"].str.contains(query, na=False)]
if option_filter != "ALL" and "suggested_option" in df.columns:
    df = df[df["suggested_option"] == option_filter]

# Sort by confidence if present
if "confidence" in df.columns:
    df = df.sort_values("confidence", ascending=False)

# Deduplicate to one row per symbol (keeps highest confidence)
if "symbol" in df.columns:
    df = df.drop_duplicates(subset=["symbol"], keep="first")

# Limit rows
if not show_all:
    df = df.head(row_limit)

# Rewrite table (clean columns + NSE price override where available)
col_order = [
    "symbol",
    "price",
    "suggested_option",
    "option_price",
    "option_value",
    "confidence",
    "model_accuracy",
    "model_coverage",
    "regime",
    "last_update",
]
existing = [c for c in col_order if c in df.columns]
view = df[existing].copy()
if "confidence" in view.columns:
    view["confidence"] = (view["confidence"] * 100).round(2)

# Color CALL/PUT
if "suggested_option" in view.columns:
    def color_call_put(val):
        if val == "CALL":
            return "color: #00c853; font-weight: 700;"
        if val == "PUT":
            return "color: #d50000; font-weight: 700;"
        return ""
    styled = view.style.map(color_call_put, subset=["suggested_option"])
    st.dataframe(
        styled,
        use_container_width=True,
        column_config={
            "symbol": st.column_config.TextColumn("Symbol"),
            "price": st.column_config.NumberColumn("Price (NSE if available)", format="%.2f"),
            "suggested_option": st.column_config.TextColumn("Option"),
            "option_price": st.column_config.NumberColumn("Option Price", format="%.2f"),
            "option_value": st.column_config.NumberColumn("Option Value", format="%.2f"),
            "confidence": st.column_config.NumberColumn("Confidence %", format="%.2f"),
            "model_accuracy": st.column_config.NumberColumn("Model Acc %", format="%.2f"),
            "model_coverage": st.column_config.NumberColumn("Coverage %", format="%.2f"),
            "regime": st.column_config.TextColumn("Regime"),
            "last_update": st.column_config.TextColumn("Updated"),
        },
    )
else:
    st.dataframe(view, use_container_width=True)

file_ts = ""
if os.path.exists("data/features/latest.csv"):
    file_ts = dt.datetime.fromtimestamp(os.path.getmtime("data/features/latest.csv")).strftime('%Y-%m-%d %H:%M:%S')

st.caption(f"Last render: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data file: {file_ts}")
