import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
from datetime import datetime

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Global Trade", page_icon="🌍", layout="wide")

# ==========================================
# 🔑 आपकी चाबी (API KEY)
# ==========================================
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

# --- AI मॉडल ---
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except:
    pass

# --- साइडबार: यूजर प्रोफाइल ---
with st.sidebar:
    st.header("👤 यूजर प्रोफाइल")
    st.info("**नाम:** शिखर तिवारी (ईशान पंडित)")
    st.warning("**Mobile:** 93360-92738")
    st.success("**Email:** shikhartiwari9336@gmail.com")
    st.markdown("---")

st.title("🌍 शिखर तिवारी - ग्लोबल मार्केट & फॉरेक्स बॉट")
st.markdown("### 🚀 XAUUSD, GBPUSD, Global Stocks & Indian Market")

# ==========================================
# ⚙️ मार्केट सिलेक्शन (पूरी दुनिया)
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("कैटेगरी:", 
    ("💱 फॉरेक्स & कमोडिटी (Global)", "🇮🇳 इंडियन मार्केट", "🇺🇸 US & ग्लोबल इंडेक्स", "₿ क्रिप्टो"))

symbol = ""
# 1. फॉरेक्स और कमोडिटी (Gold, Silver etc)
if market_cat == "💱 फॉरेक्स & कमोडिटी (Global)":
    option = st.sidebar.selectbox("पेयर चुनें:", 
        ("GOLD (XAU/USD)", "SILVER (XAG/USD)", "GBP/USD", "EUR/USD", "USD/JPY", "USD/INR", "CRUDE OIL"))
    
    if "GOLD" in option: symbol = "GC=F"      # Gold Futures
    elif "SILVER" in option: symbol = "SI=F"  # Silver Futures
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"
    elif "JPY" in option: symbol = "JPY=X"
    elif "INR" in option: symbol = "INR=X"
    elif "CRUDE" in option: symbol = "CL=F"

# 2. इंडियन मार्केट
elif market_cat == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("शेयर/इंडेक्स:", 
        ("NIFTY 50", "BANK NIFTY", "SENSEX", "RELIANCE", "TATA MOTORS", "HDFC BANK", "SBIN", "INFY", "ADANI ENT"))
    
    if option == "NIFTY 50": symbol = "^NSEI"
    elif option == "BANK NIFTY": symbol = "^NSEBANK"
    elif option == "SENSEX": symbol = "^BSESN"
    else: symbol = f"{option.replace(' ', '')}.NS" # Spaces hata kar .NS lagana

# 3. ग्लोबल इंडेक्स (US, UK, Japan)
elif market_cat == "🇺🇸 US & ग्लोबल इंडेक्स":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", 
        ("NASDAQ 100 (US)", "S&P 500 (US)", "DOW JONES (US)", "TESLA", "APPLE", "GOOGLE", "AMAZON", "NVIDIA", "NIKKEI 225 (Japan)", "FTSE 100 (UK)"))
    
    if "NASDAQ" in option: symbol = "^IXIC"
    elif "S&P" in option: symbol = "^GSPC"
    elif "DOW" in option: symbol = "^DJI"
    elif "TESLA" in option: symbol = "TSLA"
    elif "APPLE" in option: symbol = "AAPL"
    elif "GOOGLE" in option: symbol = "GOOGL"
    elif "AMAZON" in option: symbol = "AMZN"
    elif "NVIDIA" in option: symbol = "NVDA"
    elif "NIKKEI" in option: symbol = "^N225"
    elif "FTSE" in option: symbol = "^FTSE"

# 4. क्रिप्टो
elif market_cat == "₿ क्रिप्टो":
    option = st.sidebar.selectbox("कॉइन:", ("Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)", "Dogecoin"))
    symbol = "BTC-USD" if "Bit" in option else "ETH-USD" if "Eth" in option else "SOL-USD" if "Sol" in option else "DOGE-USD"

# टाइमफ्रेम
timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute (Scalping)", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2 = st.tabs(["📊 सिग्नल & लेवल्स", "🤖 AI गुरुजी"])

# TAB 1: चार्ट और सिग्नल
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀"):
        with st.spinner('मार्केट डेटा और सिग्नल्स लोड हो रहे हैं...'):
            try:
                # टाइमफ्रेम लॉजिक
                p, i = ("1y", "1d")
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"

                # डेटा डाउनलोड
                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty:
                    st.error(f"❌ डेटा नहीं मिला ({symbol})। मार्केट बंद हो सकता है।")
                else:
                    # --- सुपर इंडिकेटर्स ---
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    df['ATR'] = df.ta.atr(length=14)

                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    
                    # ATR फिक्स (Error हटाने के लिए)
                    atr = 0
                    if 'ATR' in df.columns and not pd.isna(curr['ATR']):
                        atr = float(curr['ATR'])
                    else:
                        atr = price * 0.01

                    # --- सिग्नल लॉजिक (Buy/Sell/SL/Target) ---
                    action = "WAIT (इंतजार करें)"
                    color = "blue"
                    sl = 0.0
                    tgt = 0.0
                    reason = "मार्केट साइडवेज है।"

                    # BUY Condition
                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY (खरीदें) 🟢"
                        color = "green"
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                        reason = "EMA 9 ऊपर है (Uptrend)। RSI पॉजिटिव है।"
                    
                    # SELL Condition
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL (बेचें) 🔴"
                        color = "red"
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)
                        reason = "EMA 9 नीचे है (Downtrend)। RSI नेगेटिव है।"

                    # --- नोटिफिकेशन अलर्ट (On Screen) ---
                    st.markdown(f"""
                    <div style="padding: 20px; background-color: {'#d4edda' if color == 'green' else '#f8d7da' if color == 'red' else '#e2e3e5'}; border-radius: 12px; border: 2px solid {color};">
                        <h2 style="color: {color}; text-align: center; margin:0;">📢 ALERT: {action}</h2>
                        <h3 style="text-align: center; margin:0;">Price: {price:.2f}</h3>
                        <hr>
                        <p style="text-align: center; font-size: 18px;">
                            <b>👤 Trader:</b> Shikhar Tiwari<br>
                            <b>🛑 Stop Loss:</b> {sl:.2f}<br>
                            <b>🎯 Target:</b> {tgt:.2f}<br>
                            <b>💡 Reason:</b> {reason}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")

                    # --- 2. चार्ट (Candles + EMA) ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])

                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)
                    
                    # RSI
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', name="RSI")), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red")
                    fig.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green")

                    fig.update_layout(height=600, xaxis_rangeslider_visible=False, title=f"{symbol} Analysis")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# TAB 2: AI चैट
with tab2:
    st.header("🤖 Shikhar's AI Expert")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).markdown(m["content"])
    
    if prompt := st.chat_input("मार्केट का हाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            with st.chat_message("assistant"):
                with st.spinner("AI सोच रहा है..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e: st.error(f"Error: {e}")
