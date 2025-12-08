import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Master Bot", page_icon="⚙️", layout="wide")

# ==========================================
# 🎛️ कस्टमाइज सेटिंग्स (USER CONTROL)
# ==========================================
with st.sidebar:
    st.header("⚙️ अपनी सेटिंग्स खुद करें")
    
    # 1. थीम सेटिंग (Dark vs Light)
    theme_choice = st.radio("🎨 थीम चुनें:", ("Light Mode (सफेद)", "Dark Mode (काला)"))
    
    # 2. चार्ट सेटिंग
    chart_type = st.selectbox("📊 चार्ट का प्रकार:", ("Candlestick", "Line Chart"))
    
    # 3. इंडिकेटर ऑन/ऑफ
    show_ema = st.checkbox("Show EMA Lines", value=True)
    show_vol = st.checkbox("Show Volume", value=True)
    
    st.markdown("---")

# --- CSS (थीम बदलने का जादू) ---
if "Light" in theme_choice:
    # लाइट मोड (जबरदस्ती सफेद करना)
    st.markdown("""
    <style>
        .stApp { background-color: #ffffff; color: black; }
        .stMarkdown, h1, h2, h3, p { color: black !important; }
        div[data-testid="stSidebar"] { background-color: #f0f2f6; }
        .stMetric { background-color: #f9f9f9; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)
    chart_template = "plotly_white"
else:
    # डार्क मोड
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: white; }
        .stMarkdown, h1, h2, h3, p { color: white !important; }
        .stMetric { background-color: #262730; }
    </style>
    """, unsafe_allow_html=True)
    chart_template = "plotly_dark"

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

st.title("📈 शिखर तिवारी - मास्टर कंट्रोल टर्मिनल")

# ==========================================
# मार्केट सिलेक्शन
# ==========================================
col1, col2, col3 = st.columns(3)
with col1:
    market_cat = st.selectbox("मार्केट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल", "₿ क्रिप्टो"))

with col2:
    symbol = ""
    if "इंडियन" in market_cat:
        opt = st.selectbox("सिंबल:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "HDFC BANK", "TATA MOTORS"))
        symbol = "^NSEI" if "NIFTY" in opt else "^NSEBANK" if "BANK" in opt else f"{opt.replace(' ','')}.NS"
    elif "फॉरेक्स" in market_cat:
        opt = st.selectbox("सिंबल:", ("GOLD (XAUUSD)", "SILVER", "EUR/USD", "GBP/USD"))
        symbol = "GC=F" if "GOLD" in opt else "SI=F" if "SILVER" in opt else "EURUSD=X" if "EUR" in opt else "GBPUSD=X"
    elif "ग्लोबल" in market_cat:
        symbol = "^IXIC" # Nasdaq
    else:
        symbol = "BTC-USD"

with col3:
    timeframe = st.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3 = st.tabs(["📊 लाइव चार्ट & कंट्रोल", "🎯 ऑप्शन चेन", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: कंट्रोल वाला चार्ट
# ==========================================
with tab1:
    if st.button("चार्ट अपडेट करें 🔄"):
        with st.spinner('प्रोसेसिंग...'):
            try:
                p, i = ("1y", "1d")
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"

                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty: st.error("डेटा नहीं मिला")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    curr = df.iloc[-1]
                    price = float(curr['Close'])

                    # सिग्नल
                    action = "WAIT"
                    color = "blue"
                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY 🟢"
                        color = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL 🔴"
                        color = "red"

                    st.markdown(f"""
                    <div style="padding:10px; border:2px solid {color}; border-radius:10px; text-align:center;">
                        <h2 style="color:{color}; margin:0;">{action}</h2>
                        <h3>₹{price:.2f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- डायनामिक चार्ट ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])

                    # 1. यूजर की पसंद (Candle या Line)
                    if chart_type == "Candlestick":
                        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                    else:
                        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='blue'), name="Line"), row=1, col=1)

                    # 2. इंडिकेटर (अगर यूजर ने ON किया है)
                    if show_ema:
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)

                    # 3. वॉल्यूम (अगर यूजर ने ON किया है)
                    if show_vol:
                        colors = ['red' if c < o else 'green' for c, o in zip(df['Close'], df['Open'])]
                        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

                    # --- थीम अप्लाई करना ---
                    bg_color = "white" if "Light" in theme_choice else "#131722"
                    
                    fig.update_layout(
                        template=chart_template, # Light/Dark यहाँ से कंट्रोल होगा
                        paper_bgcolor=bg_color,
                        plot_bgcolor=bg_color,
                        height=600,
                        xaxis_rangeslider_visible=False,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(str(e))

# ==========================================
# TAB 2: ऑप्शन चेन (फिक्स्ड)
# ==========================================
with tab2:
    st.header("🎯 स्मार्ट ऑप्शन एंट्री")
    if st.button("एनालिसिस करें 🎲"):
        try:
            df = yf.Ticker(symbol).history(period="5d", interval="5m")
            if df.empty: st.error("No Data")
            else:
                spot = df['Close'].iloc[-1]
                gap = 100 if "BANK" in symbol else 50
                atm = round(spot / gap) * gap
                
                # Trend
                last = df.iloc[-1]
                trend = "UP" if last['Close'] > df['Open'].iloc[-1] else "DOWN"
                
                type_ = "CE" if trend == "UP" else "PE"
                col = "green" if trend == "UP" else "red"
                
                st.markdown(f"""
                <div style="padding:15px; border:2px solid {col}; border-radius:10px; text-align:center;">
                    <h3>{type_} Buying Opportunity</h3>
                    <h1>Strike: {atm}</h1>
                    <p>Price Action: {trend}</p>
                </div>
                """, unsafe_allow_html=True)
                
        except: st.error("Error calculating options")

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
        except: st.error("AI Busy")
