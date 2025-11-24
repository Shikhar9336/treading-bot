import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import math

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Option Master", page_icon="🚀", layout="wide")

# ==========================================
# 🔑 API KEY & AI SETUP (FIXED)
# ==========================================
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"

try:
    genai.configure(api_key=api_key)
    # यहाँ हमने मॉडल बदलकर 'flash' कर दिया है जो कभी Busy नहीं होता
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"AI Setup Error: {e}")

# --- साइडबार ---
with st.sidebar:
    st.header("👤 ट्रेडर प्रोफाइल")
    st.info("नाम: शिखर तिवारी")
    st.success("✅ AI Fixed & Smart Options")
    st.markdown("---")

st.title("📈 शिखर तिवारी - मास्टर ट्रेडिंग बॉट")
st.markdown("### 🚀 Live Signals, Option Chain & AI Expert")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट (F&O)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
if market_cat == "🇮🇳 इंडियन मार्केट (F&O)":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "FINNIFTY", "RELIANCE", "TATA MOTORS", "HDFC BANK"))
    if "NIFTY" in option: symbol = "^NSEI" if "50" in option else "^NSEBANK" if "BANK" in option else "NIFTY_FIN_SERVICE.NS"
    else: symbol = f"{option.replace(' ', '')}.NS"

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

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour"))

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["🎯 स्मार्ट ऑप्शन एंट्री", "📊 लाइव चार्ट", "📚 कैंडल ज्ञान", "🤖 AI गुरुजी (Fixed)"])

# ==========================================
# TAB 1: स्मार्ट ऑप्शन एंट्री (आपका सबसे जरुरी फीचर)
# ==========================================
with tab1:
    st.header("🎯 ऑप्शन स्ट्राइक कैलकुलेटर")
    if st.button(f"{symbol} स्कैन करें 🎲", key="opt_scan"):
        with st.spinner('कैलकुलेशन चल रही है...'):
            try:
                df = yf.Ticker(symbol).history(period="5d", interval="5m")
                if df.empty: st.error("❌ डेटा नहीं मिला")
                else:
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    curr = df.iloc[-1]
                    spot_price = float(curr['Close'])
                    
                    # Trend Logic
                    trend = "SIDEWAYS"
                    if curr['EMA_9'] > curr['EMA_21']: trend = "UPTREND (Call Buy)"
                    elif curr['EMA_9'] < curr['EMA_21']: trend = "DOWNTREND (Put Buy)"

                    # Strike Logic
                    gap = 100 if "BANK" in symbol else 50
                    atm_strike = round(spot_price / gap) * gap
                    
                    # Recommendation
                    rec_type, rec_strike, color, msg = "", 0, "gray", "Wait"
                    est_premium = 0 # अनुमानित भाव
                    
                    # प्रीमियम का मोटा-मोटा अनुमान (Basic Logic)
                    # ATM options usually trade around 0.5% - 0.8% of spot price on average days
                    base_premium = spot_price * 0.006 

                    if "UPTREND" in trend:
                        rec_type = "CE (Call Option)"
                        rec_strike = atm_strike 
                        est_premium = base_premium
                        color = "green"
                        msg = "मार्केट ऊपर जा रहा है।"
                    elif "DOWNTREND" in trend:
                        rec_type = "PE (Put Option)"
                        rec_strike = atm_strike
                        est_premium = base_premium
                        color = "red"
                        msg = "मार्केट नीचे गिर रहा है।"

                    buy_above = est_premium + 5

                    # Display
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric("SPOT PRICE", f"₹{spot_price:.2f}")
                        st.info(f"ATM Strike: {atm_strike}")

                    with col2:
                        if color != "gray":
                            st.markdown(f"""
                            <div style="padding: 20px; border: 3px solid {color}; border-radius: 15px; background-color: #ffffff; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                                <h3 style="color: {color}; margin:0;">सिफारिश: {rec_type}</h3>
                                <h1 style="color: #333; margin: 10px 0;">STRIKE: {rec_strike}</h1>
                                <hr>
                                <h2 style="color: {color};">👉 BUY ABOVE: ₹{buy_above:.2f}</h2>
                                <div style="display:flex; justify-content:space-around; margin-top:10px; color:#555;">
                                    <span>🛑 SL: ₹{buy_above*0.85:.2f}</span>
                                    <span>🎯 TGT: ₹{buy_above*1.3:.2f}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.success(f"💡 **कारण:** {msg} (प्रीमियम एक अनुमान है, चार्ट देखकर ट्रेड लें)")
                        else:
                            st.warning("⚠️ मार्केट साइडवेज है। नो ट्रेड जोन।")

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: लाइव चार्ट (Angel One Style)
# ==========================================
with tab2:
    if st.button("चार्ट देखें 📉", key="chart_btn"):
        try:
            p, i = ("1y", "1d")
            if "1 Minute" in timeframe: p, i = "5d", "1m"
            elif "5 Minutes" in timeframe: p, i = "5d", "5m"
            elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
            
            df = yf.Ticker(symbol).history(period=p, interval=i)
            
            # Chart Logic
            df['EMA_9'] = df.ta.ema(length=9)
            df['EMA_21'] = df.ta.ema(length=21)
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
            # Candles
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'), row=1, col=1)
            # EMAs
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange', width=1), name="EMA 9"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue', width=1), name="EMA 21"), row=1, col=1)
            # Volume
            colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)
            
            fig.update_layout(height=600, paper_bgcolor='white', plot_bgcolor='white', xaxis_rangeslider_visible=False, showlegend=False, title=f"{symbol} Chart")
            fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0'); fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
            st.plotly_chart(fig, use_container_width=True)
        except: st.error("Chart Load Error")

# ==========================================
# TAB 3: कैंडल ज्ञान (HINDI)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक ज्ञान")
    st.info("Hammer 🔨 = तेजी | Shooting Star 🌠 = मंदी | Engulfing 📈 = बड़ा मूव")

# ==========================================
# TAB 4: AI गुरुजी (FIXED)
# ==========================================
with tab4:
    st.header("🤖 AI गुरुजी")
    st.caption("अब आप मार्केट के बारे में कुछ भी पूछ सकते हैं। (Powered by Gemini 1.5 Flash)")
    
    if prompt := st.chat_input("सवाल पूछें (जैसे: Tata Motors का टारगेट क्या है?)..."):
        st.chat_message("user").markdown(prompt)
        
        try:
            # अब यहाँ असली एरर दिखेगा अगर आया तो
            with st.chat_message("assistant"):
                with st.spinner("AI सोच रहा है..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
        except Exception as e:
            st.error(f"तकनीकी खराबी: {e}")
            st.warning("टिप: अगर यह बार-बार हो रहा है, तो शायद Google ने फ्री लिमिट रोक दी है।")
