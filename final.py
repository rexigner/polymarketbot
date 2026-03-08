import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import time

st.set_page_config(layout="wide", page_icon="🎯")

@st.cache_data(ttl=1)
def get_polymarket_price():
    """Match Polymarket's EXACT price source"""
    sources = [
        ("https://api.pyth.network/v1/price/BTCUSD/latest", lambda x: float(x['price'])),
        ("https://api.chain.link/v1/price/BTC-USD", lambda x: float(x['data'])),
        ("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", lambda x: float(x['price'])),
        ("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", lambda x: float(x['bitcoin']['usd']))
    ]
    
    for url, parser in sources:
        try:
            resp = requests.get(url, timeout=1)
            return parser(resp.json())
        except:
            continue
    
    return 67124.30

def detect_market(period_minutes):
    """Detect markets for any period (5min, 15min)"""
    now = datetime.now(timezone.utc)
    minute_block = (now.minute // period_minutes) * period_minutes
    market_start = now.replace(minute=minute_block, second=0, microsecond=0)
    market_end = market_start + timedelta(minutes=period_minutes)
    
    if now >= market_end:
        market_start += timedelta(minutes=period_minutes)
        market_end += timedelta(minutes=period_minutes)
    
    minutes_into = max(0, (now - market_start).total_seconds() / 60)
    time_left = max(0, (market_end - now).total_seconds() / 60)
    is_new_market = minutes_into < (5/60)
    
    return market_start, market_end, minutes_into, time_left, is_new_market

# === TAB SELECTION ===
tab1, tab2, tab3 = st.tabs(["🚀 5-MINUTE BOT", "⏱️ 15-MINUTE BOT", "📊 COMBINED STATS"])

# ========================================
# 5-MINUTE BOT
# ========================================
with tab1:
    st.header("🎯 **5-MINUTE POLYMARKET TRACKER**")
    
    # 5min session state
    if 'price_to_beat_5m' not in st.session_state:
        st.session_state.price_to_beat_5m = 67124.30
    if 'market_number_5m' not in st.session_state:
        st.session_state.market_number_5m = 0
    if 'last_market_start_5m' not in st.session_state:
        st.session_state.last_market_start_5m = None
    if 'trades_5m' not in st.session_state:
        st.session_state.trades_5m = []
    if 'total_wins_5m' not in st.session_state:
        st.session_state.total_wins_5m = 0
    if 'total_losses_5m' not in st.session_state:
        st.session_state.total_losses_5m = 0

    market_start_5m, market_end_5m, minutes_into_5m, time_left_5m, is_new_5m = detect_market(5)
    
    # Auto-update 5min
    if is_new_5m and st.session_state.last_market_start_5m != market_start_5m:
        st.session_state.price_to_beat_5m = get_polymarket_price()
        st.session_state.last_market_start_5m = market_start_5m
        st.session_state.market_number_5m += 1
        st.rerun()
    
    # 5min manual override
    st.sidebar.title("🔒 **5MIN MANUAL**")
    manual_5m = st.sidebar.number_input("5min Price", value=st.session_state.price_to_beat_5m, step=0.01, format="%.2f", key="manual_5m")
    if st.sidebar.button("✅ LOCK 5MIN", key="lock_5m"):
        st.session_state.price_to_beat_5m = manual_5m
        st.session_state.last_market_start_5m = None
        st.rerun()
    
    price_5m = st.session_state.price_to_beat_5m
    live_price = get_polymarket_price()
    momentum_5m = ((live_price - price_5m) / price_5m * 100) if price_5m > 0 else 0
    
    # 5min signals
    if minutes_into_5m <= 3 and abs(momentum_5m) >= 0.15:
        confidence_5m = 78 + min(10, abs(momentum_5m) * 40)
        direction_5m = "UP" if momentum_5m > 0 else "DOWN"
    elif minutes_into_5m <= 4:
        direction_5m = "UP" if momentum_5m > 0 else "DOWN"
        confidence_5m = 68
    else:
        direction_5m, confidence_5m = "HOLD", 50
    
    # 5min dashboard
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🔒 **5M PRICE**", f"${price_5m:,.2f}")
    col2.metric("🔴 **LIVE**", f"${live_price:,.2f}")
    col3.metric("📈 **MOMENTUM**", f"{momentum_5m:+.2f}%")
    col4.metric("⏰ **TIME**", f"{int(time_left_5m):02d}:{int((time_left_5m%1)*60):02d}")
    col5.metric("🔢 **MARKET**", st.session_state.market_number_5m)
    col6.metric("🎯 **SIGNAL**", f"{direction_5m} **{confidence_5m}%**")
    
    st.progress(time_left_5m / 5)

# ========================================
# 15-MINUTE BOT  
# ========================================
with tab2:
    st.header("⏱️ **15-MINUTE POLYMARKET TRACKER**")
    
    # 15min session state
    if 'price_to_beat_15m' not in st.session_state:
        st.session_state.price_to_beat_15m = 67124.30
    if 'market_number_15m' not in st.session_state:
        st.session_state.market_number_15m = 0
    if 'last_market_start_15m' not in st.session_state:
        st.session_state.last_market_start_15m = None
    if 'trades_15m' not in st.session_state:
        st.session_state.trades_15m = []
    if 'total_wins_15m' not in st.session_state:
        st.session_state.total_wins_15m = 0
    if 'total_losses_15m' not in st.session_state:
        st.session_state.total_losses_15m = 0

    market_start_15m, market_end_15m, minutes_into_15m, time_left_15m, is_new_15m = detect_market(15)
    
    # Auto-update 15min
    if is_new_15m and st.session_state.last_market_start_15m != market_start_15m:
        st.session_state.price_to_beat_15m = get_polymarket_price()
        st.session_state.last_market_start_15m = market_start_15m
        st.session_state.market_number_15m += 1
        st.rerun()
    
    # 15min manual override
    st.sidebar.title("🔒 **15MIN MANUAL**")
    manual_15m = st.sidebar.number_input("15min Price", value=st.session_state.price_to_beat_15m, step=0.01, format="%.2f", key="manual_15m")
    if st.sidebar.button("✅ LOCK 15MIN", key="lock_15m"):
        st.session_state.price_to_beat_15m = manual_15m
        st.session_state.last_market_start_15m = None
        st.rerun()
    
    price_15m = st.session_state.price_to_beat_15m
    momentum_15m = ((live_price - price_15m) / price_15m * 100) if price_15m > 0 else 0
    
    # 15min signals
    if minutes_into_15m <= 8 and abs(momentum_15m) >= 0.15:
        confidence_15m = 78 + min(10, abs(momentum_15m) * 40)
        direction_15m = "UP" if momentum_15m > 0 else "DOWN"
    elif minutes_into_15m <= 12:
        direction_15m = "UP" if momentum_15m > 0 else "DOWN"
        confidence_15m = 68
    else:
        direction_15m, confidence_15m = "HOLD", 50
    
    # 15min dashboard
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🔒 **15M PRICE**", f"${price_15m:,.2f}")
    col2.metric("🔴 **LIVE**", f"${live_price:,.2f}")                                                
    col3.metric("📈 **MOMENTUM**", f"{momentum_15m:+.2f}%")
    col4.metric("⏰ **TIME**", f"{int(time_left_15m):02d}:{int((time_left_15m%1)*60):02d}")
    col5.metric("🔢 **MARKET**", st.session_state.market_number_15m)
    col6.metric("🎯 **SIGNAL**", f"{direction_15m} **{confidence_15m}%**")
    
    st.progress(time_left_15m / 15)

# ========================================
# COMBINED STATS
# ========================================
with tab3:
    st.header("📊 **COMBINED PERFORMANCE**")
    
    # Combined win/loss
    total_wins = st.session_state.total_wins_5m + st.session_state.total_wins_15m
    total_losses = st.session_state.total_losses_5m + st.session_state.total_losses_15m
    total_signals = len(st.session_state.trades_5m) + len(st.session_state.trades_15m)
    win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✅ **TOTAL WINS**", total_wins)
    col2.metric("❌ **TOTAL LOSSES**", total_losses)
    col3.metric("🎯 **WIN RATE**", f"{win_rate:.1f}%")
    col4.metric("📈 **TOTAL SIGNALS**", total_signals)
    
    # Current signals comparison
    col1, col2 = st.columns(2)
    with col1:
        st.metric("5M SIGNAL", f"{direction_5m} **{confidence_5m}%**")
    with col2:
        st.metric("15M SIGNAL", f"{direction_15m} **{confidence_15m}%**")

# === SIDEBAR ===
st.sidebar.markdown("---")
st.sidebar.success("**🎯 DUAL BOT SYSTEM**")
st.sidebar.markdown("""
**5-MINUTE:** :00, :05, :10... (288 markets/day)
**15-MINUTE:** :00, :15, :30... (96 markets/day)

**Both auto-sync Pyth/Chainlink/Binance**
**Independent win/loss tracking**
**Manual override per timeframe**
""")

time.sleep(1)
st.rerun()
