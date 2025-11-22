import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

st.set_page_config(page_title="AI Trading Bot", page_icon="📈", layout="wide")

# ==========================================
# 🔑 API KEY (HARDCODED)
# ==========================================
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

# --- AI स्मार्ट सेटअप (Auto-Switching) ---
# यह कोड चेक करेगा कि कौन सा मॉडल चल रहा है
active_model = None

try:
    genai.configure(api_key=api_key)
    # पहले Flash ट्राई करें
    model_test = genai.GenerativeModel("gemini-1.5-flash")
    active_model = model_test
except:
    try:
        # अगर Flash फेल हो, तो Pro ट्राई करें
        model_test = genai.GenerativeModel("gemini-pro")
        active_model = model_test
    except Exception as e:
        st.error(f"AI सेटअप फेल हो गया: {e}")

st.title("🌍 AI ग्लोबल ट्रेडिंग डैशबोर्ड")

# --- साइडबार ---
st.sidebar.header("⚙️ मार्केट चुनें")
market_type = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & क्रिप्टो"))

symbol = ""
if market_type == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE.NS", "TATASTEEL.NS"))
    symbol = "^NSEI" if option == "NIFTY 50" else "^NSEBANK" if option == "BANK NIFTY" else option
else:
    option = st.sidebar.selectbox("पेयर:", ("EUR/USD", "GBP/USD", "Bitcoin", "Gold"))
    symbol = "EURUSD=X" if "EUR" in option else "GBPUSD=X" if "GBP" in option else "BTC-USD" if "Bit" in option else "GC=F"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Day", "1 Hour"))

# --- टैब्स ---
tab1, tab2 = st.tabs(["📊 चार्ट", "🤖 AI चैट"])

# TAB 1: चार्ट
with tab1:
    if st.button("चार्ट देखें 🚀"):
        with st.spinner('डेटा आ रहा है...'):
            try:
                p, i = ("1mo", "1h") if "1 Hour" in timeframe else ("1y", "1d")
                df = yf.Ticker(symbol).history(period=p, interval=i)
                if df.empty: st.error("❌ डेटा नहीं मिला")
                else:
                    df['EMA_9'], df['EMA_21'] = df.ta.ema(length=9), df.ta.ema(length=21)
                    val = float(df['Close'].iloc[-1])
                    st.metric("Price", f"{val:.2f}")
                    
                    fig = make_subplots(rows=1, cols=1)
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange')))
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue')))
                    fig.update_layout(xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e: st.error(f"Error: {e}")

# TAB 2: AI चैट (Smart)
with tab2:
    st.header("🤖 AI एक्सपर्ट")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).markdown(m["content"])
    
    if prompt := st.chat_input("सवाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        if active_model:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("AI जवाब दे रहा है..."):
                        response = active_model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("AI मॉडल कनेक्ट नहीं हो पाया।")
