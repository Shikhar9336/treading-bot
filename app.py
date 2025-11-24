import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Trading Terminal", page_icon="📈", layout="wide")

# ==========================================
# 🔑 API KEY
# ==========================================
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except:
    pass

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("नाम: शिखर तिवारी")
    st.success("Angel One / Groww स्टाइल चार्ट")
    st.markdown("---")

st.title("📈 शिखर तिवारी - प्रो ट्रेडिंग टर्मिनल")
st.markdown("### 🚀 Angel One Style Chart & Analysis")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("मार्केट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
if market_cat == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "HDFC BANK", "TATA MOTORS", "SBIN", "INFY", "ADANI ENT"))
    symbol = "^NSEI" if "NIFTY" in option else "^NSEBANK" if "BANK" in option else f"{option.replace(' ', '')}.NS"

elif market_cat == "💱 फॉरेक्स & गोल्ड":
    option = st.sidebar.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY"))
    if "GOLD" in option: symbol = "GC=F"
    elif "SILVER" in option: symbol = "SI=F"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"
    elif "JPY" in option: symbol = "JPY=X"

elif market_cat == "🇺🇸 ग्लोबल मार्केट":
    option = st.sidebar.selectbox("इंडेक्स:", ("NASDAQ 100", "S&P 500", "TESLA", "APPLE", "GOOGLE", "AMAZON"))
    symbol = "^IXIC" if "NASDAQ" in option else "^GSPC" if "S&P" in option else "TSLA" if "TESLA" in option else "AAPL" if "APPLE" in option else "GOOGL"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3 = st.tabs(["📊 लाइव चार्ट (Angel Style)", "📚 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: एंजेल वन / ग्रो जैसा चार्ट (White)
# ==========================================
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀"):
        with st.spinner('डेटा लोड हो रहा है...'):
            try:
                # टाइमफ्रेम लॉजिक
                p, i = ("1y", "1d")
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"

                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला (मार्केट बंद हो सकता है)")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    df['ATR'] = df.ta.atr(length=14)
                    
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    
                    # ATR फिक्स
                    atr = 0
                    if 'ATR' in df.columns and not pd.isna(curr['ATR']):
                        atr = float(curr['ATR'])
                    else: atr = price * 0.01

                    # सिग्नल लॉजिक
                    action = "WAIT (इंतजार करें)"
                    color = "#2962ff" # Blue
                    sl, tgt = 0.0, 0.0
                    reason = "मार्केट साइडवेज है"

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY (खरीदें) 🟢"
                        color = "#008F4C" # Angel One Green
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                        reason = "Trend ऊपर है (EMA 9 > 21)"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL (बेचें) 🔴"
                        color = "#D32F2F" # Angel One Red
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)
                        reason = "Trend नीचे है (EMA 9 < 21)"

                    # --- कार्ड (Normal White Theme) ---
                    st.markdown(f"""
                    <div style="padding: 20px; border: 2px solid {color}; border-radius: 10px; background-color: #ffffff; text-align: center; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: #333; margin:5px;">Price: {price:.2f}</h2>
                        <hr>
                        <div style="display: flex; justify-content: space-around; color: #333;">
                            <p>🛑 SL: <b style="color: red;">{sl:.2f}</b></p>
                            <p>🎯 TGT: <b style="color: green;">{tgt:.2f}</b></p>
                            <p>📈 RSI: <b>{curr['RSI']:.2f}</b></p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- चार्ट (Angel One Style - White Background) ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                        vertical_spacing=0.03, row_heights=[0.75, 0.25])

                    # Candles (Green/Red Classic)
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="Price",
                        increasing_line_color='#008F4C', # Dark Green
                        decreasing_line_color='#D32F2F'  # Dark Red
                    ), row=1, col=1)

                    # EMAs
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)

                    # Volume
                    vol_colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)

                    # Layout (White Background)
                    fig.update_layout(
                        paper_bgcolor='white', # सफेद बैकग्राउंड
                        plot_bgcolor='white',  # सफेद चार्ट एरिया
                        height=700,
                        title=f"{symbol} Chart",
                        xaxis_rangeslider_visible=False,
                        showlegend=False
                    )
                    
                    # Grid Lines (Light Gray)
                    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
                    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: कैंडलस्टिक ज्ञान (Hindi)
# ==========================================
with tab2:
    st.header("📚 कैंडलस्टिक पैटर्न गाइड")
    
    patterns = [
        {"name": "Hammer (हथौड़ा) 🔨", "type": "Bullish", "desc": "बाजार गिरने के बाद बनता है। अब ऊपर जाएगा।"},
        {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "बाजार चढ़ने के बाद बनता है। अब नीचे गिरेगा।"},
        {"name": "Bullish Engulfing 📈", "type": "Strong Buy", "desc": "बड़ी हरी कैंडल ने लाल को खा लिया। तेजी आएगी।"},
        {"name": "Bearish Engulfing 📉", "type": "Strong Sell", "desc": "बड़ी लाल कैंडल ने हरी को खा लिया। मंदी आएगी।"},
        {"name": "Doji ➕", "type": "Neutral", "desc": "मार्केट कन्फ्यूज है। अभी रुको।"}
    ]

    col1, col2 = st.columns(2)
    for i, pat in enumerate(patterns):
        with col1 if i % 2 == 0 else col2:
            st.info(f"**{pat['name']}**\n\n{pat['desc']}")

# ==========================================
# TAB 3: AI
# ==========================================
with tab3:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
        except Exception as e: st.error(str(e))
