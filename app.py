import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Master Bot", page_icon="🕯️", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- 📚 25+ कैंडल्स की विशाल लाइब्रेरी (Hindi Data) ---
CANDLE_LIBRARY = [
    # तेजी वाली कैंडल्स (Bullish)
    {"name": "Hammer (हथौड़ा) 🔨", "type": "Bullish", "desc": "बाजार गिरने के बाद बनता है। यह बताता है कि अब मार्केट ऊपर उठेगा।"},
    {"name": "Inverted Hammer 🔨", "type": "Bullish", "desc": "उल्टा हथौड़ा। यह भी गिरावट के अंत में बनता है और तेजी का संकेत देता है।"},
    {"name": "Bullish Engulfing 📈", "type": "Strong Buy", "desc": "छोटी लाल कैंडल को अगली बड़ी हरी कैंडल पूरा निगल लेती है। बहुत तगड़ी तेजी।"},
    {"name": "Morning Star 🌅", "type": "Bullish Reversal", "desc": "3 कैंडल का पैटर्न: 1 लाल, 1 छोटी डोजी, 1 हरी। रात गई, सवेरा (तेजी) हुआ।"},
    {"name": "Three White Soldiers 💂", "type": "Super Bullish", "desc": "लगातार 3 बड़ी हरी कैंडल्स। अब मार्केट रुकने वाला नहीं है, ऊपर जाएगा।"},
    {"name": "Piercing Line 🌤️", "type": "Bullish", "desc": "लाल कैंडल के बाद हरी कैंडल, जो लाल के आधे से ऊपर बंद हो।"},
    {"name": "Tweezer Bottom 🥢", "type": "Bullish", "desc": "दो कैंडल्स का निचला हिस्सा (Low) बराबर हो। यह मजबूत सपोर्ट है।"},
    {"name": "Marubozu Green 🟩", "type": "Full Power Buy", "desc": "बिना डंडी की बड़ी हरी कैंडल। खरीदार पूरी तरह हावी हैं।"},
    {"name": "Bullish Harami 🤰", "type": "Bullish", "desc": "बड़ी लाल कैंडल के पेट में छोटी हरी कैंडल। गिरावट रुक गई है।"},
    
    # मंदी वाली कैंडल्स (Bearish)
    {"name": "Shooting Star 🌠", "type": "Bearish", "desc": "तेजी के बाद ऊपर बनता है। अब मार्केट टूटकर गिरने वाला है।"},
    {"name": "Hanging Man 🧘", "type": "Bearish", "desc": "ऊपर जाते बाजार में हथौड़ा। यह खतरे की घंटी है, बेच दो।"},
    {"name": "Bearish Engulfing 📉", "type": "Strong Sell", "desc": "छोटी हरी कैंडल को अगली बड़ी लाल कैंडल पूरा निगल लेती है। भारी गिरावट।"},
    {"name": "Evening Star 🌃", "type": "Bearish Reversal", "desc": "3 कैंडल: 1 हरी, 1 डोजी, 1 लाल। दिन ढल गया, रात (मंदी) शुरू।"},
    {"name": "Three Black Crows 🦅", "type": "Super Bearish", "desc": "लगातार 3 बड़ी लाल कैंडल्स। मार्केट धड़ाम से गिरेगा।"},
    {"name": "Dark Cloud Cover ☁️", "type": "Bearish", "desc": "हरी कैंडल के बाद लाल कैंडल जो हरी के आधे से नीचे बंद हो।"},
    {"name": "Tweezer Top 🥢", "type": "Bearish", "desc": "दो कैंडल्स का ऊपरी हिस्सा (High) बराबर हो। यह मजबूत रेजिस्टेंस है।"},
    {"name": "Marubozu Red 🟥", "type": "Full Power Sell", "desc": "बिना डंडी की बड़ी लाल कैंडल। बेचने वाले पूरी तरह हावी हैं।"},
    {"name": "Bearish Harami 🤰", "type": "Bearish", "desc": "बड़ी हरी कैंडल के पेट में छोटी लाल कैंडल। तेजी रुक गई है।"},

    # कन्फ्यूजन वाली (Neutral)
    {"name": "Doji (डोजी) ➕", "type": "Neutral", "desc": "जहाँ खुला वहीं बंद। मार्केट कन्फ्यूज है। अभी ट्रेड न लें।"},
    {"name": "Spinning Top 🌪️", "type": "Neutral", "desc": "छोटी बॉडी, दोनों तरफ लंबी डंडी। बाजार में टक्कर चल रही है।"},
]

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("शिखर तिवारी (ईशान पंडित)")
    st.success("📱 93360-92738")
    st.markdown("---")

st.title("🕯️ शिखर तिवारी - मास्टर चार्ट & कैंडल्स")

# --- मार्केट सिलेक्शन ---
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
if market_cat == "🇮🇳 इंडियन मार्केट":
    option = st.sidebar.selectbox("स्टॉक:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK"))
    symbol = "^NSEI" if "NIFTY" in option else "^NSEBANK" if "BANK" in option else f"{option.replace(' ', '')}.NS"
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

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3 = st.tabs(["📊 लाइव चार्ट & सिग्नल्स", "📚 कैंडल लाइब्रेरी (25+)", "🤖 AI गुरुजी"])

# TAB 1: चार्ट और सिग्नल
with tab1:
    if st.button(f"{symbol} स्कैन करें 🚀"):
        with st.spinner('डेटा आ रहा है...'):
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
                    
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    
                    # सिग्नल लॉजिक
                    action = "WAIT (रुको)"
                    color = "blue"
                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY (खरीदें) 🟢"
                        color = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL (बेचें) 🔴"
                        color = "red"

                    # --- बड़ा सिग्नल बॉक्स ---
                    st.markdown(f"""
                    <div style="padding: 20px; border: 3px solid {color}; border-radius: 15px; background-color: {'#e8f5e9' if color=='green' else '#ffebee' if color=='red' else 'white'};">
                        <h1 style="color: {color}; text-align: center;">{action}</h1>
                        <h2 style="text-align: center; color: black;">Price: {price:.2f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- रंगीन चार्ट (Colorful) ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])

                    # कैंडल्स (लाल और हरी)
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="Price",
                        increasing_line_color='#00c853', decreasing_line_color='#ff3d00'
                    ), row=1, col=1)

                    # इंडिकेटर्स
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"), row=2, col=1)
                    
                    # RSI लाइन्स
                    fig.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red")
                    fig.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green")

                    fig.update_layout(height=700, xaxis_rangeslider_visible=False, title=f"{symbol} Colorful Chart")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# TAB 2: कैंडल लाइब्रेरी (ढेर सारी)
with tab2:
    st.header("📚 कैंडलस्टिक ज्ञान का खजाना")
    search = st.text_input("कैंडल का नाम खोजें...")
    
    col1, col2, col3 = st.columns(3)
    
    for i, candle in enumerate(CANDLE_LIBRARY):
        if search.lower() in candle['name'].lower():
            # रंग तय करना
            bg_color = "#d4edda" if "Bullish" in candle['type'] or "Buy" in candle['type'] else "#f8d7da" if "Bearish" in candle['type'] or "Sell" in candle['type'] else "#fff3cd"
            
            with col1 if i%3==0 else col2 if i%3==1 else col3:
                st.markdown(f"""
                <div style="
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    background-color: {bg_color};
                    color: black;
                ">
                    <h4 style="margin:0;">{candle['name']}</h4>
                    <p style="font-weight:bold; color: #333;">{candle['type']}</p>
                    <hr style="border-top: 1px solid #999;">
                    <p style="font-size: 14px;">{candle['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
                

[Image of forex trading chart]


# TAB 3: AI
with tab3:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("सवाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
        except Exception as e: st.error(str(e))
