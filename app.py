import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import math

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Master Bot", page_icon="🚀", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("शिखर तिवारी (ईशान पंडित)")
    st.success("✅ Signals + Option Chain Fix")
    st.markdown("---")

st.title("📈 शिखर तिवारी - मास्टर ट्रेडिंग बॉट")
st.markdown("### 🚀 Live Signals, Targets & Smart Option Chain")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट (F&O)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
is_opt = False

if market_cat == "🇮🇳 इंडियन मार्केट (F&O)":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK", "SBIN"))
    if "NIFTY" in option:
        symbol = "^NSEI" if "50" in option else "^NSEBANK"
        is_opt = True # यह ऑप्शन वाला है
    else: 
        symbol = f"{option.replace(' ', '')}.NS"

elif market_cat == "💱 फॉरेक्स & गोल्ड":
    option = st.sidebar.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY"))
    if "GOLD" in option: symbol = "GC=F"
    elif "SILVER" in option: symbol = "SI=F"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"
    elif "JPY" in option: symbol = "JPY=X"

elif market_cat == "🇺🇸 ग्लोबल मार्केट":
    symbol = "^IXIC"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["⚡ सिग्नल्स (Live)", "🎯 स्मार्ट ऑप्शन चैन", "📚 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: सिग्नल्स (वापस आ गया!)
# ==========================================
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀", key="btn1"):
        with st.spinner('मार्केट एनालाइज हो रहा है...'):
            try:
                # टाइमफ्रेम लॉजिक
                p, i = ("1y", "1d")
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"

                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty: st.error("❌ डेटा नहीं मिला")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    df['ATR'] = df.ta.atr(length=14)
                    
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    atr = float(curr['ATR']) if 'ATR' in df.columns and not pd.isna(curr['ATR']) else price * 0.01

                    # --- सिग्नल लॉजिक (Main Logic) ---
                    action = "WAIT (इंतजार करें)"
                    color = "#2962ff"
                    sl, tgt = 0.0, 0.0
                    msg = "मार्केट अभी साइडवेज है, ट्रेड न लें।"

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY (खरीदें) 🟢"
                        color = "#00c853" # Green
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                        msg = "ट्रेंड ऊपर है। कॉल (CE) या Buy साइड रहें।"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL (बेचें) 🔴"
                        color = "#ff3d00" # Red
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)
                        msg = "ट्रेंड नीचे है। पुट (PE) या Sell साइड रहें।"

                    # --- सिग्नल कार्ड (वापस आ गया) ---
                    st.markdown(f"""
                    <div style="padding: 20px; border: 3px solid {color}; border-radius: 15px; background-color: {'#e8f5e9' if 'BUY' in action else '#ffebee' if 'SELL' in action else '#f3f4f6'}; text-align: center;">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: #333;">Price: {price:.2f}</h2>
                        <hr>
                        <div style="display: flex; justify-content: space-around; font-size: 20px; color: #333;">
                            <p>🛑 SL: <b style="color: red;">{sl:.2f}</b></p>
                            <p>🎯 TGT: <b style="color: green;">{tgt:.2f}</b></p>
                        </div>
                        <p style="color: #555;">💡 <b>सलाह:</b> {msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- चार्ट (Angel One Style) ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1.5), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1.5), name="EMA 21"), row=1, col=1)
                    vol_colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)
                    
                    fig.update_layout(height=600, paper_bgcolor='white', plot_bgcolor='white', xaxis_rangeslider_visible=False, showlegend=False, title=f"{symbol} Live Chart")
                    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0'); fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: स्मार्ट ऑप्शन कैलकुलेटर (FIXED)
# ==========================================
with tab2:
    st.header("🎯 ऑप्शन स्ट्राइक कैलकुलेटर (No Errors)")
    
    if st.button("स्ट्राइक प्राइस निकालें 🎲"):
        with st.spinner('कैलकुलेट हो रहा है...'):
            try:
                # करंट प्राइस लाओ
                data = yf.Ticker(symbol).history(period="1d", interval="1m")
                if data.empty:
                    st.error("डेटा नहीं मिला")
                else:
                    spot_price = data['Close'].iloc[-1]
                    
                    # --- स्ट्राइक प्राइस का गणित (Maths) ---
                    # Nifty का स्ट्राइक 50 के अंतर पर होता है, BankNifty का 100 पर
                    step = 100 if "BANK" in symbol else 50 if "NSEI" in symbol else 10 
                    
                    # ATM (At The Money) निकालना
                    atm_strike = round(spot_price / step) * step
                    
                    # रेजिस्टेंस और सपोर्ट (Pivot Points Formula)
                    high = data['High'].max()
                    low = data['Low'].min()
                    close = data['Close'].iloc[-1]
                    pivot = (high + low + close) / 3
                    r1 = (2 * pivot) - low
                    s1 = (2 * pivot) - high

                    st.metric("अभी का भाव (Spot Price)", f"₹{spot_price:.2f}")

                    # --- कार्ड ---
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"🟢 अगर खरीदना है (CALL):")
                        st.markdown(f"""
                        - **Strike:** {atm_strike} CE (Call)
                        - **Support:** {s1:.2f} (यहाँ से उठ सकता है)
                        """)
                    with col2:
                        st.error(f"🔴 अगर बेचना है (PUT):")
                        st.markdown(f"""
                        - **Strike:** {atm_strike} PE (Put)
                        - **Resistance:** {r1:.2f} (यहाँ से गिर सकता है)
                        """)
                    
                    st.info(f"💡 **टिप:** अगर भाव {r1:.2f} को तोड़ दे तो Call लें। अगर {s1:.2f} को तोड़ दे तो Put लें।")

            except Exception as e: st.error(f"Calculation Error: {e}")

# ==========================================
# TAB 3: कैंडल लाइब्रेरी (HINDI)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक पैटर्न")
    cols = st.columns(2)
    patterns = [
        {"name": "Hammer 🔨", "type": "Bullish", "desc": "गिरावट खत्म, अब ऊपर जाएगा।"},
        {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "तेजी खत्म, अब नीचे गिरेगा।"},
        {"name": "Bullish Engulfing 📈", "type": "Strong Buy", "desc": "हरी ने लाल को खा लिया।"},
        {"name": "Bearish Engulfing 📉", "type": "Strong Sell", "desc": "लाल ने हरी को खा लिया।"}
    ]
    for i, pat in enumerate(patterns):
        with cols[i%2]:
            st.info(f"**{pat['name']}**\n\n{pat['desc']}")

# ==========================================
# TAB 4: AI
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
        except Exception as e: st.error(str(e))
