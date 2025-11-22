import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="Shikhar Trading Bot", page_icon="📊", layout="wide")

# --- API KEY ---
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except:
    pass

st.title("💰 Shikhar Trading Bot (History & Live)")
st.markdown("### 🟢 पिछला रिकॉर्ड देखें: कब खरीदना था और कब बेचना था")

# --- साइडबार सेटिंग्स ---
st.sidebar.header("⚙️ सेटिंग्स")

# 1. मार्केट टाइप
market_type = st.sidebar.radio("मार्केट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & क्रिप्टो"))

symbol = ""
if market_type == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("स्टॉक/इंडेक्स:", ("NIFTY 50", "BANK NIFTY", "RELIANCE.NS", "HDFCBANK.NS", "TATASTEEL.NS", "SBIN.NS", "INFY.NS"))
    symbol = "^NSEI" if option == "NIFTY 50" else "^NSEBANK" if option == "BANK NIFTY" else option
else:
    option = st.sidebar.selectbox("पेयर:", ("EUR/USD", "GBP/USD", "USD/JPY", "Bitcoin", "Gold"))
    if "EUR" in option: symbol = "EURUSD=X"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "JPY" in option: symbol = "JPY=X"
    elif "Bit" in option: symbol = "BTC-USD"
    elif "Gold" in option: symbol = "GC=F"

# 2. टाइमफ्रेम (विस्तृत रेंज)
timeframe = st.sidebar.selectbox(
    "टाइमफ्रेम चुनें:",
    ("1 Minute (Scalping)", "5 Minutes", "15 Minutes (Intraday)", "30 Minutes", "1 Hour", "1 Day (Swing)", "1 Week (Long Term)")
)

# --- टैब्स ---
tab1, tab2 = st.tabs(["📊 चार्ट और पिछला इतिहास", "🤖 AI गुरुजी"])

# TAB 1: चार्ट और हिस्ट्री
with tab1:
    if st.button("एनालिसिस शुरू करें 🚀"):
        with st.spinner('इतिहास खंगाला जा रहा है...'):
            try:
                # --- स्मार्ट टाइमफ्रेम सेटिंग ---
                # yfinance की लिमिट के हिसाब से डेटा मांगना
                period = "1y"
                interval = "1d"
                
                if "1 Minute" in timeframe:
                    period = "5d"   # 1 मिनट का डेटा सिर्फ 5-7 दिन का मिलता है
                    interval = "1m"
                elif "5 Minutes" in timeframe:
                    period = "5d"
                    interval = "5m"
                elif "15 Minutes" in timeframe:
                    period = "1mo"
                    interval = "15m"
                elif "30 Minutes" in timeframe:
                    period = "1mo"
                    interval = "30m"
                elif "1 Hour" in timeframe:
                    period = "1y"
                    interval = "1h"
                elif "1 Week" in timeframe:
                    period = "5y"
                    interval = "1wk"

                # डेटा डाउनलोड
                df = yf.Ticker(symbol).history(period=period, interval=interval)
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला। मार्केट बंद हो सकता है।")
                else:
                    # --- इंडिकेटर्स ---
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    
                    # --- पिछला इतिहास (Buy/Sell Signals) ढूँढना ---
                    # जहाँ EMA 9 ने EMA 21 को क्रॉस किया
                    buy_signals = []
                    sell_signals = []
                    
                    # पिछले डेटा पर लूप चलाकर सिग्नल खोजना
                    for i in range(1, len(df)):
                        # अगर पिछली कैंडल नीचे थी और अब ऊपर आ गई (Golden Cross - BUY)
                        if df['EMA_9'].iloc[i-1] < df['EMA_21'].iloc[i-1] and df['EMA_9'].iloc[i] > df['EMA_21'].iloc[i]:
                            buy_signals.append((df.index[i], df['Low'].iloc[i]))
                        
                        # अगर पिछली कैंडल ऊपर थी और अब नीचे आ गई (Death Cross - SELL)
                        elif df['EMA_9'].iloc[i-1] > df['EMA_21'].iloc[i-1] and df['EMA_9'].iloc[i] < df['EMA_21'].iloc[i]:
                            sell_signals.append((df.index[i], df['High'].iloc[i]))

                    # --- अभी का स्टेटस ---
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    action = "WAIT"
                    color = "blue"
                    
                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "UPTREND (Buy Zone) 🟢"
                        color = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "DOWNTREND (Sell Zone) 🔴"
                        color = "red"

                    # --- डिस्प्ले ---
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; text-align: center;">
                        <h2 style="color: {color};">CURRENT TREND: {action}</h2>
                        <h3>Price: {price:.2f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")

                    # --- एडवांस चार्ट ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])

                    # 1. Candlestick
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                    
                    # 2. EMA Lines
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)

                    # 3. BUY SIGNALS (Green Triangles) ▲
                    if buy_signals:
                        buy_dates, buy_prices = zip(*buy_signals)
                        fig.add_trace(go.Scatter(
                            x=buy_dates, y=buy_prices,
                            mode='markers',
                            marker=dict(symbol='triangle-up', size=12, color='green'),
                            name='BUY Signal'
                        ), row=1, col=1)

                    # 4. SELL SIGNALS (Red Triangles) ▼
                    if sell_signals:
                        sell_dates, sell_prices = zip(*sell_signals)
                        fig.add_trace(go.Scatter(
                            x=sell_dates, y=sell_prices,
                            mode='markers',
                            marker=dict(symbol='triangle-down', size=12, color='red'),
                            name='SELL Signal'
                        ), row=1, col=1)

                    # 5. RSI
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red")
                    fig.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green")

                    fig.update_layout(height=650, xaxis_rangeslider_visible=False, title=f"{symbol} - {timeframe}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.info("💡 चार्ट पर हरे रंग के तीर (▲) का मतलब है कि वहाँ 'BUY' सिग्नल मिला था, और लाल तीर (▼) का मतलब 'SELL' सिग्नल था।")

            except Exception as e: st.error(f"Error: {e}")

# TAB 2: AI चैट
with tab2:
    st.header("🤖 Shikhar Bot AI")
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
