import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Pro Charts", page_icon="🕯️", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- 40 कैंडल्स की लाइब्रेरी (Hindi Database) ---
CANDLE_LIBRARY = [
    # --- SINGLE CANDLES (अकेली कैंडल) ---
    {"name": "Hammer (हथौड़ा) 🔨", "type": "Bullish", "desc": "बाजार नीचे गया लेकिन खरीदारों ने ऊपर धक्का दिया। अब तेजी आ सकती है।"},
    {"name": "Inverted Hammer 🔨 (उल्टा)", "type": "Bullish", "desc": "गिरावट के बाद बनता है। खरीदार कोशिश कर रहे हैं। ऊपर जा सकता है।"},
    {"name": "Hanging Man 🧘", "type": "Bearish", "desc": "तेजी के बाद बनता है। यह खतरे की घंटी है, बाजार गिर सकता है।"},
    {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "ऊपर जाने की कोशिश फेल हो गई। अब मंदी आ सकती है।"},
    {"name": "Doji (Standard) ➕", "type": "Neutral", "desc": "बाजार कन्फ्यूज है। जहाँ खुला वहीं बंद हुआ।"},
    {"name": "Dragonfly Doji 🦟", "type": "Bullish", "desc": "T जैसा दिखता है। गिरावट खत्म होने का इशारा है।"},
    {"name": "Gravestone Doji 🪦", "type": "Bearish", "desc": "उल्टा T दिखता है। तेजी खत्म होने का इशारा है।"},
    {"name": "Spinning Top (लट्टू) 🌪️", "type": "Neutral", "desc": "छोटी बॉडी, दोनों तरफ डंडी। बाजार किसी भी तरफ जा सकता है।"},
    {"name": "Marubozu Green 🟩", "type": "Strong Bullish", "desc": "सिर्फ बॉडी, कोई डंडी नहीं। खरीदार बहुत ताकतवर हैं।"},
    {"name": "Marubozu Red 🟥", "type": "Strong Bearish", "desc": "सिर्फ बॉडी, कोई डंडी नहीं। बेचने वाले बहुत ताकतवर हैं।"},
    
    # --- TWO CANDLES (दो कैंडल) ---
    {"name": "Bullish Engulfing 📈", "type": "Strong Bullish", "desc": "लाल कैंडल को हरी कैंडल ने पूरा ढक लिया। तगड़ी तेजी का संकेत।"},
    {"name": "Bearish Engulfing 📉", "type": "Strong Bearish", "desc": "हरी कैंडल को लाल कैंडल ने पूरा ढक लिया। भारी गिरावट का संकेत।"},
    {"name": "Tweezer Bottom 🥢", "type": "Bullish", "desc": "दो कैंडल का लो (Low) बिल्कुल बराबर है। सपोर्ट मिल गया है।"},
    {"name": "Tweezer Top 🥢", "type": "Bearish", "desc": "दो कैंडल का हाई (High) बिल्कुल बराबर है। रेजिस्टेंस बन गया है।"},
    {"name": "Piercing Line 🌤️", "type": "Bullish", "desc": "बड़ी लाल के बाद हरी कैंडल, जो लाल के 50% से ऊपर बंद हो।"},
    {"name": "Dark Cloud Cover ☁️", "type": "Bearish", "desc": "बड़ी हरी के बाद लाल कैंडल, जो हरी के 50% से नीचे बंद हो।"},
    {"name": "Bullish Harami 🤰", "type": "Bullish", "desc": "बड़ी लाल कैंडल के पेट में छोटी हरी कैंडल। गिरावट रुक गई है।"},
    {"name": "Bearish Harami 🤰", "type": "Bearish", "desc": "बड़ी हरी कैंडल के पेट में छोटी लाल कैंडल। तेजी रुक गई है।"},
    
    # --- THREE CANDLES (तीन कैंडल) ---
    {"name": "Morning Star 🌅", "type": "Bullish", "desc": "एक लाल, एक छोटी, फिर एक बड़ी हरी। रात खत्म, सवेरा शुरू (तेजी)।"},
    {"name": "Evening Star 🌃", "type": "Bearish", "desc": "एक हरी, एक छोटी, फिर एक बड़ी लाल। दिन खत्म, रात शुरू (मंदी)।"},
    {"name": "Three White Soldiers 💂", "type": "Strong Bullish", "desc": "लगातार तीन बड़ी हरी कैंडल्स। बहुत मजबूत अपट्रेंड।"},
    {"name": "Three Black Crows 🦅", "type": "Strong Bearish", "desc": "लगातार तीन बड़ी लाल कैंडल्स। बहुत मजबूत डाउनट्रेंड।"},
    
    # --- ADVANCED ---
    {"name": "Rising Three Methods 📶", "type": "Continuation", "desc": "तेजी के बीच में थोड़ा आराम, फिर वापस तेजी।"},
    {"name": "Falling Three Methods 📉", "type": "Continuation", "desc": "मंदी के बीच में थोड़ा आराम, फिर वापस मंदी।"},
    {"name": "Tasuki Gap Up ⤴️", "type": "Bullish", "desc": "गैप के साथ खुलने के बाद भी बाजार ऊपर जाए।"},
    {"name": "Tasuki Gap Down ⤵️", "type": "Bearish", "desc": "गैप के साथ नीचे खुलने के बाद और नीचे जाए।"}
]

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("नाम: शिखर तिवारी (ईशान पंडित)")
    st.warning("📞 93360-92738")
    st.success("📧 shikhartiwari9336@gmail.com")
    st.markdown("---")

st.title("🕯️ शिखर तिवारी - प्रो चार्ट & कैंडलस्टिक पैटर्न")
st.markdown("### 🚀 Professional Dark Charts with Volume & Patterns")

# --- मार्केट सिलेक्शन ---
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("मार्केट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
if market_cat == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "HDFC BANK", "TATA MOTORS", "SBIN", "ADANI ENT"))
    symbol = "^NSEI" if "NIFTY" in option else "^NSEBANK" if "BANK" in option else f"{option.replace(' ', '')}.NS"

elif market_cat == "💱 फॉरेक्स & गोल्ड":
    option = st.sidebar.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY"))
    if "GOLD" in option: symbol = "GC=F"
    elif "SILVER" in option: symbol = "SI=F"
    elif "GBP" in option: symbol = "GBPUSD=X"
    elif "EUR" in option: symbol = "EURUSD=X"
    elif "JPY" in option: symbol = "JPY=X"

elif market_cat == "🇺🇸 ग्लोबल मार्केट":
    symbol = "^IXIC" # Default NASDAQ

elif market_cat == "₿ क्रिप्टो":
    symbol = "BTC-USD"

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3 = st.tabs(["📊 प्रो चार्ट (Dark Mode)", "📖 40 कैंडल्स (हिंदी ज्ञान)", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: डार्क मोड चार्ट + वॉल्यूम (आपकी फोटो जैसा)
# ==========================================
with tab1:
    if st.button(f"{symbol} चार्ट देखें 🚀"):
        with st.spinner('प्रो चार्ट लोड हो रहा है...'):
            try:
                # टाइमफ्रेम लॉजिक
                p, i = ("1y", "1d")
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"

                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty: st.error("❌ डेटा नहीं मिला")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    
                    # सिग्नल लॉजिक
                    last = df.iloc[-1]
                    price = float(last['Close'])
                    
                    action = "WAIT"
                    color = "blue"
                    if last['EMA_9'] > last['EMA_21']:
                        action = "BUY ZONE 🟢"
                        color = "green"
                    elif last['EMA_9'] < last['EMA_21']:
                        action = "SELL ZONE 🔴"
                        color = "red"

                    # --- कार्ड ---
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; background-color: #1e1e1e; color: white;">
                        <h2 style="color: {'#00ff00' if color=='green' else '#ff4444' if color=='red' else 'white'}; text-align: center; margin:0;">{action}</h2>
                        <h3 style="text-align: center;">Price: {price:.2f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- प्रो चार्ट (Dark + Volume) ---
                    # 2 rows: ऊपर Price, नीचे Volume
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                        vertical_spacing=0.03, row_heights=[0.75, 0.25])

                    # 1. Candlestick (TradingView Colors)
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="Price",
                        increasing_line_color='#089981', # TradingView Green
                        decreasing_line_color='#f23645'  # TradingView Red
                    ), row=1, col=1)

                    # 2. EMAs
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='#2962ff', width=1), name="EMA 21"), row=1, col=1)

                    # 3. Volume Bar Chart (नीचे वाली लाइनें)
                    colors = ['#f23645' if c < o else '#089981' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(
                        x=df.index, y=df['Volume'],
                        marker_color=colors,
                        name="Volume"
                    ), row=2, col=1)

                    # --- Dark Theme Settings ---
                    fig.update_layout(
                        template="plotly_dark", # यह है डार्क मोड का जादू
                        paper_bgcolor="#131722", # TradingView Dark Background
                        plot_bgcolor="#131722",
                        height=700,
                        title=f"{symbol} Professional Chart",
                        xaxis_rangeslider_visible=False,
                        showlegend=False
                    )
                    
                    # ग्रिड लाइन्स हटाना (साफ लुक के लिए)
                    fig.update_xaxes(showgrid=False)
                    fig.update_yaxes(showgrid=True, gridcolor='#2a2e39') # हल्की लाइन

                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: 40 कैंडल्स की लाइब्रेरी (HINDI)
# ==========================================
with tab2:
    st.header("📚 40+ कैंडलस्टिक पैटर्न (विस्तृत हिंदी ज्ञान)")
    st.markdown("यहाँ शेयर बाजार की हर महत्वपूर्ण कैंडल के बारे में बताया गया है:")

    # सर्च बार
    search = st.text_input("कैंडल का नाम खोजें (Search)...")

    # कार्ड्स दिखाना
    cols = st.columns(3) # 3 कार्ड एक लाइन में
    
    for i, candle in enumerate(CANDLE_LIBRARY):
        if search.lower() in candle['name'].lower():
            # रंग तय करना
            color = "#d4edda" if "Bullish" in candle['type'] else "#f8d7da" if "Bearish" in candle['type'] else "#fff3cd"
            text_color = "green" if "Bullish" in candle['type'] else "red" if "Bearish" in candle['type'] else "orange"
            
            with cols[i % 3]:
                st.markdown(f"""
                <div style="
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 20px;
                    background-color: {color};
                    height: 200px;
                ">
                    <h3 style="margin: 0; color: #333;">{candle['name']}</h3>
                    <p style="font-weight: bold; color: {text_color};">{candle['type']}</p>
                    <hr>
                    <p style="color: #444; font-size: 14px;">{candle['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
                
# ==========================================
# TAB 3: AI
# ==========================================
with tab3:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
        except Exception as e: st.error(str(e))
