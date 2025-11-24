import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import math

# --- पेज सेटिंग (Dark Theme Force) ---
st.set_page_config(page_title="Shikhar Pro Terminal", page_icon="🚀", layout="wide")

# --- CSS (पूरी वेबसाइट को डार्क और सुंदर बनाने के लिए) ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stMarkdown { color: white; }
    div[data-testid="stMetricValue"] { color: #00ff00; }
</style>
""", unsafe_allow_html=True)

# 🔑 API KEY & AI SETUP (GEMINI PRO - NO ERROR)
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("नाम: शिखर तिवारी")
    st.success("✅ Pro Dark Mode Activated")
    st.markdown("---")

st.title("📈 शिखर तिवारी - प्रो ट्रेडिंग टर्मिनल")
st.markdown("### 🚀 Professional Dark Charts & Option Chain")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट (F&O)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
if market_cat == "🇮🇳 इंडियन मार्केट (F&O)":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "FINNIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK", "SBIN"))
    if "NIFTY" in option: symbol = "^NSEI" if "50" in option else "^NSEBANK" if "BANK" in option else "NIFTY_FIN_SERVICE.NS"
    else: symbol = f"{option.replace(' ', '')}.NS"

elif market_cat == "💱 फॉरेक्स & गोल्ड":
    option = st.sidebar.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY"))
    if "GOLD" in option: symbol = "GC=F"
    elif "SILVER" in option: symbol = "SI=F"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"

elif market_cat == "🇺🇸 ग्लोबल मार्केट":
    symbol = "^IXIC"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 लाइव चार्ट (Dark)", "🎯 स्मार्ट ऑप्शन एंट्री", "📚 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: लाइव चार्ट (DARK MODE - जैसा आपने फोटो भेजा था)
# ==========================================
with tab1:
    if st.button(f"{symbol} चार्ट देखें 🚀", key="btn_chart"):
        with st.spinner('प्रो चार्ट लोड हो रहा है...'):
            try:
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

                    # सिग्नल लॉजिक
                    action = "WAIT (रुको)"
                    color = "#2962ff"
                    sl, tgt = 0.0, 0.0

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY (खरीदें) 🟢"
                        color = "#00ff00" # Neon Green
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL (बेचें) 🔴"
                        color = "#ff0000" # Neon Red
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)

                    # सिग्नल कार्ड (Dark Style)
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; background-color: #1e1e1e; text-align: center;">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: white; margin:5px;">Price: {price:.2f}</h2>
                        <div style="display: flex; justify-content: space-around; color: white;">
                            <span>🛑 SL: <b style="color: #ff4444;">{sl:.2f}</b></span>
                            <span>🎯 TGT: <b style="color: #00ff00;">{tgt:.2f}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- चार्ट (DARK THEME - TradingView Style) ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25])
                    
                    # Candles
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="Price", increasing_line_color='#089981', decreasing_line_color='#f23645'
                    ), row=1, col=1)

                    # EMAs
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='#2962ff', width=1), name="EMA 21"), row=1, col=1)
                    
                    # Volume (नीचे वाली रंगीन लाइनें)
                    vol_colors = ['#f23645' if c < o else '#089981' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)
                    
                    # Dark Layout
                    fig.update_layout(
                        template="plotly_dark", # डार्क मोड चालू
                        paper_bgcolor='#131722', plot_bgcolor='#131722',
                        height=700, title=f"{symbol} Pro Chart",
                        xaxis_rangeslider_visible=False, showlegend=False
                    )
                    # Grid को हल्का करना
                    fig.update_xaxes(showgrid=False); fig.update_yaxes(showgrid=True, gridcolor='#2a2e39')
                    
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: स्मार्ट ऑप्शन कैलकुलेटर (Buy/Sell Price)
# ==========================================
with tab2:
    st.header("🎯 ऑप्शन स्ट्राइक कैलकुलेटर")
    if st.button(f"{symbol} ऑप्शन स्कैन 🎲", key="opt_btn"):
        with st.spinner('कैलकुलेट हो रहा है...'):
            try:
                df = yf.Ticker(symbol).history(period="5d", interval="5m")
                if df.empty: st.error("डेटा नहीं मिला")
                else:
                    curr = df.iloc[-1]
                    spot_price = float(curr['Close'])
                    
                    # Trend Check
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    last = df.iloc[-1]
                    
                    trend = "SIDEWAYS"
                    if last['EMA_9'] > last['EMA_21']: trend = "UPTREND"
                    elif last['EMA_9'] < last['EMA_21']: trend = "DOWNTREND"

                    gap = 100 if "BANK" in symbol else 50
                    atm_strike = round(spot_price / gap) * gap
                    
                    rec_type, color = "WAIT", "gray"
                    est_premium = spot_price * 0.006 # Approximate premium

                    if trend == "UPTREND":
                        rec_type = "BUY CALL (CE)"
                        color = "green"
                    elif trend == "DOWNTREND":
                        rec_type = "BUY PUT (PE)"
                        color = "red"

                    buy_above = est_premium + 5

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("SPOT PRICE", f"{spot_price:.2f}")
                        st.info(f"ATM Strike: {atm_strike}")
                    with col2:
                        if color != "gray":
                            st.markdown(f"""
                            <div style="padding:10px; border:2px solid {color}; border-radius:10px; text-align:center; background-color: #262730;">
                                <h3 style="color:{'#00ff00' if color=='green' else '#ff4444'}; margin:0;">{rec_type}</h3>
                                <h2 style="color:white;">Strike: {atm_strike}</h2>
                                <p style="color:white;">Buy Above: <b>₹{buy_above:.2f}</b></p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("मार्केट साइडवेज है।")

            except Exception as e: st.error(str(e))

# ==========================================
# TAB 3: कैंडलस्टिक ज्ञान (HINDI)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक पैटर्न गाइड")
    
    patterns = [
        {"name": "Hammer (हथौड़ा) 🔨", "type": "Bullish", "desc": "गिरावट के बाद नीचे बनता है। मतलब तेजी आने वाली है।"},
        {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "तेजी के बाद ऊपर बनता है। मतलब मंदी आने वाली है।"},
        {"name": "Bullish Engulfing 📈", "type": "Strong Buy", "desc": "बड़ी हरी कैंडल ने लाल को पूरा ढक लिया।"},
        {"name": "Bearish Engulfing 📉", "type": "Strong Sell", "desc": "बड़ी लाल कैंडल ने हरी को पूरा ढक लिया।"}
    ]
    
    for pat in patterns:
        st.info(f"**{pat['name']}**\n\n{pat['desc']}")

# ==========================================
# TAB 4: AI गुरुजी (GEMINI PRO - FIXED)
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("सवाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            response = model.generate_content(prompt)
            st.chat_message("assistant").markdown(response.text)
        except Exception as e:
            st.error("AI कनेक्ट नहीं हो पा रहा।")
