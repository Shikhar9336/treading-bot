import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज कॉन्फ़िगरेशन (Dark Theme) ---
st.set_page_config(page_title="Shikhar Pro Terminal", page_icon="📈", layout="wide")

# ==========================================
# 🔑 API KEY & AI SETUP
# ==========================================
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- CSS (Design को सुंदर बनाने के लिए) ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #262730; padding: 10px; border-radius: 5px; }
    h1, h2, h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- साइडबार ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4285/4285652.png", width=80)
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("नाम: शिखर तिवारी (ईशान पंडित)")
    st.warning("📞 93360-92738")
    st.success("📧 shikhartiwari9336@gmail.com")
    st.markdown("---")

st.title("📈 शिखर तिवारी - अल्ट्रा प्रो ट्रेडिंग टर्मिनल")
st.markdown("### 🚀 Professional Dark Charts, Volume & Auto-Signals")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

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
    symbol = "^IXIC" if "NASDAQ" in option else "^GSPC" if "S&P" in option else "TSLA" if "TESLA" in option else "AAPL"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3 = st.tabs(["📊 लाइव चार्ट & सिग्नल्स", "📚 कैंडलस्टिक ज्ञान (Images)", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: डार्क चार्ट + सिग्नल्स (आपका मेन काम)
# ==========================================
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀", key="btn1"):
        with st.spinner('डेटा और चार्ट लोड हो रहा है...'):
            try:
                # 1. डेटा डाउनलोड
                p, i = ("1y", "1d")
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"

                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला।")
                else:
                    # 2. इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    df['ATR'] = df.ta.atr(length=14)
                    
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    atr = float(curr['ATR']) if 'ATR' in df.columns and not pd.isna(curr['ATR']) else price * 0.01

                    # 3. सिग्नल लॉजिक
                    action = "WAIT (इंतजार करें)"
                    color = "#2962ff" # Blue
                    sl, tgt = 0.0, 0.0
                    reason = "मार्केट साइडवेज है"

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY (खरीदें) 🟢"
                        color = "#00c853" # Bright Green
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                        reason = "Trend ऊपर है (EMA 9 > 21)"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL (बेचें) 🔴"
                        color = "#ff3d00" # Bright Red
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)
                        reason = "Trend नीचे है (EMA 9 < 21)"

                    # 4. सिग्नल कार्ड (बड़ा वाला)
                    st.markdown(f"""
                    <div style="padding: 20px; border: 2px solid {color}; border-radius: 10px; background-color: #1e1e1e; text-align: center;">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: white; margin:5px;">Price: {price:.2f}</h2>
                        <hr style="border-color: #333;">
                        <div style="display: flex; justify-content: space-around; color: white;">
                            <p>🛑 SL: <b style="color: #ff3d00;">{sl:.2f}</b></p>
                            <p>🎯 TGT: <b style="color: #00c853;">{tgt:.2f}</b></p>
                            <p>📈 RSI: <b>{curr['RSI']:.2f}</b></p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # 5. प्रोफेशनल चार्ट (Volume + Dark Theme)
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                        vertical_spacing=0.03, row_heights=[0.75, 0.25])

                    # Candlestick (TradingView Style Colors)
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="Price",
                        increasing_line_color='#089981', decreasing_line_color='#f23645'
                    ), row=1, col=1)

                    # EMAs
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='#2962ff', width=1), name="EMA 21"), row=1, col=1)

                    # Volume (Colored Bars)
                    vol_colors = ['#f23645' if c < o else '#089981' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)

                    # Dark Mode Layout (TradingView Look)
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="#131722", plot_bgcolor="#131722",
                        height=700, title=f"{symbol} Professional Chart",
                        xaxis_rangeslider_visible=False, showlegend=False
                    )
                    # Grid हटाना (Cleaner Look)
                    fig.update_xaxes(showgrid=False)
                    fig.update_yaxes(showgrid=True, gridcolor='#2a2e39')

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: कैंडलस्टिक ज्ञान (Images + Hindi)
# ==========================================
with tab2:
    st.header("📚 कैंडलस्टिक पैटर्न गाइड")
    st.write("यहाँ कैंडल्स की फोटो और उनके मतलब हिंदी में दिए गए हैं:")

    # डेटाबेस (फोटो लिंक्स के साथ)
    patterns = [
        {
            "name": "Hammer (हथौड़ा) 🔨",
            "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Hammer_candlestick_pattern.svg/1200px-Hammer_candlestick_pattern.svg.png",
            "type": "Bullish (तेजी)",
            "desc": "यह गिरावट के बाद बनता है। इसका मतलब है सेलर्स थक गए हैं और अब मार्केट ऊपर जाएगा। इसे देखकर Buy कर सकते हैं।"
        },
        {
            "name": "Shooting Star 🌠",
            "img": "https://a.c-dn.net/b/2E7F4m/shooting-star-candlestick-pattern_body_shootingstarcandlestickpattern.png",
            "type": "Bearish (मंदी)",
            "desc": "यह तेजी के बाद ऊपर बनता है। इसका मतलब है बायर्स थक गए हैं और अब मार्केट नीचे गिरेगा। इसे देखकर Sell कर सकते हैं।"
        },
        {
            "name": "Bullish Engulfing 📈",
            "img": "https://a.c-dn.net/b/0Yk6A8/engulfing-candle-trading-strategy_body_bullishengulfing.png",
            "type": "Strong Buy",
            "desc": "जब एक छोटी लाल कैंडल को अगली बड़ी हरी कैंडल पूरा ढक ले। यह बहुत मजबूत तेजी का संकेत है।"
        },
        {
            "name": "Bearish Engulfing 📉",
            "img": "https://a.c-dn.net/b/1L0z6y/engulfing-candle-trading-strategy_body_bearishengulfing.png",
            "type": "Strong Sell",
            "desc": "जब एक छोटी हरी कैंडल को अगली बड़ी लाल कैंडल पूरा ढक ले। यह बहुत मजबूत मंदी (गिरावट) का संकेत है।"
        },
        {
            "name": "Doji (डोजी) ➕",
            "img": "https://a.c-dn.net/b/1f20Vj/what-is-a-doji-candle_body_DragonflyDoji.png",
            "type": "Indecision (कन्फ्यूज)",
            "desc": "इसमें बॉडी नहीं होती, सिर्फ लाइन होती है। इसका मतलब है मार्केट कन्फ्यूज है। अभी ट्रेड न लें, अगली कैंडल का इंतजार करें।"
        },
         {
            "name": "Morning Star 🌅",
            "img": "https://a.c-dn.net/b/4h3S1p/morning-star-candlestick_body_MorningStarPattern.png",
            "type": "Trend Reversal (Up)",
            "desc": "यह तीन कैंडल का पैटर्न है। एक लाल, एक छोटी, और फिर एक बड़ी हरी। यह बताता है कि रात (मंदी) खत्म, सवेरा (तेजी) शुरू।"
        }
    ]

    # कार्ड्स दिखाना
    col1, col2 = st.columns(2)
    for i, pat in enumerate(patterns):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
            <div style="border: 1px solid #333; border-radius: 10px; padding: 10px; background-color: #1e1e1e; margin-bottom: 20px;">
                <h3 style="color: white; margin-bottom: 5px;">{pat['name']}</h3>
                <span style="background-color: {'green' if 'Bullish' in pat['type'] or 'Buy' in pat['type'] else 'red' if 'Bearish' in pat['type'] else 'orange'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{pat['type']}</span>
                <p style="color: #ccc; font-size: 14px; margin-top: 10px;">{pat['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.image(pat['img'], width=150)

# ==========================================
# TAB 3: AI
# ==========================================
with tab3:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("मार्केट के बारे में पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
        except Exception as e: st.error(str(e))
