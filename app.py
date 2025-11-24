import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import numpy as np

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Master Trade", page_icon="📊", layout="wide")

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
    st.success("मोड: ऑप्शन चेन + टेक्निकल")
    st.markdown("---")

st.title("📈 शिखर तिवारी - एडवांस्ड ऑप्शन & टेक्निकल बॉट")
st.markdown("### 🚀 Nifty/BankNifty Option Chain & Technicals")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट (Options)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
is_index = False # ऑप्शन चेन सिर्फ इंडेक्स के लिए दिखाएंगे

if market_cat == "🇮🇳 इंडियन मार्केट (Options)":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "TATA MOTORS", "SBIN"))
    if "NIFTY" in option:
        symbol = "^NSEI" if "50" in option else "^NSEBANK"
        is_index = True
    else: 
        symbol = f"{option.replace(' ', '')}.NS"

elif market_cat == "💱 फॉरेक्स & गोल्ड":
    option = st.sidebar.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD"))
    if "GOLD" in option: symbol = "GC=F"
    elif "SILVER" in option: symbol = "SI=F"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"

elif market_cat == "🇺🇸 ग्लोबल मार्केट":
    symbol = "^IXIC"

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 टेक्निकल चार्ट", "🎯 ऑप्शन चेन डेटा", "📚 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: लाइव चार्ट (CLEAN LOOK)
# ==========================================
with tab1:
    if st.button(f"{symbol} चार्ट स्कैन करें 🚀", key="btn1"):
        with st.spinner('डेटा लोड हो रहा है...'):
            try:
                p, i = ("5d", "5m") if "5" in timeframe else ("1mo", "15m") if "15" in timeframe else ("1y", "1h") if "1 H" in timeframe else ("1y", "1d")
                
                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty: st.error("❌ डेटा नहीं मिला")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    
                    # सिग्नल
                    action = "WAIT"
                    color = "#2962ff"
                    
                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY CALL (CE) 🟢"
                        color = "#008F4C"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "BUY PUT (PE) 🔴"
                        color = "#D32F2F"

                    # कार्ड
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; background-color: #ffffff; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: #333;">LTP: ₹{price:.2f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # चार्ट
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)
                    vol_colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)
                    
                    fig.update_layout(paper_bgcolor='white', plot_bgcolor='white', height=600, title=f"{symbol} Chart", xaxis_rangeslider_visible=False, showlegend=False)
                    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0'); fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: ऑप्शन चेन एनालिसिस (NEW FEATURE)
# ==========================================
with tab2:
    st.header("🎯 ऑप्शन चेन एनालिसिस (Support & Resistance)")
    
    if not is_index:
        st.warning("⚠️ ऑप्शन चेन डेटा केवल NIFTY और BANK NIFTY के लिए बेहतर काम करता है।")
    
    if st.button("ऑप्शन डेटा निकालें 🎲"):
        with st.spinner('ऑप्शन चेन डीकोड हो रही है...'):
            try:
                ticker = yf.Ticker(symbol)
                # करंट प्राइस
                current_price = ticker.history(period="1d")['Close'].iloc[-1]
                
                # एक्सपायरी डेट्स
                expirations = ticker.options
                if not expirations:
                    st.error("❌ ऑप्शन डेटा नहीं मिला (शायद फ्री डेटा में उपलब्ध नहीं है)")
                else:
                    # सबसे पास वाली एक्सपायरी
                    expiry = expirations[0]
                    opt = ticker.option_chain(expiry)
                    
                    calls = opt.calls
                    puts = opt.puts
                    
                    # --- 1. PCR (Put Call Ratio) ---
                    total_put_oi = puts['openInterest'].sum()
                    total_call_oi = calls['openInterest'].sum()
                    pcr = total_put_oi / total_call_oi
                    
                    pcr_signal = "NEUTRAL"
                    pcr_color = "orange"
                    if pcr > 1.2: 
                        pcr_signal = "BULLISH (Call Buy करो) 🟢"
                        pcr_color = "green"
                    elif pcr < 0.8: 
                        pcr_signal = "BEARISH (Put Buy करो) 🔴"
                        pcr_color = "red"

                    # --- 2. Support & Resistance (Max OI) ---
                    # Resistance = Max Call OI
                    max_call_oi_row = calls.loc[calls['openInterest'].idxmax()]
                    resistance_level = max_call_oi_row['strike']
                    
                    # Support = Max Put OI
                    max_put_oi_row = puts.loc[puts['openInterest'].idxmax()]
                    support_level = max_put_oi_row['strike']

                    # --- डिस्प्ले ---
                    st.subheader(f"📊 Expiry: {expiry}")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Current Price (Spot)", f"₹{current_price:.2f}")
                    col2.metric("PCR Ratio", f"{pcr:.2f}", pcr_signal)
                    
                    # सिग्नल बॉक्स
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: {pcr_color}; color: white; border-radius: 5px; text-align: center;">
                        <h3>PCR Signal: {pcr_signal}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")
                    st.markdown("### 🛡️ महत्वपूर्ण लेवल्स (Important Levels)")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.error(f"🛑 **RESISTANCE (रुकावट): {resistance_level}**")
                        st.caption(f"यहाँ सबसे ज्यादा Call Sellers बैठे हैं। बाजार को इसके ऊपर जाने में दिक्कत होगी।")
                    with c2:
                        st.success(f"✅ **SUPPORT (सहारा): {support_level}**")
                        st.caption(f"यहाँ सबसे ज्यादा Put Sellers बैठे हैं। बाजार यहाँ से उछल सकता है।")

                    st.info("💡 **टिप:** अगर बाजार 'Support' के पास आए और PCR 1 से ऊपर हो, तो **Call (ATM)** खरीदें। अगर 'Resistance' के पास आए और PCR 1 से कम हो, तो **Put (ATM)** खरीदें।")

            except Exception as e:
                st.error(f"Option Data Error (Free API Limit): {e}")

# ==========================================
# TAB 3: कैंडल लाइब्रेरी (HINDI)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक पैटर्न गाइड")
    patterns = [
        {"name": "Hammer (हथौड़ा) 🔨", "type": "Bullish", "desc": "बाजार गिरने के बाद बनता है। अब ऊपर जाएगा।"},
        {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "बाजार चढ़ने के बाद बनता है। अब नीचे गिरेगा।"},
        {"name": "Bullish Engulfing 📈", "type": "Strong Buy", "desc": "बड़ी हरी कैंडल ने लाल को खा लिया। तेजी आएगी।"},
        {"name": "Bearish Engulfing 📉", "type": "Strong Sell", "desc": "बड़ी लाल कैंडल ने हरी को खा लिया। मंदी आएगी।"}
    ]
    col1, col2 = st.columns(2)
    for i, pat in enumerate(patterns):
        with col1 if i % 2 == 0 else col2:
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
