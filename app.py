import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Trading Pro", page_icon="🕯️", layout="wide")

# ==========================================
# 🔑 API KEY
# ==========================================
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

# --- AI सेटअप ---
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash") # New fast model
except:
    pass

# --- कैंडलस्टिक पहचानने का फंक्शन (Hindi Logic) ---
def identify_candle(open, high, low, close):
    body = abs(close - open)
    upper_wick = high - max(close, open)
    lower_wick = min(close, open) - low
    total_range = high - low
    
    # 1. Hammer (हथौड़ा) - तेजी
    if lower_wick > 2 * body and upper_wick < body * 0.5:
        return "Hammer (हथौड़ा) 🔨 - मार्केट ऊपर जा सकता है 🟢"
    
    # 2. Shooting Star (टूटता तारा) - मंदी
    elif upper_wick > 2 * body and lower_wick < body * 0.5:
        return "Shooting Star (टूटता तारा) 🌠 - मार्केट नीचे गिर सकता है 🔴"
    
    # 3. Doji (डोजी) - कन्फ्यूजन
    elif body <= total_range * 0.1:
        return "Doji (डोजी) ➕ - मार्केट कन्फ्यूज है (इंतजार करें) ⏸️"
    
    # 4. Marubozu Green (बड़ी हरी कैंडल)
    elif body > total_range * 0.8 and close > open:
        return "Green Marubozu (मजबूत तेजी) 🟩 - बायर्स हावी हैं"
    
    # 5. Marubozu Red (बड़ी लाल कैंडल)
    elif body > total_range * 0.8 and close < open:
        return "Red Marubozu (मजबूत मंदी) 🟥 - सेलर्स हावी हैं"
    
    else:
        return "Normal Candle (सामान्य) 🕯️"

# --- साइडबार ---
with st.sidebar:
    st.header("👤 यूजर प्रोफाइल")
    st.info("**Trader:** शिखर तिवारी")
    st.warning("📞 93360-92738")
    st.success("📧 shikhartiwari9336@gmail.com")
    st.markdown("---")

st.title("🕯️ शिखर तिवारी - प्रो चार्ट & कैंडलस्टिक पैटर्न")
st.markdown("### 🚀 Forex, Gold, Stocks & Hindi Analysis")

# --- मार्केट सिलेक्शन ---
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("मार्केट:", ("💱 फॉरेक्स & गोल्ड", "🇮🇳 इंडियन मार्केट", "🇺🇸 ग्लोबल इंडेक्स", "₿ क्रिप्टो"))

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
    if "NIFTY" in option: symbol = "^NSEI" if "50" in option else "^NSEBANK"
    else: symbol = f"{option.replace(' ', '')}.NS"

elif market_cat == "🇺🇸 ग्लोबल इंडेक्स":
    option = st.sidebar.selectbox("इंडेक्स:", ("NASDAQ", "S&P 500", "TESLA", "APPLE", "GOOGLE"))
    symbol = "^IXIC" if "NASDAQ" in option else "TSLA" if "TESLA" in option else "AAPL" if "APPLE" in option else "^GSPC"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3 = st.tabs(["📊 लाइव चार्ट (Full)", "📖 कैंडलस्टिक ज्ञान (Hindi)", "🤖 AI गुरुजी"])

# TAB 1: चार्ट और पैटर्न
with tab1:
    if st.button(f"{symbol} चार्ट देखें 🚀"):
        with st.spinner('डेटा लोड हो रहा है...'):
            try:
                p, i = ("1y", "1d")
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"

                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    
                    # --- कैंडल पहचानना ---
                    curr = df.iloc[-1]
                    last_candle_name = identify_candle(curr['Open'], curr['High'], curr['Low'], curr['Close'])
                    price = float(curr['Close'])
                    
                    # सिग्नल
                    sig = "WAIT"
                    col = "blue"
                    if curr['EMA_9'] > curr['EMA_21']:
                        sig = "BUY 🟢"
                        col = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        sig = "SELL 🔴"
                        col = "red"

                    # --- नोटिफिकेशन और कैंडल नाम ---
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {col}; border-radius: 10px; background-color: #f8f9fa;">
                        <h2 style="color: {col}; text-align: center; margin:0;">SIGNAL: {sig}</h2>
                        <h3 style="text-align: center;">Price: {price:.2f}</h3>
                        <hr>
                        <h4 style="text-align: center; color: #333;">🕯️ अभी बनी कैंडल: <b>{last_candle_name}</b></h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")

                    # --- फुल स्क्रीन चार्ट ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red")
                    fig.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green")

                    # चार्ट की हाइट बढ़ाई गई (ताकि फुल स्क्रीन जैसा लगे)
                    fig.update_layout(height=700, xaxis_rangeslider_visible=False, title=f"{symbol} Full Chart ({timeframe})")
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("💡 चार्ट को पूरा खोलने के लिए चार्ट के कोने में बने 'Full Screen' आइकन पर क्लिक करें।")

            except Exception as e: st.error(f"Error: {e}")

# TAB 2: कैंडलस्टिक ज्ञान (HINDI GUIDE)
with tab2:
    st.header("📖 कैंडलस्टिक पैटर्न गाइड (हिंदी में)")
    st.markdown("यहाँ देखिये कि कौन सी कैंडल क्या इशारा करती है:")
    
    data = {
        "कैंडल का नाम (Name)": ["Hammer (हथौड़ा) 🔨", "Shooting Star 🌠", "Bullish Engulfing 📈", "Bearish Engulfing 📉", "Doji (डोजी) ➕", "Marubozu Green 🟩", "Marubozu Red 🟥"],
        "क्या होगा? (Signal)": ["मार्केट ऊपर जाएगा (Bullish)", "मार्केट नीचे गिरेगा (Bearish)", "बहुत तेज ऊपर जाएगा", "बहुत तेज नीचे गिरेगा", "मार्केट कन्फ्यूज है (रुकें)", "फुल पावर तेजी", "फुल पावर मंदी"],
        "कैसे पहचानें?": ["नीचे की डंडी (Wick) लंबी होती है", "ऊपर की डंडी (Wick) लंबी होती है", "हरी कैंडल ने लाल को पूरा खा लिया", "लाल कैंडल ने हरी को पूरा खा लिया", "बॉडी बहुत छोटी या गायब होती है", "सिर्फ बॉडी होती है, डंडी नहीं", "सिर्फ बॉडी होती है, डंडी नहीं"]
    }
    st.table(pd.DataFrame(data))
    
    st.markdown("---")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Candlestick_Pattern.png/800px-Candlestick_Pattern.png", caption="Candlestick Cheat Sheet")

# TAB 3: AI चैट
with tab2: # Note: Using tab2 variable for AI as requested structure
    pass 
with tab3:
    st.header("🤖 Shikhar's AI Expert")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).markdown(m["content"])
    
    if prompt := st.chat_input("सवाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            with st.chat_message("assistant"):
                with st.spinner("AI सोच रहा है..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e: st.error(f"Error: {e}")
