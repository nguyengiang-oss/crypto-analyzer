import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="Crypto Analyzer", layout="centered", initial_sidebar_state="collapsed")

st.title("📱 Crypto Investment Analyzer - Dành cho iPhone")

coin_symbol = st.text_input("Nhập mã coin (BTC, ETH, SOL, XRP, DOGE...)", value="BTC").upper().strip()

period_options = {"1 tháng": "1mo", "3 tháng": "3mo", "6 tháng": "6mo", "1 năm": "1y", "2 năm": "2y", "5 năm": "5y"}
selected_period = st.selectbox("Chọn khoảng thời gian", options=list(period_options.keys()))
period = period_options[selected_period]

coin_map = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "xrp", "DOGE": "dogecoin", "ADA": "cardano", "BNB": "binancecoin", "AVAX": "avalanche-2", "TON": "the-open-network"}
coin_id = coin_map.get(coin_symbol, coin_symbol.lower())

ticker = f"{coin_symbol}-USD"
data = yf.download(ticker, period=period, progress=False, auto_adjust=True)

if data.empty:
    st.error("❌ Không tìm thấy coin. Thử BTC, ETH, SOL...")
    st.stop()

current_price = data['Close'][-1]

info = {}
try:
    r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", timeout=5)
    if r.status_code == 200:
        d = r.json()
        info = {"market_cap": d['market_data']['market_cap']['usd'], "volume_24h": d['market_data']['total_volume']['usd'], "rank": d['market_cap_rank'], "change_24h": d['market_data']['price_change_percentage_24h']}
except:
    pass

col1, col2, col3 = st.columns(3)
col1.metric("Giá hiện tại", f"${current_price:,.4f}", f"{info.get('change_24h', 0):.2f}%")
col2.metric("Market Cap", f"${info.get('market_cap', 0):,.0f}")
col3.metric("Rank", f"#{info.get('rank', 'N/A')}")

fig = go.Figure()
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Giá"))
fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(20).mean(), name="MA20", line=dict(color="orange")))
fig.update_layout(title=f"{coin_symbol} - {selected_period}", height=480, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("💰 Tính lời/lỗ nếu hold")
invest = st.number_input("Số tiền đầu tư (VND)", value=10_000_000, step=1_000_000)
days_ago = st.slider("Hold bao nhiêu ngày?", min_value=7, max_value=min(365, len(data)), value=30)
if st.button("Tính ngay"):
    buy_price = data['Close'].iloc[-days_ago]
    profit = invest * (current_price / buy_price - 1)
    if profit > 0:
        st.success(f"✅ LỜI: **{profit:,.0f} VND** (+{(current_price/buy_price-1)*100:.2f}%)")
    else:
        st.error(f"❌ LỖ: **{profit:,.0f} VND** ({(current_price/buy_price-1)*100:.2f}%)")

st.caption("Dữ liệu realtime • Không phải lời khuyên đầu tư • Code by Grok 2026")
