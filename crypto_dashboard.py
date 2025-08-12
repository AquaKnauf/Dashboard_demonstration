import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("📊 Real-Time Crypto Dashboard")

# Refresh the app every 60 seconds
st_autorefresh(interval=60000, key="crypto_dashboard_autorefresh")

@st.cache_data(ttl=60)
def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d"
    }
    response = requests.get(url, params=params)
    return pd.DataFrame(response.json())

df = get_crypto_data()

if df.empty:
    st.error("⚠ Could not fetch data. Try again later.")
else:
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"Last updated: {last_update}")

    coins = df['name'].tolist()
    selected_coin = st.selectbox("Select a coin to view details:", coins)

    df["Mover"] = df["price_change_percentage_24h"].apply(
        lambda x: "🚀" if x and x > 5 else ("📉" if x and x < -5 else "")
    )

    st.subheader("Top 10 Cryptocurrencies")
    st.dataframe(
        df[["name", "symbol", "current_price", 
            "price_change_percentage_1h_in_currency",
            "price_change_percentage_24h", 
            "price_change_percentage_7d_in_currency", "Mover"]],
        use_container_width=True
    )

    coin_id = df[df["name"] == selected_coin]["id"].iloc[0]
    chart_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": 7, "interval": "hourly"}
    chart_data = requests.get(chart_url, params=params).json()

    if "prices" in chart_data:
        prices = pd.DataFrame(chart_data["prices"], columns=["Time", "Price"])
        prices["Time"] = pd.to_datetime(prices["Time"], unit="ms")
        prices = prices.set_index("Time")
        st.subheader(f"Price Trend for {selected_coin} (Last 7 Days)")
        st.line_chart(prices["Price"])
    else:
        st.warning("No chart data available.")
