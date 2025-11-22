import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

st.set_page_config(page_title="Shikhar AI Bot", page_icon="🚀", layout="wide")

# ==========================================
# 🔑 API KEY (यहाँ अपनी चाबी रखें)
# ==========================================
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

# --- AI मॉडल सेटअप (Safety Check के साथ) ---
try:
    genai.configure(api_key=api_key)
    # हम सबसे पहले Flash मॉडल ट्राई करेंगे
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"API Error: {e}")

st.title("🚀 शिखर तिवारी - AI ट्रेडिंग बॉट")

# --- साइडबार ---
st.sidebar.header("⚙️ सेटिंग्स")
option = st.sidebar.selectbox("शेयर चुनें:", ("NIFTY 50", "BANK NIFTY", "SENSEX", "Custom Stock"))
symbol = "^NSEI" if option == "NIFTY 50" else "^NSEBANK" if option == "BANK NIFTY" else "^BSESN" if option == "SENSEX" else st.sidebar.text_input("सिंबल:", "RELIANCE.NS").upper()
timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Day", "1 Hour", "15 Minutes"))

# --- टैब्स ---
tab1, tab2 = st.tabs(["📊 चार्ट", "🤖 AI चैट"])

# TAB 1: चार्ट
with tab1:
    if st.button("चार्ट देखें 🔄"):
        with st.spinner('डेटा आ रहा है...'):
            try:
                p, i = ("1mo", "1h") if "1 Hour" in timeframe else ("5d", "15m") if "15 Minutes" in timeframe else ("1y", "1d")
                df = yf.Ticker(symbol).history(period=p, interval=i)
                if df.empty: st.error("❌ डेटा नहीं मिला")
                else:
                    df['EMA_9'], df['EMA_21'], df['RSI'] = df.ta.ema(length=9), df.ta.ema(length=21), df.ta.rsi(length=14)
                    curr = df.iloc[-1]
                    val = float(curr['Close'])
                    sig = "BUY 🟢" if curr['EMA_9'] > curr['EMA_21'] else "SELL 🔴" if curr['EMA_9'] < curr['EMA_21'] else "HOLD ⏸️"
                    c1, c2 = st.columns([1, 3])
                    c1.metric("भाव", f"₹{val:.2f}")
                    if "BUY" in sig: c1.success(f"## {sig}")
                    elif "SELL" in sig: c1.error(f"## {sig}")
                    else: c1.info(f"## {sig}")
                    
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dot", row=2, col=1); fig.add_hline(y=30, line_dash="dot", row=2, col=1)
                    fig.update_layout(height=500, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e: st.error(f"Error: {e}")

# TAB 2: AI चैट
with tab2:
    st.header("🤖 AI एक्सपर्ट")
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
        except Exception as e:
            # अगर Flash फेल हुआ, तो पुराना Pro मॉडल ट्राई करेंगे (Fallback)
            try:
                fallback_model = genai.GenerativeModel("gemini-pro")
                response = fallback_model.generate_content(prompt)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error(f"Error: {e}. (कृपया requirements.txt चेक करें)")
