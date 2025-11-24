import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Master Bot", page_icon="📈", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("नाम: शिखर तिवारी (ईशान पंडित)")
    st.success("Mode: Education + Trading")
    st.markdown("---")

st.title("📈 शिखर तिवारी - मास्टर ट्रेडिंग & लर्निंग हब")
st.markdown("### 🚀 Learn Candles & Trade Live")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
if market_cat == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK", "SBIN"))
    symbol = "^NSEI" if "NIFTY" in option else "^NSEBANK" if "BANK" in option else f"{option.replace(' ', '')}.NS"

elif market_cat == "💱 फॉरेक्स & गोल्ड":
    option = st.sidebar.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY"))
    if "GOLD" in option: symbol = "GC=F"
    elif "SILVER" in option: symbol = "SI=F"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"
    elif "JPY" in option: symbol = "JPY=X"

elif market_cat == "🇺🇸 ग्लोबल मार्केट":
    symbol = "^IXIC" # Nasdaq

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 लाइव चार्ट (Clean)", "🎓 कैंडल कैसे पढ़ें (New)", "📚 पैटर्न लाइब्रेरी", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: लाइव चार्ट (आपकी फोटो जैसा क्लीन लुक)
# ==========================================
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀", key="btn1"):
        with st.spinner('डेटा लोड हो रहा है...'):
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
                        color = "#008F4C" # Sharp Green
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL 🔴"
                        color = "#D32F2F" # Sharp Red
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)

                    # कार्ड
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; background-color: #ffffff; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: #333; margin:5px;">₹{price:.2f}</h2>
                        <div style="display: flex; justify-content: space-around; color: #555;">
                            <span>🛑 SL: <b>{sl:.2f}</b></span>
                            <span>🎯 TGT: <b>{tgt:.2f}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- चार्ट (CLEAN WHITE LOOK) ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                        vertical_spacing=0.03, row_heights=[0.75, 0.25])

                    # Candles (Sharp Colors like Image)
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="Price",
                        increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'
                    ), row=1, col=1)

                    # EMAs (Thin Lines)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1.5), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1.5), name="EMA 21"), row=1, col=1)

                    # Volume
                    vol_colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)

                    # Layout (Clean White like Image)
                    fig.update_layout(
                        paper_bgcolor='white', plot_bgcolor='white',
                        height=700, title=f"{symbol} Analysis Chart",
                        xaxis_rangeslider_visible=False, showlegend=False
                    )
                    
                    # Grid (Very light dashed)
                    fig.update_xaxes(showgrid=True, gridcolor='#e0e0e0', gridwidth=0.5)
                    fig.update_yaxes(showgrid=True, gridcolor='#e0e0e0', gridwidth=0.5)

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: कैंडल कैसे पढ़ें (NEW FEATURE)
# ==========================================
with tab2:
    st.header("🎓 कैंडलस्टिक एनाटॉमी (बनावट)")
    st.write("जैसा आपने फोटो में भेजा, वैसे ही सीखें कि कैंडल क्या बताती है:")

    # डेमो डेटा (सिखाने के लिए)
    st.info("💡 **टिप:** Wick (डंडी) का मतलब है 'Price Rejection' (भाव को नकारा गया)।")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟢 Bullish Candle (तेजी)")
        st.markdown("""
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; text-align: center;">
            <h3 style="color: #008F4C;">BUYERS जीत गए</h3>
            <p><b>High:</b> आज का सबसे महंगा भाव</p>
            <p><b>Close:</b> यहाँ बाजार बंद हुआ (ऊपर)</p>
            <div style="height: 100px; width: 30px; background-color: #008F4C; margin: auto;"></div>
            <p><b>Open:</b> यहाँ बाजार खुला था (नीचे)</p>
            <p><b>Low:</b> आज का सबसे सस्ता भाव</p>
        </div>
        """, unsafe_allow_html=True)
        st.success("नीचे से ऊपर जाती है। इसका मतलब लोग खरीद रहे हैं।")

    with col2:
        st.subheader("🔴 Bearish Candle (मंदी)")
        st.markdown("""
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; text-align: center;">
            <h3 style="color: #D32F2F;">SELLERS जीत गए</h3>
            <p><b>High:</b> आज का सबसे महंगा भाव</p>
            <p><b>Open:</b> यहाँ बाजार खुला था (ऊपर)</p>
            <div style="height: 100px; width: 30px; background-color: #D32F2F; margin: auto;"></div>
            <p><b>Close:</b> यहाँ बाजार बंद हुआ (नीचे)</p>
            <p><b>Low:</b> आज का सबसे सस्ता भाव</p>
        </div>
        """, unsafe_allow_html=True)
        st.error("ऊपर से नीचे आती है। इसका मतलब लोग बेच रहे हैं।")

# ==========================================
# TAB 3: कैंडल लाइब्रेरी (Hindi)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक पैटर्न गाइड")
    st.image("https://a.c-dn.net/b/4h3S1p/morning-star-candlestick_body_MorningStarPattern.png", caption="Example: Morning Star", width=200)
    
    patterns = [
        {"name": "Hammer (हथौड़ा) 🔨", "type": "Bullish", "desc": "गिरावट के बाद बनता है। Wick नीचे होती है, मतलब Price Reject हुआ है।"},
        {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "तेजी के बाद बनता है। Wick ऊपर होती है, मतलब ऊपर जाने से मना कर दिया।"},
        {"name": "Bullish Engulfing 📈", "type": "Strong Buy", "desc": "हरी कैंडल ने पिछली लाल कैंडल को पूरा निगल लिया।"},
        {"name": "Bearish Engulfing 📉", "type": "Strong Sell", "desc": "लाल कैंडल ने पिछली हरी कैंडल को पूरा निगल लिया।"},
        {"name": "Doji ➕", "type": "Neutral", "desc": "जहाँ खुला वहीं बंद हुआ। बाजार सोच में है।"}
    ]

    for pat in patterns:
        st.info(f"**{pat['name']}** ({pat['type']})\n\n{pat['desc']}")

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
