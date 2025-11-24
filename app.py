import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import math
from datetime import datetime, timedelta

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Option Master", page_icon="🎯", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("नाम: शिखर तिवारी")
    st.success("Feature: Option Chain + Premium Pricing")
    st.markdown("---")

st.title("📈 शिखर तिवारी - मास्टर ट्रेडिंग टर्मिनल")
st.markdown("### 🚀 Nifty/BankNifty Option Chain & Live Levels")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट (Options)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
is_index = False

if market_cat == "🇮🇳 इंडियन मार्केट (Options)":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "TATA MOTORS", "SBIN"))
    if "NIFTY" in option:
        symbol = "^NSEI" if "50" in option else "^NSEBANK"
        is_index = True
    else: 
        symbol = f"{option.replace(' ', '')}.NS"

elif market_cat == "💱 फॉरेक्स & गोल्ड":
    option = st.sidebar.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY"))
    if "GOLD" in option: symbol = "GC=F"
    elif "SILVER" in option: symbol = "SI=F"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"
    elif "JPY" in option: symbol = "JPY=X"

elif market_cat == "🇺🇸 ग्लोबल मार्केट":
    symbol = "^IXIC"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- ब्लैक-शोल्स फॉर्मूला (प्रीमियम निकालने का गणित) ---
def black_scholes(S, K, T, r, sigma, option_type):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    # Normal Distribution Approximation
    def N(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    if option_type == "Call":
        price = S * N(d1) - K * math.exp(-r * T) * N(d2)
    else:
        price = K * math.exp(-r * T) * N(-d2) - S * N(-d1)
    
    return max(price, 0.05) # कम से कम 0.05

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 चार्ट & सिग्नल्स", "🎯 ऑप्शन चेन (Premium)", "📚 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: चार्ट और सिग्नल्स
# ==========================================
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀", key="btn1"):
        with st.spinner('डेटा लोड हो रहा है...'):
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
                    atr = float(curr['ATR']) if 'ATR' in df.columns and not pd.isna(curr['ATR']) else price * 0.01

                    # सिग्नल
                    action = "WAIT"
                    color = "#2962ff"
                    sl, tgt = 0.0, 0.0

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY 🟢"
                        color = "#008F4C"
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL 🔴"
                        color = "#D32F2F"
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)

                    # कार्ड
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; background-color: #ffffff; text-align: center;">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: #333;">LTP: ₹{price:.2f}</h2>
                        <div style="display: flex; justify-content: space-around; color: #555;">
                            <span>🛑 SL: <b>{sl:.2f}</b></span>
                            <span>🎯 TGT: <b>{tgt:.2f}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # चार्ट (Angel One Style)
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1.5), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1.5), name="EMA 21"), row=1, col=1)
                    vol_colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)
                    
                    fig.update_layout(height=600, paper_bgcolor='white', plot_bgcolor='white', xaxis_rangeslider_visible=False, showlegend=False, title=f"{symbol} Chart")
                    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0'); fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: ऑप्शन चेन (PREMIUM PRICE के साथ)
# ==========================================
with tab2:
    st.header("🎯 लाइव ऑप्शन चेन & प्रीमियम कैलकुलेटर")
    
    if st.button("ऑप्शन चेन दिखाओ 🎲"):
        if not is_index:
            st.warning("⚠️ यह फीचर सिर्फ NIFTY और BANKNIFTY के लिए बेस्ट है।")
        
        with st.spinner('प्रीमियम कैलकुलेट हो रहे हैं...'):
            try:
                # 1. स्पॉट प्राइस लाओ
                data = yf.Ticker(symbol).history(period="1d", interval="1m")
                spot_price = data['Close'].iloc[-1]
                
                # 2. स्ट्राइक गैप सेट करो
                step = 100 if "BANK" in symbol else 50
                atm_strike = round(spot_price / step) * step
                
                # 3. एक्सपायरी (अगले गुरुवार तक के दिन)
                today = datetime.now()
                days_to_expiry = (3 - today.weekday()) % 7 # गुरुवार (3)
                if days_to_expiry == 0: days_to_expiry = 7
                T = days_to_expiry / 365.0
                
                # 4. टेबल बनाना (आपकी फोटो जैसा)
                strikes = []
                for i in range(-4, 5): # 4 ऊपर, 4 नीचे
                    strikes.append(atm_strike + (i * step))
                
                option_data = []
                
                for k in strikes:
                    # प्रीमियम कैलकुलेशन
                    ce_price = black_scholes(spot_price, k, T, 0.07, 0.15, "Call")
                    pe_price = black_scholes(spot_price, k, T, 0.07, 0.15, "Put")
                    
                    # एंट्री प्राइस (थोड़ा बफर जोड़कर)
                    buy_ce_above = ce_price * 1.05 
                    buy_pe_above = pe_price * 1.05
                    
                    row = {
                        "Call LTP (₹)": f"₹{ce_price:.2f}",
                        "STRIKE": k,
                        "Put LTP (₹)": f"₹{pe_price:.2f}",
                        "Action": "ATM" if k == atm_strike else ""
                    }
                    option_data.append(row)

                # --- डेटा दिखाना ---
                st.metric("SPOT PRICE", f"₹{spot_price:.2f}")
                
                df_opt = pd.DataFrame(option_data)
                st.dataframe(df_opt.style.apply(lambda x: ['background-color: #e3f2fd' if x.name == 4 else '' for i in x], axis=1), use_container_width=True)

                # --- एंट्री कार्ड्स (USER REQUEST) ---
                st.markdown("### 💡 ट्रेडिंग सलाह (Premium Buying Levels)")
                
                # ATM का डेटा
                atm_row = option_data[4] # बीच वाला
                atm_ce = float(atm_row['Call LTP (₹)'].replace('₹',''))
                atm_pe = float(atm_row['Put LTP (₹)'].replace('₹',''))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"🟢 **CALL (CE) सेटअप**")
                    st.markdown(f"""
                    - **Strike:** {atm_strike} CE
                    - **Current Premium:** ₹{atm_ce:.2f}
                    - **👉 Buy Above:** **₹{atm_ce + 5:.2f}**
                    - **SL:** ₹{atm_ce - 10:.2f}
                    """)
                
                with col2:
                    st.error(f"🔴 **PUT (PE) सेटअप**")
                    st.markdown(f"""
                    - **Strike:** {atm_strike} PE
                    - **Current Premium:** ₹{atm_pe:.2f}
                    - **👉 Buy Above:** **₹{atm_pe + 5:.2f}**
                    - **SL:** ₹{atm_pe - 10:.2f}
                    """)
                
                st.caption("नोट: यह प्रीमियम Black-Scholes फॉर्मूले से निकाला गया अनुमानित भाव है। ब्रोकर ऐप में ₹2-4 का फर्क हो सकता है।")

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 3: कैंडल लाइब्रेरी (HINDI)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक पैटर्न गाइड")
    patterns = [
        {"name": "Hammer 🔨", "type": "Bullish", "desc": "गिरावट खत्म, अब ऊपर जाएगा।"},
        {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "तेजी खत्म, अब नीचे गिरेगा।"},
        {"name": "Bullish Engulfing 📈", "type": "Strong Buy", "desc": "हरी ने लाल को खा लिया।"},
        {"name": "Bearish Engulfing 📉", "type": "Strong Sell", "desc": "लाल ने हरी को खा लिया।"}
    ]
    for i, pat in enumerate(patterns):
        st.info(f"**{pat['name']}**\n\n{pat['desc']}")

# ==========================================
# TAB 4: AI
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
        except Exception as e: st.error(str(e))
