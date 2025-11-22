import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Super AI Trading Bot", page_icon="🚀", layout="wide")

st.title("🚀 AI सुपर ट्रेडिंग डैशबोर्ड")
st.markdown("### चार्ट्स, सिग्नल्स और AI रिसर्च - सब एक जगह")

# --- साइडबार: API Key और सेटिंग्स ---
st.sidebar.header("🔑 AI चाबी (API Key)")
api_key = st.sidebar.text_input("Google API Key पेस्ट करें:", type="password")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ चार्ट सेटिंग्स")
option = st.sidebar.selectbox("शेयर चुनें:", ("NIFTY 50", "BANK NIFTY", "SENSEX", "Custom Stock"))

symbol = ""
if option == "NIFTY 50": symbol = "^NSEI"
elif option == "BANK NIFTY": symbol = "^NSEBANK"
elif option == "SENSEX": symbol = "^BSESN"
else:
    user_input = st.sidebar.text_input("सिंबल लिखें (जैसे RELIANCE.NS)", "RELIANCE.NS")
    symbol = user_input.upper()

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Day", "1 Hour", "15 Minutes"))

# --- टैब्स (Tabs) ---
tab1, tab2 = st.tabs(["📊 टेक्निकल चार्ट & सिग्नल्स", "🤖 AI से सवाल पूछें (Chat)"])

# ==========================================
# TAB 1: टेक्निकल चार्ट (FIXED CODE)
# ==========================================
with tab1:
    if st.button("चार्ट अपडेट करें 🔄"):
        with st.spinner('मार्केट डेटा लाया जा रहा है...'):
            try:
                # टाइमफ्रेम लॉजिक
                period = "1y"
                interval = "1d"
                if "1 Hour" in timeframe: period, interval = "1mo", "1h"
                elif "15 Minutes" in timeframe: period, interval = "5d", "15m"

                # --- FIX: डेटा लाने का सुरक्षित तरीका ---
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला। कृपया सिंबल सही लिखें।")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    
                    current_price = float(df['Close'].iloc[-1])
                    
                    # सिग्नल लॉजिक
                    signal = "HOLD ⏸️"
                    color = "blue"
                    curr = df.iloc[-1]

                    if curr['EMA_9'] > curr['EMA_21']:
                        signal = "BUY TREND 🟢"
                        color = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        signal = "SELL TREND 🔴"
                        color = "red"

                    # डिस्प्ले
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        st.metric("अभी का भाव", f"₹{current_price:.2f}")
                        if color == "green": st.success(f"### {signal}")
                        elif color == "red": st.error(f"### {signal}")
                        else: st.info(f"### {signal}")
                        st.write(f"**RSI:** {curr['RSI']:.2f}")
                    
                    with c2:
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                        # चार्ट में कैंडलस्टिक
                        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                        # इंडिकेटर लाइन्स
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)
                        # RSI
                        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name="RSI"), row=2, col=1)
                        fig.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red")
                        fig.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green")
                        
                        fig.update_layout(height=500, xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"तकनीकी एरर: {e}")

# ==========================================
# TAB 2: AI चैटबॉट
# ==========================================
with tab2:
    st.header("🤖 शेयर मार्केट एक्सपर्ट से पूछें")
    
    # API Key चेक
    if not api_key:
        st.warning("⚠️ पहले साइडबार (Sidebar) में अपनी Google API Key डालें।")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("अपना सवाल यहाँ लिखें...")
    
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                full_prompt = f"You are a helpful Indian Stock Market Expert. Answer this question in Hindi (Hinglish) clearly: {prompt}"
                
                with st.chat_message("assistant"):
                    with st.spinner("AI सोच रहा है..."):
                        response = model.generate_content(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"API Error: {e}")
