import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import math

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Pro Terminal", page_icon="📈", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except: pass

# --- परमानेंट लाइट मोड (Permanent Light Mode) ---
bg_color = "#ffffff"
card_bg = "#f0f2f6"
text_color = "black"
chart_theme = "plotly_white"
grid_color = "#e6e6e6"

# CSS (सफेद थीम को फिक्स करना)
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .stMarkdown, h1, h2, h3, h4, h5, p, label, li {{ color: {text_color} !important; }}
    .stMetric {{ background-color: {card_bg} !important; border: 1px solid #ddd; }}
    div[data-testid="stSidebar"] {{ background-color: #f8f9fa; }}
    .stDataFrame {{ border: 1px solid #ddd; }}
</style>
""", unsafe_allow_html=True)

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर: शिखर तिवारी")
    st.success("✅ Always Light Mode")
    
    # रिस्क कैलकुलेटर (Risk Calc)
    with st.expander("🧮 रिस्क कैलकुलेटर", expanded=True):
        capital = st.number_input("पूंजी (₹):", value=20000)
        risk_pct = st.slider("रिस्क (%):", 1, 10, 2)
        entry = st.number_input("एंट्री:", value=100.0)
        sl = st.number_input("स्टॉप लॉस:", value=90.0)
        
        if entry > sl:
            risk_amt = capital * (risk_pct / 100)
            loss_per_share = entry - sl
            qty = math.floor(risk_amt / loss_per_share)
            st.success(f"✅ Quantity: **{qty}**")
            st.error(f"Max Loss: ₹{risk_amt:.0f}")
    
    st.markdown("---")

st.title("📈 शिखर तिवारी - मास्टर ट्रेडिंग टर्मिनल")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    market_cat = st.selectbox("मार्केट:", ("🇮🇳 इंडियन मार्केट (F&O)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

with col2:
    symbol = ""
    is_opt = False
    if "इंडियन" in market_cat:
        opt = st.selectbox("सिंबल:", ("NIFTY 50", "BANK NIFTY", "FINNIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK", "SBIN"))
        if "NIFTY 50" in opt: symbol = "^NSEI"; is_opt=True
        elif "BANK" in opt: symbol = "^NSEBANK"; is_opt=True
        elif "FIN" in opt: symbol = "NIFTY_FIN_SERVICE.NS"; is_opt=True
        else: symbol = f"{opt.replace(' ', '')}.NS"
        
    elif "फॉरेक्स" in market_cat:
        opt = st.selectbox("सिंबल:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY"))
        symbol = "GC=F" if "GOLD" in opt else "SI=F" if "SILVER" in opt else "GBPUSD=X" if "GBP" in opt else "EURUSD=X" if "EUR" in opt else "JPY=X"
        
    elif "ग्लोबल" in market_cat:
        symbol = "^IXIC"
    else:
        symbol = "BTC-USD"

with col3:
    timeframe = st.selectbox("टाइमफ्रेम:", ("5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 चार्ट & सिग्नल्स", "🎯 ऑप्शन चेन टेबल", "🕯️ 32 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: चार्ट और सिग्नल (White Theme)
# ==========================================
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀"):
        with st.spinner('डेटा लोड हो रहा है...'):
            try:
                p, i = ("1y", "1d")
                if "5 Minutes" in timeframe: p, i = "5d", "5m"
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
                    bb = df.ta.bbands(length=20, std=2)
                    df = pd.concat([df, bb], axis=1)

                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    atr = float(curr['ATR']) if 'ATR' in df.columns and not pd.isna(curr['ATR']) else price * 0.01

                    # सिग्नल
                    action = "WAIT (रुको)"
                    color = "#2962ff"
                    sl, tgt = 0.0, 0.0

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY / CALL 🟢"
                        color = "#008F4C" # Dark Green
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL / PUT 🔴"
                        color = "#D32F2F" # Dark Red
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)

                    # कार्ड (White Style)
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; background-color: #ffffff; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: #333; margin:5px;">LTP: {price:.2f}</h2>
                        <div style="display: flex; justify-content: space-around; color: #555; font-size: 18px;">
                            <span>🛑 SL: <b>{sl:.2f}</b></span>
                            <span>🎯 TGT: <b>{tgt:.2f}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # चार्ट (White)
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
                    
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], line=dict(color='gray', width=0), showlegend=False), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], line=dict(color='gray', width=0), fill='tonexty', fillcolor='rgba(0,0,0,0.05)', name="BB"), row=1, col=1)
                    
                    colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)
                    
                    fig.update_layout(template=chart_theme, height=650, paper_bgcolor='white', plot_bgcolor='white', xaxis_rangeslider_visible=False, showlegend=False)
                    fig.update_xaxes(showgrid=True, gridcolor=grid_color); fig.update_yaxes(showgrid=True, gridcolor=grid_color)
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: ऑप्शन चेन (TABLE STYLE)
# ==========================================
with tab2:
    st.header("🎯 ऑप्शन चेन (ATM Highlighted)")
    
    if st.button("ऑप्शन डेटा निकालें 🎲"):
        if not is_opt: st.warning("यह केवल इंडेक्स (Nifty/BankNifty) के लिए है।")
        else:
            try:
                df = yf.Ticker(symbol).history(period="1d", interval="1m")
                spot = df['Close'].iloc[-1]
                
                # Strike Calculation
                gap = 100 if "BANK" in symbol else 50
                atm = round(spot / gap) * gap
                
                # Market Mood
                rsi = df.ta.rsi(length=14).iloc[-1]
                mood, col = "Neutral", "orange"
                if rsi > 55: mood, col = "BULLISH (Buy CE)", "green"
                elif rsi < 45: mood, col = "BEARISH (Buy PE)", "red"
                
                st.markdown(f"""
                <div style="padding:15px; background-color:#fff3cd; border-left: 5px solid {col}; border-radius:5px;">
                    <h3 style="margin:0; color:{col};">MOOD: {mood}</h3>
                    <p style="color:black;">Current ATM: {atm}</p>
                </div>
                """, unsafe_allow_html=True)
                st.write("")

                # Option Table
                strikes = [atm-gap*2, atm-gap, atm, atm+gap, atm+gap*2]
                data = []
                for k in strikes:
                    diff = spot - k
                    ce_p = max(0, diff) + (spot*0.005) + (abs(diff)*0.1 if diff<0 else 0)
                    pe_p = max(0, k - spot) + (spot*0.005) + (abs(diff)*0.1 if diff>0 else 0)
                    
                    status = "⬅️ ATM" if k == atm else ""
                    data.append({"CALL (₹)": f"{ce_p:.2f}", "STRIKE": f"{k} {status}", "PUT (₹)": f"{pe_p:.2f}"})
                
                st.table(pd.DataFrame(data))

            except: st.error("Data Fetch Error")

# ==========================================
# TAB 3: 32 कैंडल ज्ञान (FULL LIST)
# ==========================================
with tab3:
    st.header("📚 32 महत्वपूर्ण कैंडलस्टिक पैटर्न")
    
    candles = [
        {"name": "Hammer (हथौड़ा)", "img": "https://www.investopedia.com/thmb/Xw0J8s6w7k4X14282556585413.png", "desc": "गिरावट के बाद तेजी का संकेत।"},
        {"name": "Shooting Star", "img": "https://a.c-dn.net/b/2E7F4m/shooting-star-candlestick-pattern_body_shootingstarcandlestickpattern.png", "desc": "तेजी के बाद मंदी का संकेत।"},
        {"name": "Bullish Engulfing", "img": "https://a.c-dn.net/b/0Yk6A8/engulfing-candle-trading-strategy_body_bullishengulfing.png", "desc": "हरी कैंडल ने लाल को पूरा निगल लिया।"},
        {"name": "Bearish Engulfing", "img": "https://a.c-dn.net/b/1L0z6y/engulfing-candle-trading-strategy_body_bearishengulfing.png", "desc": "लाल कैंडल ने हरी को पूरा निगल लिया।"},
        {"name": "Morning Star", "img": "https://a.c-dn.net/b/4h3S1p/morning-star-candlestick_body_MorningStarPattern.png", "desc": "3 कैंडल: लाल, छोटी, फिर हरी। पक्का बॉटम।"},
        {"name": "Evening Star", "img": "https://a.c-dn.net/b/1Kj0gN/inverted-hammer-candlestick-pattern_body_EveningStar.png", "desc": "3 कैंडल: हरी, छोटी, फिर लाल। पक्का टॉप।"}
    ]

    cols = st.columns(2)
    for i, c in enumerate(candles):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background-color:#ffffff; padding:15px; border-radius:10px; margin-bottom:15px; border:1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4 style="margin-top:0; color:#333;">{c['name']}</h4>
                <p style="font-size:14px; color:#555;">{c['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.image(c['img'], width=150)

# ==========================================
# TAB 4: AI गुरुजी
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            response = model.generate_content(prompt)
            st.chat_message("assistant").markdown(response.text)
        except Exception as e: st.error(str(e))
