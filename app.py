import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज की बेसिक सेटिंग ---
st.set_page_config(page_title="Super AI Trading Bot", page_icon="🚀", layout="wide")

st.title("🚀 AI सुपर ट्रेडिंग डैशबोर्ड")
st.markdown("### चार्ट्स, सिग्नल्स और AI रिसर्च - सब एक जगह")

# --- साइडबार: सेटिंग्स ---
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

# --- टैब्स बनाना ---
tab1, tab2 = st.tabs(["📊 टेक्निकल चार्ट & सिग्नल्स", "🤖 AI से सवाल पूछें (Chat)"])

# ==========================================
# TAB 1: टेक्निकल चार्ट और सिग्नल्स
# ==========================================
with tab1:
    if st.button("चार्ट अपडेट करें 🔄"):
        with st.spinner('मार्केट डेटा और चार्ट लोड हो रहा है...'):
            try:
                # टाइमफ्रेम सेट करना
                period = "1y"
                interval = "1d"
                if "1 Hour" in timeframe: 
                    period = "1mo"
                    interval = "1h"
                elif "15 Minutes" in timeframe: 
                    period = "5d"
                    interval = "15m"

                # --- डेटा डाउनलोड (Correct Method) ---
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला। कृपया सिंबल सही लिखें (जैसे: TCS.NS)।")
                else:
                    # इंडिकेटर्स बनाना
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    
                    current_price = float(df['Close'].iloc[-1])
                    
                    # सिग्नल का लॉजिक
                    signal = "HOLD ⏸️ (इंतजार करें)"
                    color = "blue"
                    curr = df.iloc[-1]

                    # Buy/Sell Logic
                    if curr['EMA_9'] > curr['EMA_21']:
                        signal = "BUY TREND 🟢 (तेजी)"
                        color = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        signal = "SELL TREND 🔴 (मंदी)"
                        color = "red"

                    # RSI Warning
                    rsi_msg = ""
                    if curr['RSI'] < 30: rsi_msg = " (Oversold - बाउंस आ सकता है)"
                    elif curr['RSI'] > 70: rsi_msg = " (Overbought - गिर सकता है)"

                    # --- स्क्रीन पर दिखाना ---
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        st.metric("अभी का भाव", f"₹{current_price:.2f}")
                        
                        if color == "green": st.success(f"### {signal}")
                        elif color == "red": st.error(f"### {signal}")
                        else: st.info(f"### {signal}")
                        
                        st.write(f"**RSI Score:** {curr['RSI']:.2f} {rsi_msg}")
                    
                    with c2:
                        # --- एडवांस चार्ट (Plotly) ---
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                            vertical_spacing=0.1, row_heights=[0.7, 0.3])

                        # 1. Price Candle
                        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                                     low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                        
                        # 2. EMA Lines
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)

                        # 3. RSI
                        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name="RSI"), row=2, col=1)
                        fig.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red")
                        fig.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green")

                        fig.update_layout(height=500, xaxis_rangeslider_visible=False, title=f"{symbol} लाइव चार्ट")
                        st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"तकनीकी खराबी: {e}")

# ==========================================
# TAB 2: AI चैटबॉट (Gemini 1.5 Flash)
# ==========================================
with tab2:
    st.header("🤖 शेयर मार्केट एक्सपर्ट (AI Chat)")
    st.caption("यहाँ आप मार्केट, किसी स्टॉक या ट्रेडिंग स्ट्रैटेजी के बारे में कुछ भी पूछ सकते हैं।")

    # API Key Warning
    if not api_key:
        st.warning("⚠️ कृपया पहले साइडबार (Left Side) में अपनी Google API Key डालें।")
    
    # चैट हिस्ट्री
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # पुराने मैसेज दिखाएं
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # यूजर का इनपुट
    prompt = st.chat_input("अपना सवाल यहाँ लिखें (जैसे: Tata Motors का फंडामेंटल कैसा है?)...")
    
    if prompt:
        # यूजर का मैसेज सेव करें
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # AI से जवाब मांगें
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # लेटेस्ट मॉडल
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # AI को निर्देश (Prompt)
                full_prompt = f"""You are an expert Indian Stock Market Analyst. 
                Answer the following question in clear Hindi (or Hinglish). 
                Keep the answer concise, accurate, and helpful for a trader.
                Question: {prompt}"""
                
                with st.chat_message("assistant"):
                    with st.spinner("AI रिसर्च कर रहा है..."):
                        response = model.generate_content(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"API Error (शायद Key गलत है या कोटा खत्म हो गया): {e}")
