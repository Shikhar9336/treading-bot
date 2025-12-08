import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import math

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Ultimate Trader", page_icon="📈", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except: pass

# --- परमानेंट लाइट मोड (Angel One Style) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: black; }
    .stMarkdown, h1, h2, h3, p, label { color: black !important; }
    .stMetric { background-color: #f0f2f6 !important; border: 1px solid #ddd; }
    div[data-testid="stSidebar"] { background-color: #f8f9fa; }
</style>
""", unsafe_allow_html=True)

# --- साइडबार: रिस्क कैलकुलेटर (User Request) ---
with st.sidebar:
    st.header("👤 ट्रेडर: शिखर तिवारी")
    
    with st.expander("🧮 रिस्क कैलकुलेटर (जरूरी)", expanded=True):
        capital = st.number_input("पूंजी (Capital ₹):", value=20000)
        risk_pct = st.slider("रिस्क प्रति ट्रेड (%):", 1, 10, 2)
        entry = st.number_input("एंट्री प्राइस:", value=100.0)
        sl = st.number_input("स्टॉप लॉस:", value=95.0)
        
        if entry > sl:
            risk_amt = capital * (risk_pct / 100)
            loss_per_share = entry - sl
            qty = math.floor(risk_amt / loss_per_share)
            st.success(f"✅ केवल **{qty}** शेयर खरीदें")
            st.error(f"अधिकतम नुकसान: ₹{risk_amt:.0f}")
    
    st.markdown("---")

st.title("📈 शिखर तिवारी - मास्टर ट्रेडिंग टर्मिनल")

# ==========================================
# ⚙️ मार्केट और टाइमफ्रेम (1 Min Added)
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    market_cat = st.selectbox("मार्केट:", ("🇮🇳 इंडियन मार्केट (F&O)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

with col2:
    symbol = ""
    is_opt = False
    if "इंडियन" in market_cat:
        opt = st.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "FINNIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK", "SBIN", "ADANI ENT"))
        if "NIFTY 50" in opt: symbol = "^NSEI"; is_opt=True
        elif "BANK" in opt: symbol = "^NSEBANK"; is_opt=True
        elif "FIN" in opt: symbol = "NIFTY_FIN_SERVICE.NS"; is_opt=True
        else: symbol = f"{opt.replace(' ', '')}.NS"
    elif "फॉरेक्स" in market_cat:
        opt = st.selectbox("पेयर:", ("GOLD (XAU/USD)", "SILVER", "GBP/USD", "EUR/USD", "USD/JPY", "CRUDE OIL"))
        symbol = "GC=F" if "GOLD" in opt else "SI=F" if "SILVER" in opt else "GBPUSD=X" if "GBP" in opt else "EURUSD=X" if "EUR" in opt else "JPY=X" if "JPY" in opt else "CL=F"
    elif "ग्लोबल" in market_cat:
        symbol = "^IXIC"
    else:
        symbol = "BTC-USD"

with col3:
    # टाइमफ्रेम में 1 मिनट जोड़ दिया गया है
    timeframe = st.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "30 Minutes", "1 Hour", "1 Day", "1 Week", "1 Month"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 प्रो चार्ट (Fixed)", "🎯 ऑप्शन चेन (Hindi)", "🕯️ 32 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: प्रो चार्ट (Bollinger Error Fixed)
# ==========================================
with tab1:
    if st.button(f"{symbol} चार्ट देखें 🚀"):
        with st.spinner('चार्ट और इंडिकेटर लोड हो रहे हैं...'):
            try:
                # --- टाइमफ्रेम लॉजिक (1 Minute Fix) ---
                # 1 मिनट का डेटा 1 साल का नहीं मिलता, इसलिए इसे 5 दिन (5d) किया है
                if "1 Minute" in timeframe: p, i = "5d", "1m"
                elif "5 Minutes" in timeframe: p, i = "5d", "5m"
                elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
                elif "30 Minutes" in timeframe: p, i = "1mo", "30m"
                elif "1 Hour" in timeframe: p, i = "1y", "1h"
                elif "1 Week" in timeframe: p, i = "2y", "1wk"
                elif "1 Month" in timeframe: p, i = "5y", "1mo"
                else: p, i = "1y", "1d"

                df = yf.Ticker(symbol).history(period=p, interval=i)
                
                if df.empty: st.error("❌ डेटा नहीं मिला (मार्केट बंद हो सकता है)")
                else:
                    # इंडिकेटर्स
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    df['RSI'] = df.ta.rsi(length=14)
                    df['ATR'] = df.ta.atr(length=14)
                    
                    # Bollinger Bands Fix (Error Solution)
                    bb = df.ta.bbands(length=20, std=2)
                    if bb is not None:
                        df = pd.concat([df, bb], axis=1)
                        # नाम छोटा कर रहे हैं ताकि एरर न आए
                        df.rename(columns={df.columns[-3]: 'BBL', df.columns[-2]: 'BBM', df.columns[-1]: 'BBU'}, inplace=True)

                    curr = df.iloc[-1]
                    price = float(curr['Close'])
                    atr = float(curr['ATR']) if 'ATR' in df.columns and not pd.isna(curr['ATR']) else price * 0.01

                    # सिग्नल लॉजिक
                    action = "WAIT (रुको)"
                    color = "#2962ff"
                    sl, tgt = 0.0, 0.0

                    if curr['EMA_9'] > curr['EMA_21']:
                        action = "BUY / CALL 🟢"
                        color = "#008F4C"
                        sl = price - (atr * 1.5)
                        tgt = price + (atr * 3.0)
                    elif curr['EMA_9'] < curr['EMA_21']:
                        action = "SELL / PUT 🔴"
                        color = "#D32F2F"
                        sl = price + (atr * 1.5)
                        tgt = price - (atr * 3.0)

                    # --- 1. सिग्नल कार्ड ---
                    st.markdown(f"""
                    <div style="padding: 15px; border: 2px solid {color}; border-radius: 10px; background-color: #ffffff; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <h1 style="color: {color}; margin:0;">{action}</h1>
                        <h2 style="color: #333; margin:5px;">LTP: {price:.2f}</h2>
                        <div style="display: flex; justify-content: space-around; color: #555; font-size: 18px;">
                            <span>🛑 SL: <b>{sl:.2f}</b></span>
                            <span>🎯 TGT: <b>{tgt:.2f}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # --- 2. चार्ट (Angel One Style) ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
                    
                    # Candlestick
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'), row=1, col=1)
                    
                    # EMAs
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)
                    
                    # Bollinger Bands (Safe Mode)
                    if 'BBU' in df.columns:
                        fig.add_trace(go.Scatter(x=df.index, y=df['BBU'], line=dict(color='gray', width=0.5), showlegend=False), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['BBL'], line=dict(color='gray', width=0.5), fill='tonexty', fillcolor='rgba(0,0,0,0.05)', name="BB"), row=1, col=1)
                    
                    # Volume
                    colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)
                    
                    fig.update_layout(height=650, paper_bgcolor='white', plot_bgcolor='white', xaxis_rangeslider_visible=False, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
                    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0'); fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e: st.error(f"Chart Error: {e}")

# ==========================================
# TAB 2: ऑप्शन चेन (HINDI MOOD)
# ==========================================
with tab2:
    st.header("🎯 ऑप्शन चेन और मार्केट मूड")
    
    if st.button("ऑप्शन डेटा निकालें 🎲"):
        if not is_opt: st.warning("यह केवल इंडेक्स (Nifty/BankNifty) के लिए है।")
        else:
            try:
                df = yf.Ticker(symbol).history(period="5d", interval="5m")
                spot = df['Close'].iloc[-1]
                
                # --- मार्केट मूड (हिंदी में) ---
                rsi = df.ta.rsi(length=14).iloc[-1]
                mood = "सामान्य (Neutral)"
                col = "orange"
                msg = "बाजार अभी दिशा ढूंढ रहा है। सावधानी से ट्रेड करें।"

                if rsi > 60: 
                    mood = "तेजी (Bullish) 🚀"
                    col = "green"
                    msg = "बाजार में खरीदार हावी हैं। कॉल (CE) खरीदने का मौका देखें।"
                elif rsi < 40: 
                    mood = "मंदी (Bearish) 🩸"
                    col = "red"
                    msg = "बाजार में बिकवाली हो रही है। पुट (PE) खरीदने का मौका देखें।"
                
                # मूड कार्ड
                st.markdown(f"""
                <div style="padding:15px; background-color:#ffffff; border-left: 10px solid {col}; border-radius:5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h3 style="margin:0; color:{col};">मार्केट मूड: {mood}</h3>
                    <p style="color:black;">RSI स्कोर: {rsi:.2f}</p>
                    <p style="color:gray;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
                st.write("")

                # --- स्ट्राइक प्राइस टेबल ---
                gap = 100 if "BANK" in symbol else 50
                atm = round(spot / gap) * gap
                
                strikes = [atm-gap*2, atm-gap, atm, atm+gap, atm+gap*2]
                data = []
                for k in strikes:
                    diff = spot - k
                    ce_p = max(0, diff) + (spot*0.005) + (abs(diff)*0.1 if diff<0 else 0)
                    pe_p = max(0, k - spot) + (spot*0.005) + (abs(diff)*0.1 if diff>0 else 0)
                    
                    status = "⬅️ ATM (यहाँ ट्रेड करें)" if k == atm else ""
                    data.append({"CALL Price (₹)": f"{ce_p:.2f}", "STRIKE PRICE": f"{k} {status}", "PUT Price (₹)": f"{pe_p:.2f}"})
                
                st.table(pd.DataFrame(data))

            except: st.error("Data Fetch Error")

# ==========================================
# TAB 3: 32 कैंडल ज्ञान (FULL LIST)
# ==========================================
with tab3:
    st.header("📚 32 महत्वपूर्ण कैंडलस्टिक पैटर्न")
    
    # 32 Candles List
    candles = [
        {"name": "Hammer (हथौड़ा)", "type": "तेजी (Bullish)", "desc": "गिरावट के बाद बनता है। नीचे से अच्छी खरीदारी आई है।", "img": "https://a.c-dn.net/b/2w0y8E/hammer-candlestick-pattern_body_Hammer.png"},
        {"name": "Inverted Hammer", "type": "तेजी (Bullish)", "desc": "उल्टा हथौड़ा। डाउनट्रेंड में बायर्स का जोर दिखा रहा है।", "img": "https://a.c-dn.net/b/1Kj0gN/inverted-hammer-candlestick-pattern_body_InvertedHammer.png"},
        {"name": "Bullish Engulfing", "type": "मजबूत तेजी", "desc": "हरी कैंडल ने पिछली लाल कैंडल को पूरा ढक लिया।", "img": "https://a.c-dn.net/b/0Yk6A8/engulfing-candle-trading-strategy_body_bullishengulfing.png"},
        {"name": "Piercing Line", "type": "तेजी (Bullish)", "desc": "लाल कैंडल के बाद हरी कैंडल, जो उसके 50% के ऊपर बंद हो।", "img": "https://www.dailyfx.com/images/2020/06/17/Piercing-Line-Candlestick.png"},
        {"name": "Morning Star", "type": "तेजी (Reversal)", "desc": "3 कैंडल: लाल, छोटी, फिर हरी। यह बॉटम (Support) बनने का पक्का सबूत है।", "img": "https://a.c-dn.net/b/4h3S1p/morning-star-candlestick_body_MorningStarPattern.png"},
        {"name": "Three White Soldiers", "type": "मजबूत तेजी", "desc": "लगातार 3 हरी कैंडल्स। बहुत मजबूत अपट्रेंड।", "img": "https://www.dailyfx.com/images/2020/06/17/Three-White-Soldiers.png"},
        {"name": "Bullish Harami", "type": "तेजी (Bullish)", "desc": "बड़ी लाल कैंडल के पेट (अंदर) में छोटी हरी कैंडल।", "img": "https://www.dailyfx.com/images/2020/06/17/Bullish-Harami.png"},
        {"name": "Tweezer Bottom", "type": "तेजी (Bullish)", "desc": "दो कैंडल्स जिनका Low बिल्कुल समान हो। सपोर्ट मिल गया है।", "img": "https://www.dailyfx.com/images/2020/06/17/Tweezer-Bottoms.png"},
        {"name": "Marubozu Green", "type": "सुपर तेजी", "desc": "बिना डंडी की बड़ी हरी कैंडल। खरीदार बहुत आक्रामक हैं।", "img": "https://a.c-dn.net/b/0Yk6A8/engulfing-candle-trading-strategy_body_bullishengulfing.png"},
        {"name": "Dragonfly Doji", "type": "तेजी (Bullish)", "desc": "'T' जैसा दिखता है। गिरावट खत्म होने वाली है।", "img": "https://a.c-dn.net/b/1f20Vj/what-is-a-doji-candle_body_DragonflyDoji.png"},
        
        {"name": "Shooting Star", "type": "मंदी (Bearish)", "desc": "तेजी के बाद ऊपर बनता है। ऊपर से बिकवाली आई है।", "img": "https://a.c-dn.net/b/2E7F4m/shooting-star-candlestick-pattern_body_shootingstarcandlestickpattern.png"},
        {"name": "Hanging Man", "type": "मंदी (Bearish)", "desc": "ऊपर जाते मार्केट में हथौड़ा। यह खतरे की घंटी है, मार्केट गिरेगा।", "img": "https://www.dailyfx.com/images/2020/06/17/Hanging-Man.png"},
        {"name": "Bearish Engulfing", "type": "मजबूत मंदी", "desc": "लाल कैंडल ने पिछली हरी कैंडल को पूरा ढक लिया।", "img": "https://a.c-dn.net/b/1L0z6y/engulfing-candle-trading-strategy_body_bearishengulfing.png"},
        {"name": "Dark Cloud Cover", "type": "मंदी (Bearish)", "desc": "हरी कैंडल के बाद लाल कैंडल जो उसके 50% के नीचे बंद हो।", "img": "https://www.dailyfx.com/images/2020/06/17/Dark-Cloud-Cover.png"},
        {"name": "Evening Star", "type": "मंदी (Reversal)", "desc": "3 कैंडल: हरी, छोटी, फिर लाल। टॉप (Resistance) बनने का सबूत।", "img": "https://a.c-dn.net/b/1Kj0gN/inverted-hammer-candlestick-pattern_body_EveningStar.png"},
        {"name": "Three Black Crows", "type": "मजबूत मंदी", "desc": "लगातार 3 लाल कैंडल्स। बहुत मजबूत डाउनट्रेंड।", "img": "https://www.dailyfx.com/images/2020/06/17/Three-Black-Crows.png"},
        {"name": "Bearish Harami", "type": "मंदी (Bearish)", "desc": "बड़ी हरी कैंडल के पेट (अंदर) में छोटी लाल कैंडल।", "img": "https://www.dailyfx.com/images/2020/06/17/Bearish-Harami.png"},
        {"name": "Tweezer Top", "type": "मंदी (Bearish)", "desc": "दो कैंडल्स जिनका High बिल्कुल समान हो। रेजिस्टेंस बन गया है।", "img": "https://www.dailyfx.com/images/2020/06/17/Tweezer-Tops.png"},
        {"name": "Marubozu Red", "type": "सुपर मंदी", "desc": "बिना डंडी की बड़ी लाल कैंडल। सेलर्स बहुत आक्रामक हैं।", "img": "https://a.c-dn.net/b/1L0z6y/engulfing-candle-trading-strategy_body_bearishengulfing.png"},
        {"name": "Gravestone Doji", "type": "मंदी (Bearish)", "desc": "उल्टा 'T' जैसा। तेजी खत्म होने वाली है।", "img": "https://a.c-dn.net/b/1f20Vj/what-is-a-doji-candle_body_DragonflyDoji.png"},

        {"name": "Doji (Standard)", "type": "न्यूट्रल", "desc": "जहाँ खुला वहीं बंद हुआ। मार्केट कन्फ्यूज है।", "img": "https://a.c-dn.net/b/1f20Vj/what-is-a-doji-candle_body_DragonflyDoji.png"},
        {"name": "Spinning Top", "type": "न्यूट्रल", "desc": "लट्टू जैसा। छोटी बॉडी, दोनों तरफ डंडी।", "img": "https://www.dailyfx.com/images/2020/06/17/Spinning-Top.png"},
        {"name": "High Wave", "type": "वोलेटाइल", "desc": "लंबी डंडियां, छोटी बॉडी। बाजार में हलचल है पर दिशा नहीं।", "img": "https://www.dailyfx.com/images/2020/06/17/Spinning-Top.png"}, # Similar to spinning top
        {"name": "Falling Three Methods", "type": "गिरावट जारी", "desc": "एक बड़ी लाल, फिर 3 छोटी हरी, फिर बड़ी लाल। गिरावट जारी रहेगी।", "img": "https://www.dailyfx.com/images/2020/06/17/Three-Black-Crows.png"}, # Placeholder
        {"name": "Rising Three Methods", "type": "तेजी जारी", "desc": "एक बड़ी हरी, फिर 3 छोटी लाल, फिर बड़ी हरी। तेजी जारी रहेगी।", "img": "https://www.dailyfx.com/images/2020/06/17/Three-White-Soldiers.png"}, # Placeholder
        {"name": "Tasuki Gap Up", "type": "तेजी (Bullish)", "desc": "गैप के साथ खुलने के बाद भी मार्केट ऊपर जाए।", "img": "https://a.c-dn.net/b/0Yk6A8/engulfing-candle-trading-strategy_body_bullishengulfing.png"},
        {"name": "Tasuki Gap Down", "type": "मंदी (Bearish)", "desc": "गैप के साथ नीचे खुलने के बाद और नीचे जाए।", "img": "https://a.c-dn.net/b/1L0z6y/engulfing-candle-trading-strategy_body_bearishengulfing.png"},
        {"name": "Long Legged Doji", "type": "न्यूट्रल", "desc": "बहुत लंबी डंडियां। बायर्स और सेलर्स की बराबर लड़ाई।", "img": "https://a.c-dn.net/b/1f20Vj/what-is-a-doji-candle_body_DragonflyDoji.png"},
        {"name": "Abandoned Baby (Top)", "type": "रिवर्सल", "desc": "गैप के साथ बना डोजी जो वापिस नीचे गैप से गिरे।", "img": "https://a.c-dn.net/b/2E7F4m/shooting-star-candlestick-pattern_body_shootingstarcandlestickpattern.png"},
        {"name": "Abandoned Baby (Bottom)", "type": "रिवर्सल", "desc": "नीचे गैप के साथ बना डोजी जो वापिस ऊपर गैप से उठे।", "img": "https://a.c-dn.net/b/2w0y8E/hammer-candlestick-pattern_body_Hammer.png"},
        {"name": "On Neck Line", "type": "मंदी (Bearish)", "desc": "गिरावट में एक छोटी हरी कैंडल जो पिछली लाल के लो पर बंद हो।", "img": "https://a.c-dn.net/b/1L0z6y/engulfing-candle-trading-strategy_body_bearishengulfing.png"},
        {"name": "Mat Hold", "type": "तेजी (Bullish)", "desc": "बड़ी हरी कैंडल के बाद छोटी गिरावट, फिर ब्रेकआउट।", "img": "https://a.c-dn.net/b/0Yk6A8/engulfing-candle-trading-strategy_body_bullishengulfing.png"}
    ]

    cols = st.columns(3)
    for i, c in enumerate(candles):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background-color:#ffffff; padding:10px; margin-bottom:10px; border-radius:10px; border:1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h5 style="margin:0; color:#333;">{c['name']}</h5>
                <span style="color:{'green' if 'Bullish' in c['type'] or 'तेजी' in c['type'] else 'red' if 'Bearish' in c['type'] or 'मंदी' in c['type'] else 'orange'}; font-size:12px; font-weight:bold;">{c['type']}</span>
                <p style="font-size:12px; color:#555; margin-top:5px;">{c['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            try: st.image(c['img'], use_column_width=True)
            except: pass

# ==========================================
# TAB 4: AI गुरुजी
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    if prompt := st.chat_input("सवाल पूछें..."):
        st.chat_message("user").markdown(prompt)
        try:
            response = model.generate_content(prompt)
            st.chat_message("assistant").markdown(response.text)
        except Exception as e: st.error(f"Error: {e}")
