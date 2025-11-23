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

# --- कैंडलस्टिक पहचान फंक्शन ---
def recognize_candle(df):
    current = df.iloc[-1]
    prev = df.iloc[-2]
    
    body = abs(current['Close'] - current['Open'])
    upper_wick = current['High'] - max(current['Close'], current['Open'])
    lower_wick = min(current['Close'], current['Open']) - current['Low']
    avg_body = abs(df['Open'] - df['Close']).mean()
    
    pattern = "Normal Candle (सामान्य)"
    
    # 1. Marubozu
    if body > avg_body * 2 and lower_wick < body*0.1 and upper_wick < body*0.1:
        if current['Close'] > current['Open']: return "Green Marubozu (मजबूत तेजी) 🟩"
        else: return "Red Marubozu (मजबूत मंदी) 🟥"
    
    # 2. Hammer
    elif lower_wick > body * 2 and upper_wick < body * 0.5:
        return "Hammer (हथौड़ा) 🔨 - पलटने का संकेत"

    # 3. Shooting Star
    elif upper_wick > body * 2 and lower_wick < body * 0.5:
        return "Shooting Star 🌠 - गिरावट का संकेत"

    # 4. Doji
    elif body < avg_body * 0.1:
        return "Doji (कन्फ्यूजन) ➕ - ट्रेंड बदल सकता है"

    # 5. Engulfing
    elif current['Close'] > current['Open'] and prev['Close'] < prev['Open']:
        if current['Close'] > prev['Open'] and current['Open'] < prev['Close']:
            return "Bullish Engulfing (बड़ी तेजी) 📈"
    elif current['Close'] < current['Open'] and prev['Close'] > prev['Open']:
        if current['Close'] < prev['Open'] and current['Open'] > prev['Close']:
            return "Bearish Engulfing (बड़ी मंदी) 📉"

    return pattern

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
    symbol = "^IXIC" if "NASDAQ" in option else "TSLA" if "TESLA" in option else "AAPL" if "APPLE" in option else "^GSPC"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["⚡ सिग्नल्स (Live)", "📊 चार्ट (History)", "📖 कैंडल लाइब्रेरी", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: सिग्नल्स और लेवल्स
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
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    df['ATR'] = df.ta.atr(length=14)
                    
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    
                    pattern_name = recognize_candle(df)
                    atr = float(curr['ATR']) if 'ATR' in df.columns and not pd.isna(curr['ATR']) else price * 0.01

                    action = "WAIT (इंतजार करें)"
                    color = "blue"
                    sl, tgt = 0.0, 0.0
                    reason = "मार्केट साइडवेज है"

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY (खरीदें) 🟢"
                        color = "green"
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                        reason = "EMA Uptrend + " + pattern_name
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL (बेचें) 🔴"
                        color = "red"
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)
                        reason = "EMA Downtrend + " + pattern_name

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
                        c1.metric("🛑 STOP LOSS", f"{sl:.2f}")
                        c2.metric("🎯 TARGET", f"{tgt:.2f}")
                        c3.metric("📈 RSI", f"{curr['RSI']:.2f}")
                        st.info(f"💡 **सलाह:** {reason}")
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# TAB 2: चार्ट (Buy/Sell तीरों के साथ)
# ==========================================
with tab2:
    if st.button("चार्ट खोलें 📉", key="btn2"):
        try:
            p, i = ("1mo", "1h") if "1 Hour" in timeframe else ("1y", "1d")
            df = yf.Ticker(symbol).history(period=p, interval=i)
            df['EMA_9'], df['EMA_21'] = df.ta.ema(length=9), df.ta.ema(length=21)
            
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
            
            if buy_sig:
                bd, bp = zip(*buy_sig)
                fig.add_trace(go.Scatter(x=bd, y=bp, mode='markers', marker=dict(symbol='triangle-up', size=15, color='green'), name='BUY'), row=1, col=1)
            if sell_sig:
                sd, sp = zip(*sell_sig)
                fig.add_trace(go.Scatter(x=sd, y=sp, mode='markers', marker=dict(symbol='triangle-down', size=15, color='red'), name='SELL'), row=1, col=1)

            fig.update_layout(height=700, title=f"{symbol} History Chart")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Chart Error: {e}")

# ==========================================
# TAB 3: कैंडलस्टिक लाइब्रेरी (हिंदी में)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक पैटर्न लाइब्रेरी")
    candles_data = [
        {"नाम": "Hammer (हथौड़ा) 🔨", "संकेत": "Bullish", "मतलब": "गिरावट खत्म, अब बाजार ऊपर जाएगा।"},
        {"नाम": "Shooting Star 🌠", "संकेत": "Bearish", "मतलब": "तेजी खत्म, अब बाजार गिर सकता है।"},
        {"नाम": "Bullish Engulfing 📈", "संकेत": "Strong Buy", "मतलब": "बड़ी हरी कैंडल ने पिछली लाल को खा लिया।"},
        {"नाम": "Bearish Engulfing 📉", "संकेत": "Strong Sell", "मतलब": "बड़ी लाल कैंडल ने पिछली हरी को खा लिया।"},
        {"नाम": "Doji (डोजी) ➕", "संकेत": "Indecision", "मतलब": "बाजार कन्फ्यूज है, अभी ट्रेड न लें।"},
        {"नाम": "Marubozu Green 🟩", "संकेत": "Super Bullish", "मतलब": "सिर्फ खरीदारी हो रही है, बहुत तेजी।"},
        {"नाम": "Marubozu Red 🟥", "संकेत": "Super Bearish", "मतलब": "सिर्फ बिकवाली हो रही है, भारी गिरावट।"}
    ]
    st.table(pd.DataFrame(candles_data))
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Candlestick_Pattern.png/800px-Candlestick_Pattern.png", caption="Patterns")

# ==========================================
# TAB 4: AI
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).markdown(m["content"])
    
    if prompt := st.chat_input("सवाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except Exception as e: st.error(str(e))
