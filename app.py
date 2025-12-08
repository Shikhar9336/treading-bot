import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Pro Terminal", page_icon="📈", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except: pass

# --- साइडबार सेटिंग्स ---
with st.sidebar:
    st.header("⚙️ डिस्प्ले सेटिंग्स")
    theme_choice = st.radio("थीम:", ("Light Mode (सफेद)", "Dark Mode (काला)"))
    
    st.subheader("📈 चार्ट इंडिकेटर्स")
    show_ema = st.checkbox("EMA (9 & 21)", value=True)
    show_bb = st.checkbox("Bollinger Bands", value=True)
    show_macd = st.checkbox("MACD Panel", value=True)
    
    st.markdown("---")
    st.info("👤 **Trader:** शिखर तिवारी")

# थीम कलर्स
if "Dark" in theme_choice:
    bg_color = "#0e1117"
    card_bg = "#1e1e1e"
    text_color = "white"
    chart_theme = "plotly_dark"
else:
    bg_color = "#ffffff"
    card_bg = "#f0f2f6"
    text_color = "black"
    chart_theme = "plotly_white"

# CSS
st.markdown(f"""<style>.stApp {{ background-color: {bg_color}; color: {text_color}; }}</style>""", unsafe_allow_html=True)

st.title("📈 शिखर तिवारी - मास्टर ट्रेडिंग टर्मिनल")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
col1, col2, col3 = st.columns(3)
with col1:
    market_cat = st.selectbox("मार्केट:", ("🇮🇳 इंडियन मार्केट", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल", "₿ क्रिप्टो"))

with col2:
    symbol = ""
    if "इंडियन" in market_cat:
        opt = st.selectbox("सिंबल:", ("NIFTY 50", "BANK NIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK"))
        symbol = "^NSEI" if "NIFTY" in opt else "^NSEBANK" if "BANK" in opt else f"{opt.replace(' ','')}.NS"
    elif "फॉरेक्स" in market_cat:
        opt = st.selectbox("सिंबल:", ("GOLD (XAUUSD)", "SILVER", "EUR/USD", "GBP/USD"))
        symbol = "GC=F" if "GOLD" in opt else "SI=F" if "SILVER" in opt else "EURUSD=X" if "EUR" in opt else "GBPUSD=X"
    elif "ग्लोबल" in market_cat:
        symbol = "^IXIC"
    else:
        symbol = "BTC-USD"

with col3:
    timeframe = st.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "1 Day"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 प्रो चार्ट (Advance)", "🎯 स्मार्ट ऑप्शन & PCR", "🕯️ 32 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: प्रो चार्ट (Bollinger + MACD)
# ==========================================
with tab1:
    if st.button(f"{symbol} चार्ट देखें 🚀"):
        with st.spinner('प्रो चार्ट बन रहा है...'):
            try:
                p, i = ("1y", "1d")
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"

                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty: st.error("डेटा नहीं मिला")
                else:
                    # इंडिकेटर्स कैलकुलेशन
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    bb = df.ta.bbands(length=20, std=2)
                    df = pd.concat([df, bb], axis=1)
                    macd = df.ta.macd(fast=12, slow=26, signal=9)
                    df = pd.concat([df, macd], axis=1)

                    # सिग्नल लॉजिक
                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    action = "WAIT"
                    color = "blue"
                    
                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY ZONE 🟢"
                        color = "green"
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL ZONE 🔴"
                        color = "red"

                    st.markdown(f"""
                    <div style="padding:10px; border:2px solid {color}; border-radius:10px; text-align:center; background-color:{card_bg};">
                        <h2 style="color:{color}; margin:0;">{action}</h2>
                        <h3>LTP: {price:.2f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- ADVANCED CHART ---
                    rows = 2 if show_macd else 1
                    row_heights = [0.75, 0.25] if show_macd else [1.0]
                    
                    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=row_heights, vertical_spacing=0.03)

                    # 1. Main Candle Chart
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                    
                    if show_ema:
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)
                    
                    if show_bb:
                        fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], line=dict(color='gray', width=0.5), name="BB Upper"), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], line=dict(color='gray', width=0.5), name="BB Lower"), row=1, col=1)

                    # 2. MACD Panel (Broker Style)
                    if show_macd:
                        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], line=dict(color='green', width=1), name="MACD"), row=2, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], line=dict(color='red', width=1), name="Signal"), row=2, col=1)
                        fig.add_bar(x=df.index, y=df['MACDh_12_26_9'], marker_color='gray', name="Hist", row=2, col=1)

                    fig.update_layout(template=chart_theme, height=700, xaxis_rangeslider_visible=False, showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: स्मार्ट ऑप्शन & मार्केट मूड (New)
# ==========================================
with tab2:
    st.header("🎯 ऑप्शन चेन & मार्केट मूड")
    if st.button("एनालिसिस करें 🎲", key="opt"):
        try:
            df = yf.Ticker(symbol).history(period="5d", interval="5m")
            if df.empty: st.error("No Data")
            else:
                spot = df['Close'].iloc[-1]
                gap = 100 if "BANK" in symbol else 50
                atm = round(spot / gap) * gap
                
                # --- MARKET MOOD METER (RSI Based) ---
                rsi = df.ta.rsi(length=14).iloc[-1]
                mood = "Neutral"
                mood_col = "orange"
                if rsi > 60: 
                    mood = "SUPER BULLISH (तेजी)"
                    mood_col = "green"
                elif rsi < 40: 
                    mood = "SUPER BEARISH (मंदी)"
                    mood_col = "red"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div style="padding:15px; background-color:{card_bg}; border-left: 5px solid {mood_col}; border-radius:5px;">
                        <h4>📢 Market Mood</h4>
                        <h2 style="color:{mood_col};">{mood}</h2>
                        <p>RSI Strength: {rsi:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    rec = "CALL (CE)" if rsi > 50 else "PUT (PE)"
                    buy_price = spot * 0.005 + 10 # Estimated
                    st.markdown(f"""
                    <div style="padding:15px; background-color:{card_bg}; border-left: 5px solid {mood_col}; border-radius:5px;">
                        <h4>🎯 Strike Selection</h4>
                        <h2>{atm} {rec}</h2>
                        <p>Buy Above: ₹{buy_price:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.info("💡 **Tip:** अगर Mood 'Super Bullish' है तो Put के बारे में सोचें भी मत। सिर्फ Call के मौके ढूँढें।")

        except: st.error("Error")

# ==========================================
# TAB 3: 32 कैंडलस्टिक लाइब्रेरी (Images + Hindi)
# ==========================================
with tab3:
    st.header("📚 32 महत्वपूर्ण कैंडलस्टिक पैटर्न (हिंदी में)")
    st.markdown("ट्रेडिंग में ये 32 कैंडल्स सबसे ज्यादा काम आती हैं। इन्हें पहचानें:")

    # 32 Candles Database
    candles = [
        {"name": "Hammer (हथौड़ा)", "type": "Bullish", "desc": "गिरावट के बाद बनता है। नीचे से रिजेक्शन मिलता है। तेजी का संकेत।"},
        {"name": "Inverted Hammer", "type": "Bullish", "desc": "उल्टा हथौड़ा। डाउनट्रेंड के नीचे बनता है। बायर्स एक्टिव हो रहे हैं।"},
        {"name": "Bullish Engulfing", "type": "Strong Buy", "desc": "छोटी लाल कैंडल को बड़ी हरी कैंडल पूरा खा जाती है।"},
        {"name": "Piercing Line", "type": "Bullish", "desc": "लाल कैंडल के बाद हरी कैंडल जो उसके 50% के ऊपर बंद हो।"},
        {"name": "Morning Star", "type": "Bullish Reversal", "desc": "3 कैंडल का सेट: लाल, छोटी, फिर हरी। यह बॉटम बनने का पक्का सबूत है।"},
        {"name": "Three White Soldiers", "type": "Strong Bullish", "desc": "लगातार 3 हरी कैंडल्स। बहुत मजबूत अपट्रेंड।"},
        {"name": "Bullish Harami", "type": "Bullish", "desc": "बड़ी लाल कैंडल के अंदर छोटी हरी कैंडल (गर्भवती महिला जैसा)।"},
        {"name": "Tweezer Bottom", "type": "Bullish", "desc": "दो कैंडल्स जिनका Low बिल्कुल समान हो। सपोर्ट मिल गया है।"},
        {"name": "Marubozu Green", "type": "Super Bullish", "desc": "बिना डंडी की बड़ी हरी कैंडल। एकतरफा खरीदारी।"},
        {"name": "Dragonfly Doji", "type": "Bullish", "desc": "'T' जैसा दिखता है। गिरावट खत्म होने वाली है।"},
        
        {"name": "Shooting Star", "type": "Bearish", "desc": "तेजी के बाद ऊपर बनता है। ऊपर से रिजेक्शन (बिकवाली) आई है।"},
        {"name": "Hanging Man", "type": "Bearish", "desc": "अपट्रेंड के ऊपर हथौड़ा जैसा। यह खतरे की घंटी है, मार्केट गिरेगा।"},
        {"name": "Bearish Engulfing", "type": "Strong Sell", "desc": "छोटी हरी कैंडल को बड़ी लाल कैंडल पूरा खा जाती है।"},
        {"name": "Dark Cloud Cover", "type": "Bearish", "desc": "हरी कैंडल के बाद लाल कैंडल जो उसके 50% के नीचे बंद हो।"},
        {"name": "Evening Star", "type": "Bearish Reversal", "desc": "3 कैंडल: हरी, छोटी, फिर लाल। टॉप बनने का संकेत।"},
        {"name": "Three Black Crows", "type": "Strong Bearish", "desc": "लगातार 3 लाल कैंडल्स। बहुत मजबूत डाउनट्रेंड।"},
        {"name": "Bearish Harami", "type": "Bearish", "desc": "बड़ी हरी कैंडल के अंदर छोटी लाल कैंडल।"},
        {"name": "Tweezer Top", "type": "Bearish", "desc": "दो कैंडल्स जिनका High बिल्कुल समान हो। रेजिस्टेंस बन गया है।"},
        {"name": "Marubozu Red", "type": "Super Bearish", "desc": "बिना डंडी की बड़ी लाल कैंडल। एकतरफा बिकवाली।"},
        {"name": "Gravestone Doji", "type": "Bearish", "desc": "उल्टा 'T' जैसा। तेजी खत्म होने वाली है।"},

        {"name": "Doji (Standard)", "type": "Neutral", "desc": "जहाँ खुला वहीं बंद हुआ। मार्केट कन्फ्यूज है।"},
        {"name": "Spinning Top", "type": "Neutral", "desc": "लट्टू जैसा। छोटी बॉडी, दोनों तरफ डंडी।"},
        {"name": "High Wave", "type": "Volatile", "desc": "बहुत लंबी डंडियां और छोटी बॉडी। मार्केट में हलचल है पर दिशा नहीं।"},
        {"name": "Falling Three Methods", "type": "Continuation (Bearish)", "desc": "एक बड़ी लाल, फिर 3 छोटी हरी, फिर बड़ी लाल। गिरावट जारी रहेगी।"},
        {"name": "Rising Three Methods", "type": "Continuation (Bullish)", "desc": "एक बड़ी हरी, फिर 3 छोटी लाल, फिर बड़ी हरी। तेजी जारी रहेगी।"},
        {"name": "Tasuki Gap Up", "type": "Bullish", "desc": "गैप के साथ खुलने के बाद भी मार्केट ऊपर जाए।"},
        {"name": "Tasuki Gap Down", "type": "Bearish", "desc": "गैप के साथ नीचे खुलने के बाद और नीचे जाए।"},
        {"name": "Mat Hold", "type": "Bullish", "desc": "बड़ी हरी कैंडल के बाद छोटी गिरावट, फिर ब्रेकआउट।"},
        {"name": "On Neck Line", "type": "Bearish", "desc": "गिरावट में एक छोटी हरी कैंडल जो पिछली लाल के लो पर बंद हो।"},
        {"name": "Long Legged Doji", "type": "Indecision", "desc": "बहुत लंबी डंडियां। बायर्स और सेलर्स की बराबर लड़ाई।"},
        {"name": "Abandoned Baby (Top)", "type": "Reversal", "desc": "गैप के साथ बना डोजी जो वापिस नीचे गैप से गिरे।"},
        {"name": "Abandoned Baby (Bottom)", "type": "Reversal", "desc": "नीचे गैप के साथ बना डोजी जो वापिस ऊपर गैप से उठे।"}
    ]

    # ग्रिड लेआउट (Grid Layout)
    cols = st.columns(3)
    for i, c in enumerate(candles):
        color = "green" if "Bullish" in c['type'] or "Buy" in c['type'] else "red" if "Bearish" in c['type'] or "Sell" in c['type'] else "orange"
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:10px; margin-bottom:10px; border-radius:10px; background-color:{card_bg};">
                <h4 style="margin:0;">{c['name']}</h4>
                <span style="color:{color}; font-weight:bold;">{c['type']}</span>
                <hr style="margin:5px 0;">
                <p style="font-size:13px;">{c['desc']}</p>
                <div style="text-align:center; font-size:40px;">{'📈' if color=='green' else '📉' if color=='red' else '⚖️'}</div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# TAB 4: AI
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("सवाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            res = model.generate_content(prompt)
            st.chat_message("assistant").markdown(res.text)
        except: st.error("AI Busy")
