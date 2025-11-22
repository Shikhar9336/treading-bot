import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd  # <-- यह लाइन जोड़ दी गई है
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

st.set_page_config(page_title="Shikhar Trading Pro", page_icon="💰", layout="wide")

# --- API KEY ---
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except:
    pass

st.title("💰 शिखर तिवारी - प्रो ट्रेडिंग सिग्नल")

# --- साइडबार ---
st.sidebar.header("⚙️ मार्केट चुनें")
market_type = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & क्रिप्टो"))

symbol = ""
if market_type == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE.NS", "HDFCBANK.NS", "TATASTEEL.NS", "INFY.NS"))
    symbol = "^NSEI" if option == "NIFTY 50" else "^NSEBANK" if option == "BANK NIFTY" else option
else:
    option = st.sidebar.selectbox("पेयर:", ("EUR/USD", "GBP/USD", "USD/JPY", "Bitcoin", "Gold"))
    if "EUR" in option: symbol = "EURUSD=X"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "JPY" in option: symbol = "JPY=X"
    elif "Bit" in option: symbol = "BTC-USD"
    elif "Gold" in option: symbol = "GC=F"

timeframe = st.sidebar.selectbox("टाइमफ्रेम (Trading Style):", ("1 Day (Swing)", "1 Hour (Short Term)", "15 Minutes (Intraday)"))

# --- टैब्स ---
tab1, tab2 = st.tabs(["⚡ सिग्नल्स & लेवल्स", "🤖 AI गुरुजी"])

# TAB 1: सिग्नल्स
with tab1:
    if st.button("सिग्नल दिखाओ 🚀"):
        with st.spinner('मार्केट को स्कैन किया जा रहा है...'):
            try:
                # डेटा लाओ
                p, i = ("1mo", "1h") if "1 Hour" in timeframe else ("5d", "15m") if "15 Minutes" in timeframe else ("1y", "1d")
                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला")
                else:
                    # --- कैलकुलेशन ---
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    df['ATR'] = df.ta.atr(length=14)
                    
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    
                    # ATR चेक (यहीं पर Error था, अब ठीक है)
                    atr = 0
                    if 'ATR' in df.columns and not pd.isna(curr['ATR']):
                        atr = float(curr['ATR'])
                    else:
                        atr = price * 0.01
                    
                    # सिग्नल लॉजिक
                    trend = "SIDEWAYS ⏸️"
                    action = "WAIT (इंतजार करें)"
                    color = "blue"
                    
                    sl = 0.0
                    tgt = 0.0
                    
                    if curr['EMA_9'] > curr['EMA_21']:
                        trend = "UPTREND 🟢"
                        action = "BUY (खरीदें)"
                        color = "green"
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                    elif curr['EMA_9'] < curr['EMA_21']:
                        trend = "DOWNTREND 🔴"
                        action = "SELL (बेचें)"
                        color = "red"
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)
                    
                    # --- रिजल्ट कार्ड ---
                    st.markdown(f"""
                    <div style="padding: 20px; background-color: {'#e6fffa' if color == 'green' else '#fff5f5' if color == 'red' else '#f0f9ff'}; border-radius: 10px; border: 2px solid {color};">
                        <h2 style="color: {color}; text-align: center;">ACTION: {action}</h2>
                        <h3 style="text-align: center;">अभी का भाव: ₹{price:.2f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # लेवल्स दिखाएं
                    if color != "blue":
                        c1, c2, c3 = st.columns(3)
                        c1.metric("🛑 Stop Loss (SL)", f"₹{sl:.2f}", delta_color="inverse")
                        c2.metric("🎯 Target (TGT)", f"₹{tgt:.2f}")
                        c3.metric("📈 RSI Strength", f"{curr['RSI']:.2f}")
                        
                        if color == "green":
                            st.success(f"✅ **सलाह:** ₹{sl:.2f} के स्टॉप लॉस के साथ खरीद सकते हैं।")
                        else:
                            st.error(f"✅ **सलाह:** ₹{sl:.2f} के स्टॉप लॉस के साथ बेच सकते हैं।")
                    else:
                        st.info("⚠️ अभी ट्रेड न लें, मार्केट साइडवेज है।")

                    st.markdown("---")
                    
                    # चार्ट
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dot", row=2, col=1); fig.add_hline(y=30, line_dash="dot", row=2, col=1)
                    fig.update_layout(height=600, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"तकनीकी खराबी: {e}")

# TAB 2: AI चैट
with tab2:
    st.header("🤖 ट्रेडिंग गुरु")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).markdown(m["content"])
    
    if prompt := st.chat_input("सवाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            with st.chat_message("assistant"):
                with st.spinner("सोच रहा हूँ..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e: st.error(f"Error: {e}")
