import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

st.set_page_config(page_title="Global Trading Bot", page_icon="🌍", layout="wide")

# ==========================================
# 🔑 API KEY (सीधे कोड में)
# ==========================================
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

# --- AI सेटअप ---
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"AI Error: {e}")

st.title("🌍 AI ग्लोबल ट्रेडिंग डैशबोर्ड")
st.markdown("### इंडियन मार्केट (Stocks) + फॉरेक्स (Forex) + क्रिप्टो")

# ==========================================
# ⚙️ साइडबार सेटिंग्स (MARKET SELECTION)
# ==========================================
st.sidebar.header("⚙️ मार्केट चुनें")

# 1. मार्केट टाइप चुनें
market_type = st.sidebar.radio("मार्केट कैटेगरी:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स (Forex) & क्रिप्टो"))

symbol = ""

# 2. सिंबल चुनें
if market_type == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "SENSEX", "Custom Stock"))
    if option == "NIFTY 50": symbol = "^NSEI"
    elif option == "BANK NIFTY": symbol = "^NSEBANK"
    elif option == "SENSEX": symbol = "^BSESN"
    else:
        user_input = st.sidebar.text_input("शेयर का नाम (जैसे TATASTEEL.NS):", "RELIANCE.NS")
        symbol = user_input.upper()

elif market_type == "💱 फॉरेक्स (Forex) & क्रिप्टो":
    option = st.sidebar.selectbox("करेंसी पेयर:", ("EUR/USD", "GBP/USD", "USD/JPY", "USD/INR", "Bitcoin (USD)", "Gold (USD)"))
    if option == "EUR/USD": symbol = "EURUSD=X"
    elif option == "GBP/USD": symbol = "GBPUSD=X"
    elif option == "USD/JPY": symbol = "JPY=X"
    elif option == "USD/INR": symbol = "INR=X"
    elif option == "Bitcoin (USD)": symbol = "BTC-USD"
    elif option == "Gold (USD)": symbol = "GC=F"
    else:
        user_input = st.sidebar.text_input("सिंबल (Yahoo Finance वाला):", "EURUSD=X")
        symbol = user_input

# 3. टाइमफ्रेम
timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Day", "1 Hour", "15 Minutes"))

# --- टैब्स ---
tab1, tab2 = st.tabs(["📊 लाइव चार्ट", "🤖 AI एक्सपर्ट (Chat)"])

# ==========================================
# TAB 1: चार्ट और सिग्नल्स
# ==========================================
with tab1:
    if st.button("एनालिसिस करें 🚀"):
        with st.spinner(f'{symbol} का डेटा लोड हो रहा है...'):
            try:
                # टाइमफ्रेम लॉजिक
                p, i = ("1mo", "1h") if "1 Hour" in timeframe else ("5d", "15m") if "15 Minutes" in timeframe else ("1y", "1d")
                
                # डेटा डाउनलोड
                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty:
                    st.error(f"❌ डेटा नहीं मिला ({symbol})। फॉरेक्स के लिए सिंबल सही चेक करें।")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    
                    curr = df.iloc[-1]
                    val = float(curr['Close'])
                    
                    # सिग्नल लॉजिक
                    sig = "HOLD ⏸️"
                    color = "blue"
                    if curr['EMA_9'] > curr['EMA_21']:
                        sig = "BUY 🟢"
                        color = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        sig = "SELL 🔴"
                        color = "red"

                    # डिस्प्ले
                    st.subheader(f"📍 रिपोर्ट: {symbol}")
                    c1, c2 = st.columns([1, 3])
                    c1.metric("Current Price", f"{val:.4f}")
                    
                    if color == "green": c1.success(f"## {sig}")
                    elif color == "red": c1.error(f"## {sig}")
                    else: c1.info(f"## {sig}")
                    
                    c1.write(f"**RSI:** {curr['RSI']:.2f}")

                    # चार्ट
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dot", row=2, col=1); fig.add_hline(y=30, line_dash="dot", row=2, col=1)
                    fig.update_layout(height=500, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: AI चैट (FIXED)
# ==========================================
with tab2:
    st.header("🤖 मार्केट एक्सपर्ट")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).markdown(m["content"])
    
    if prompt := st.chat_input("सवाल पूछें (उदा: EUR/USD का ट्रेंड कैसा है?)..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            # AI जवाब
            with st.chat_message("assistant"):
                with st.spinner("AI रिसर्च कर रहा है..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"AI Error: {e}")
