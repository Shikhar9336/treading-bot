import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import math

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Trading Master", page_icon="⚙️", layout="wide")

# ==========================================
# 🎨 थीम और सेटिंग्स (User Control)
# ==========================================
with st.sidebar:
    st.header("⚙️ डिस्प्ले सेटिंग्स")
    
    # 1. थीम बटन
    theme_choice = st.radio("थीम चुनें:", ("Dark Mode (काला)", "Light Mode (सफेद)"))
    
    # थीम के अनुसार रंग सेट करना
    if "Dark" in theme_choice:
        bg_color = "#0e1117"
        text_color = "white"
        card_bg = "#1e1e1e"
        chart_template = "plotly_dark"
        grid_color = "#2a2e39"
        # डार्क CSS
        st.markdown("""
        <style>
            .stApp { background-color: #0e1117; color: white; }
            .stMarkdown, h1, h2, h3, p, label { color: white !important; }
            div[data-testid="stSidebar"] { background-color: #262730; }
            .stMetric { background-color: #262730; border: 1px solid #444; }
        </style>
        """, unsafe_allow_html=True)
    else:
        bg_color = "#ffffff"
        text_color = "black"
        card_bg = "#f9f9f9"
        chart_template = "plotly_white"
        grid_color = "#f0f0f0"
        # लाइट CSS
        st.markdown("""
        <style>
            .stApp { background-color: #ffffff; color: black; }
            .stMarkdown, h1, h2, h3, p, label { color: black !important; }
            div[data-testid="stSidebar"] { background-color: #f0f2f6; }
            .stMetric { background-color: #ffffff; border: 1px solid #ddd; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("---")

# ==========================================
# 🧮 रिस्क कैलकुलेटर (NEW FEATURE)
# ==========================================
with st.sidebar:
    with st.expander("🧮 पोजीशन कैलकुलेटर (New)"):
        st.caption("ट्रेड लेने से पहले चेक करें")
        capital = st.number_input("पूंजी (Capital):", value=10000)
        risk_pct = st.number_input("रिस्क (%):", value=2.0)
        entry = st.number_input("एंट्री प्राइस:", value=100.0)
        sl_price = st.number_input("स्टॉप लॉस:", value=95.0)
        
        if st.button("कैलकुलेट करें"):
            risk_amt = capital * (risk_pct / 100)
            loss_per_share = entry - sl_price
            if loss_per_share > 0:
                qty = math.floor(risk_amt / loss_per_share)
                st.success(f"✅ केवल **{qty}** शेयर खरीदें")
                st.info(f"अधिकतम नुकसान: ₹{risk_amt:.2f}")
            else:
                st.error("Stop Loss एंट्री से कम होना चाहिए!")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except: pass

st.title("📈 शिखर तिवारी - ट्रेडिंग टर्मिनल")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    market_cat = st.selectbox("मार्केट:", ("🇮🇳 इंडियन मार्केट (F&O)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

with col2:
    symbol = ""
    if "इंडियन" in market_cat:
        option = st.selectbox("सिंबल:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK"))
        if "NIFTY" in option: symbol = "^NSEI" if "50" in option else "^NSEBANK"
        else: symbol = f"{option.replace(' ', '')}.NS"
    elif "फॉरेक्स" in market_cat:
        option = st.selectbox("सिंबल:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD"))
        if "GOLD" in option: symbol = "GC=F"
        elif "SILVER" in option: symbol = "SI=F"
        elif "GBP" in option: symbol = "GBPUSD=X"
        elif "EUR" in option: symbol = "EURUSD=X"
    elif "ग्लोबल" in market_cat:
        symbol = "^IXIC"
    elif "क्रिप्टो" in market_cat:
        symbol = "BTC-USD"

with col3:
    timeframe = st.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 लाइव चार्ट", "🎯 स्मार्ट ऑप्शन चेन", "📚 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: लाइव चार्ट (Dynamic Theme)
# ==========================================
with tab1:
    if st.button(f"{symbol} चार्ट देखें 🚀"):
        with st.spinner('चार्ट बन रहा है...'):
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

                    # सिग्नल
                    action = "WAIT"
                    color = "#2962ff"
                    sl, tgt = 0.0, 0.0

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY 🟢"
                        color = "#00c853" # Green
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL 🔴"
                        color = "#ff3d00" # Red
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)

                    # कार्ड (Theme Based Colors)
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; background-color: {card_bg}; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: {text_color}; margin:5px;">LTP: ₹{price:.2f}</h2>
                        <div style="display: flex; justify-content: space-around; color: {text_color};">
                            <span>🛑 SL: <b>{sl:.2f}</b></span>
                            <span>🎯 TGT: <b>{tgt:.2f}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # चार्ट (Dynamic Theme)
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25])
                    
                    # Candles
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="Price", increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'
                    ), row=1, col=1)

                    # EMAs
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)
                    
                    # Volume
                    vol_colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)
                    
                    # Layout Update based on Theme
                    fig.update_layout(
                        template=chart_template, # Magic Line for Theme
                        paper_bgcolor=bg_color,
                        plot_bgcolor=bg_color,
                        height=650, title=f"{symbol} Chart",
                        xaxis_rangeslider_visible=False, showlegend=False
                    )
                    fig.update_xaxes(showgrid=True, gridcolor=grid_color)
                    fig.update_yaxes(showgrid=True, gridcolor=grid_color)
                    
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: स्मार्ट ऑप्शन कैलकुलेटर
# ==========================================
with tab2:
    st.header("🎯 ऑप्शन स्ट्राइक & प्रीमियम")
    if st.button("ऑप्शन डेटा निकालें 🎲"):
        with st.spinner('Calculating...'):
            try:
                df = yf.Ticker(symbol).history(period="5d", interval="5m")
                if df.empty: st.error("No Data")
                else:
                    curr = df.iloc[-1]
                    spot = float(curr['Close'])
                    
                    # Trend
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    last = df.iloc[-1]
                    
                    trend = "SIDEWAYS"
                    if last['EMA_9'] > last['EMA_21']: trend = "UPTREND"
                    elif last['EMA_9'] < last['EMA_21']: trend = "DOWNTREND"

                    gap = 100 if "BANK" in symbol else 50
                    atm = round(spot / gap) * gap
                    
                    rec, col = "WAIT", "gray"
                    est_prem = spot * 0.006

                    if trend == "UPTREND":
                        rec = "BUY CALL (CE)"
                        col = "green"
                    elif trend == "DOWNTREND":
                        rec = "BUY PUT (PE)"
                        col = "red"

                    buy_above = est_prem + 5

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("SPOT PRICE", f"{spot:.2f}")
                        st.info(f"ATM: {atm}")
                    with col2:
                        if col != "gray":
                            st.markdown(f"""
                            <div style="padding:10px; border:2px solid {col}; border-radius:10px; text-align:center; background-color:{card_bg}; color:{text_color};">
                                <h3 style="color:{col}; margin:0;">{rec}</h3>
                                <h2>Strike: {atm}</h2>
                                <p>Buy Above: <b>₹{buy_above:.2f}</b></p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("मार्केट साइडवेज है।")

            except Exception as e: st.error(str(e))

# ==========================================
# TAB 3: कैंडल ज्ञान (Theme Adaptive)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक पैटर्न")
    
    # Theme के हिसाब से कार्ड का कलर
    info_bg = "#262730" if "Dark" in theme_choice else "#e3f2fd"
    info_text = "white" if "Dark" in theme_choice else "black"

    patterns = [
        {"name": "Hammer 🔨", "type": "Bullish", "desc": "गिरावट के बाद बनता है, तेजी का संकेत।"},
        {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "तेजी के बाद बनता है, मंदी का संकेत।"},
        {"name": "Bullish Engulfing 📈", "type": "Strong Buy", "desc": "हरी कैंडल ने लाल को खा लिया।"},
        {"name": "Bearish Engulfing 📉", "type": "Strong Sell", "desc": "लाल कैंडल ने हरी को खा लिया।"}
    ]
    
    for pat in patterns:
        st.markdown(f"""
        <div style="background-color: {info_bg}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="color: {info_text}; margin:0;">{pat['name']}</h4>
            <p style="color: {info_text};">{pat['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 4: AI गुरुजी
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
        except: st.error("AI Busy")
