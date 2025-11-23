import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Pro Trader", page_icon="🕯️", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- कैंडलस्टिक पहचान फंक्शन (Logic for Patterns) ---
def recognize_candle(df):
    current = df.iloc[-1]
    prev = df.iloc[-2]
    
    body = abs(current['Close'] - current['Open'])
    upper_wick = current['High'] - max(current['Close'], current['Open'])
    lower_wick = min(current['Close'], current['Open']) - current['Low']
    avg_body = abs(df['Open'] - df['Close']).mean()
    
    pattern = "Normal Candle (सामान्य)"
    signal = "Neutral"

    # 1. Marubozu (मजबूत)
    if body > avg_body * 2 and lower_wick < body*0.1 and upper_wick < body*0.1:
        if current['Close'] > current['Open']:
            pattern = "Green Marubozu (मजबूत तेजी) 🟩"
            signal = "Bullish"
        else:
            pattern = "Red Marubozu (मजबूत मंदी) 🟥"
            signal = "Bearish"
    
    # 2. Hammer (हथौड़ा)
    elif lower_wick > body * 2 and upper_wick < body * 0.5:
        pattern = "Hammer (हथौड़ा) 🔨 - पलटने का संकेत"
        signal = "Bullish Reversal"

    # 3. Shooting Star (टूटता तारा)
    elif upper_wick > body * 2 and lower_wick < body * 0.5:
        pattern = "Shooting Star 🌠 - गिरावट का संकेत"
        signal = "Bearish Reversal"

    # 4. Doji (डोजी)
    elif body < avg_body * 0.1:
        pattern = "Doji (कन्फ्यूजन) ➕ - ट्रेंड बदल सकता है"
        signal = "Indecision"

    # 5. Bullish Engulfing (निगलना)
    elif current['Close'] > current['Open'] and prev['Close'] < prev['Open']:
        if current['Close'] > prev['Open'] and current['Open'] < prev['Close']:
            pattern = "Bullish Engulfing (बड़ी तेजी) 📈"
            signal = "Strong Bullish"

    # 6. Bearish Engulfing
    elif current['Close'] < current['Open'] and prev['Close'] > prev['Open']:
        if current['Close'] < prev['Open'] and current['Open'] > prev['Close']:
            pattern = "Bearish Engulfing (बड़ी मंदी) 📉"
            signal = "Strong Bearish"

    return pattern, signal

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("नाम: शिखर तिवारी (ईशान पंडित)")
    st.warning("📞 93360-92738")
    st.success("📧 shikhartiwari9336@gmail.com")
    st.markdown("---")

st.title("🕯️ शिखर तिवारी - मास्टर ट्रेडिंग बॉट")
st.markdown("### 🚀 Forex, Gold, Stocks & All Candle Patterns")

# --- मार्केट सिलेक्शन ---
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("💱 फॉरेक्स & गोल्ड", "🇮🇳 इंडियन मार्केट", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
if market_cat == "💱 फॉरेक्स & गोल्ड":
    option = st.sidebar.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY"))
    if "GOLD" in option: symbol = "GC=F"
    elif "SILVER" in option: symbol = "SI=F"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"
    elif "JPY" in option: symbol = "JPY=X"

elif market_cat == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK"))
    symbol = "^NSEI" if "NIFTY" in option else "^NSEBANK" if "BANK" in option else f"{option.replace(' ', '')}.NS"

elif market_cat == "🇺🇸 ग्लोबल मार्केट":
    option = st.sidebar.selectbox("इंडेक्स:", ("NASDAQ", "S&P 500", "TESLA", "APPLE", "GOOGLE"))
    symbol = "^IXIC" if "NASDAQ" in option else "TSLA" if "TESLA" in option else "AAPL"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["⚡ सिग्नल्स (Live)", "📊 चार्ट (History)", "📖 कैंडल लाइब्रेरी (46+)", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: सिग्नल्स और लेवल्स (वो कार्ड वापस आ गया)
# ==========================================
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀", key="btn1"):
        with st.spinner('कैलकुलेशन चल रही है...'):
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
                    
                    # कैंडल पहचानना
                    pattern_name, pattern_signal = recognize_candle(df)
                    
                    # ATR Logic
                    atr = float(curr['ATR']) if 'ATR' in df.columns and not pd.isna(curr['ATR']) else price * 0.01

                    # सिग्नल लॉजिक
                    action = "WAIT (इंतजार करें)"
                    color = "blue"
                    sl, tgt = 0.0, 0.0
                    reason = "मार्केट साइडवेज है"

                    # BUY
                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY (खरीदें) 🟢"
                        color = "green"
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                        reason = "EMA Uptrend + " + pattern_name
                    # SELL
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL (बेचें) 🔴"
                        color = "red"
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)
                        reason = "EMA Downtrend + " + pattern_name

                    # --- कार्ड डिस्प्ले ---
                    st.markdown(f"""
                    <div style="padding: 20px; border: 3px solid {color}; border-radius: 15px; background-color: {'#e8f5e9' if color=='green' else '#ffebee' if color=='red' else '#f3f4f6'};">
                        <h1 style="color: {color}; text-align: center; margin:0;">{action}</h1>
                        <h2 style="text-align: center;">Price: {price:.2f}</h2>
                        <hr>
                        <h3 style="text-align: center; color: #333;">🕯️ {pattern_name}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if color != "blue":
                        c1, c2, c3 = st.columns(3)
                        c1.metric("🛑 STOP LOSS", f"{sl:.2f}", delta_color="inverse")
                        c2.metric("🎯 TARGET", f"{tgt:.2f}")
                        c3.metric("📈 RSI Strength", f"{curr['RSI']:.2f}")
                        st.info(f"💡 **सलाह:** {reason}")

# ==========================================
# TAB 2: चार्ट (Buy/Sell तीरों के साथ)
# ==========================================
with tab2:
    if st.button("चार्ट खोलें 📉", key="btn2"):
        p, i = ("1mo", "1h") if "1 Hour" in timeframe else ("1y", "1d")
        df = yf.Ticker(symbol).history(period=p, interval=i)
        df['EMA_9'], df['EMA_21'] = df.ta.ema(length=9), df.ta.ema(length=21)
        
        # सिग्नल ढूंढना (तीर के लिए)
        buy_sig, sell_sig = [], []
        for j in range(1, len(df)):
            if df['EMA_9'].iloc[j-1] < df['EMA_21'].iloc[j-1] and df['EMA_9'].iloc[j] > df['EMA_21'].iloc[j]:
                buy_sig.append((df.index[j], df['Low'].iloc[j]))
            elif df['EMA_9'].iloc[j-1] > df['EMA_21'].iloc[j-1] and df['EMA_9'].iloc[j] < df['EMA_21'].iloc[j]:
                sell_sig.append((df.index[j], df['High'].iloc[j]))

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)
        
        # तीरों को जोड़ना
        if buy_sig:
            bd, bp = zip(*buy_sig)
            fig.add_trace(go.Scatter(x=bd, y=bp, mode='markers', marker=dict(symbol='triangle-up', size=15, color='green'), name='BUY Point'), row=1, col=1)
        if sell_sig:
            sd, sp = zip(*sell_sig)
            fig.add_trace(go.Scatter(x=sd, y=sp, mode='markers', marker=dict(symbol='triangle-down', size=15, color='red'), name='SELL Point'), row=1, col=1)

        fig.update_layout(height=700, title=f"{symbol} History Chart")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("नोट: चार्ट पर ▲ का मतलब 'खरीदने की जगह' और ▼ का मतलब 'बेचने की जगह' थी।")

# ==========================================
# TAB 3: कैंडलस्टिक लाइब्रेरी (हिंदी में)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक पैटर्न लाइब्रेरी (हिंदी में)")
    st.write("यहाँ सभी प्रमुख कैंडल्स की जानकारी दी गई है:")
    
    candles_data = [
        {"नाम": "Hammer (हथौड़ा) 🔨", "संकेत": "Bullish (तेजी)", "मतलब": "गिरावट खत्म, अब बाजार ऊपर जाएगा।"},
        {"नाम": "Shooting Star 🌠", "संकेत": "Bearish (मंदी)", "मतलब": "तेजी खत्म, अब बाजार गिर सकता है।"},
        {"नाम": "Bullish Engulfing 📈", "संकेत": "Strong Buy", "मतलब": "बड़ी हरी कैंडल ने पिछली लाल को खा लिया।"},
        {"नाम": "Bearish Engulfing 📉", "संकेत": "Strong Sell", "मतलब": "बड़ी लाल कैंडल ने पिछली हरी को खा लिया।"},
        {"नाम": "Doji (डोजी) ➕", "संकेत": "Indecision", "मतलब": "बाजार कन्फ्यूज है, अभी ट्रेड न लें।"},
        {"नाम": "Morning Star 🌅", "संकेत": "Reversal (Up)", "मतलब": "रात (मंदी) खत्म, सवेरा (तेजी) शुरू।"},
        {"नाम": "Evening Star 🌃", "संकेत": "Reversal (Down)", "मतलब": "दिन (तेजी) खत्म, रात (मंदी) शुरू।"},
        {"नाम": "Marubozu Green 🟩", "संकेत": "Super Bullish", "मतलब": "सिर्फ खरीदारी हो रही है, बहुत तेजी।"},
        {"नाम": "Marubozu Red 🟥", "संकेत": "Super Bearish", "मतलब": "सिर्फ बिकवाली हो रही है, भारी गिरावट।"},
        {"नाम": "Spinning Top 🌪️", "संकेत": "Neutral", "मतलब": "छोटी बॉडी, दोनों तरफ डंडी। बाजार रुक सकता है।"},
        {"नाम": "Hanging Man 🧘", "संकेत": "Bearish", "मतलब": "ऊपर जाते बाजार में हथौड़ा - खतरा।"},
        {"नाम": "Inverted Hammer 🔨", "संकेत": "Bullish", "मतलब": "नीचे गिरते बाजार में उल्टा हथौड़ा - मौका।"}
    ]
    st.table(pd.DataFrame(candles_data))
    
    st.image("https://zerodha.com/varsity/wp-content/uploads/2015/05/M6-Ch11-Candlestick-Cheat-Sheet.png", caption="All Candlestick Cheat Sheet")
    [Image of forex trading chart]

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
