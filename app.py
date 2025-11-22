import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Market Bot", page_icon="🚀", layout="wide")

# --- ऑटोमैटिक API Key सेटअप ---
# यह कोड चेक करेगा कि क्या Secrets में चाबी रखी है
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # अगर Secrets खाली है, तो साइडबार दिखाओ (बैकअप के लिए)
    st.sidebar.warning("⚠️ Secrets सेटिंग नहीं मिली। साइडबार में Key डालें।")
    api_key = st.sidebar.text_input("Google API Key:", type="password")

# --- मेन ऐप ---
st.title("🚀 शिखर तिवारी (ईशान पंडित) - AI ट्रेडिंग बॉट")
st.markdown("### स्टॉक एनालिसिस और AI रिसर्च")

# --- साइडबार सेटिंग्स ---
st.sidebar.header("⚙️ सेटिंग्स")
option = st.sidebar.selectbox("शेयर चुनें:", ("NIFTY 50", "BANK NIFTY", "SENSEX", "Custom Stock"))

symbol = ""
if option == "NIFTY 50": symbol = "^NSEI"
elif option == "BANK NIFTY": symbol = "^NSEBANK"
elif option == "SENSEX": symbol = "^BSESN"
else:
    user_input = st.sidebar.text_input("सिंबल लिखें (जैसे RELIANCE.NS)", "RELIANCE.NS")
    symbol = user_input.upper()

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Day", "1 Hour", "15 Minutes"))

# --- टैब्स ---
tab1, tab2 = st.tabs(["📊 चार्ट & सिग्नल्स", "🤖 AI से बात करें"])

# ==========================================
# TAB 1: चार्ट
# ==========================================
with tab1:
    if st.button("मार्केट चेक करें 🔄"):
        with st.spinner('डेटा लोड हो रहा है...'):
            try:
                period = "1y"
                interval = "1d"
                if "1 Hour" in timeframe: period, interval = "1mo", "1h"
                elif "15 Minutes" in timeframe: period, interval = "5d", "15m"

                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला।")
                else:
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    
                    current_price = float(df['Close'].iloc[-1])
                    curr = df.iloc[-1]
                    
                    # सिग्नल
                    signal = "HOLD ⏸️"
                    color = "blue"
                    if curr['EMA_9'] > curr['EMA_21']:
                        signal = "BUY 🟢"
                        color = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        signal = "SELL 🔴"
                        color = "red"

                    c1, c2 = st.columns([1, 3])
                    with c1:
                        st.metric("भाव", f"₹{current_price:.2f}")
                        if color == "green": st.success(f"### {signal}")
                        elif color == "red": st.error(f"### {signal}")
                        else: st.info(f"### {signal}")
                        st.write(f"RSI: {curr['RSI']:.2f}")
                    
                    with c2:
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"), row=2, col=1)
                        fig.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red")
                        fig.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green")
                        fig.update_layout(height=500, xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# TAB 2: AI चैटबॉट (Gemini Pro)
# ==========================================
with tab2:
    st.header("🤖 ईशान पंडित AI")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("सवाल पूछें...")
    
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-pro")
                
                with st.chat_message("assistant"):
                    with st.spinner("AI रिसर्च कर रहा है..."):
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"API Error: {e}")
        else:
            st.error("❌ चाबी नहीं मिली! कृपया Secrets सेटिंग्स चेक करें।")
