import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import math
from datetime import datetime

# --- पेज सेटिंग ---
st.set_page_config(page_title="Shikhar Pro Trader", page_icon="🎯", layout="wide")

# 🔑 API KEY
api_key = "AIzaSyDKx2IgsHmnCDYm7IDqUXzr9Yfu9yuFgls"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except: pass

# --- साइडबार ---
with st.sidebar:
    st.header("👤 यूजर प्रोफाइल")
    st.info("नाम: शिखर तिवारी")
    st.success("Mode: Smart Option Chain")
    st.markdown("---")

st.title("📈 शिखर तिवारी - मास्टर ऑप्शन बॉट")
st.markdown("### 🚀 Exact Strike Price & Entry Levels")

# ==========================================
# ⚙️ मार्केट सिलेक्शन
# ==========================================
st.sidebar.header("🔍 मार्केट चुनें")
market_cat = st.sidebar.radio("सेगमेंट:", ("🇮🇳 इंडियन मार्केट (Options)", "💱 फॉरेक्स & गोल्ड", "🇺🇸 ग्लोबल मार्केट", "₿ क्रिप्टो"))

symbol = ""
is_index = False

if market_cat == "🇮🇳 इंडियन मार्केट (Options)":
    option = st.sidebar.selectbox("इंडेक्स/स्टॉक:", ("NIFTY 50", "BANK NIFTY", "FINNIFTY", "RELIANCE", "TATA MOTORS", "SBIN"))
    if "NIFTY" in option:
        symbol = "^NSEI" if "50" in option else "^NSEBANK" if "BANK" in option else "NIFTY_FIN_SERVICE.NS"
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

timeframe = st.sidebar.selectbox("टाइमफ्रेम:", ("1 Minute", "5 Minutes", "15 Minutes", "1 Hour"))

# --- प्रीमियम कैलकुलेटर (Maths) ---
def calculate_premium(spot, strike, days_left, type="CE"):
    # यह एक बेसिक अनुमान (Estimation) है
    intrinsic = 0
    if type == "CE": intrinsic = max(0, spot - strike)
    else: intrinsic = max(0, strike - spot)
    
    time_value = (spot * 0.002) * days_left # Time decay estimation
    return intrinsic + time_value

# --- टैब्स ---
tab1, tab2, tab3, tab4 = st.tabs(["🎯 स्मार्ट ऑप्शन एंट्री", "📊 लाइव चार्ट", "📚 कैंडल ज्ञान", "🤖 AI गुरुजी"])

# ==========================================
# TAB 1: स्मार्ट ऑप्शन एंट्री (आपका सवाल यहाँ हल होगा)
# ==========================================
with tab1:
    st.header("🎯 ऑप्शन चेन: सटीक एंट्री प्लान")
    st.caption("यह टूल मार्केट ट्रेंड देखकर बताता है कि कौन सा स्ट्राइक खरीदना है और कितने पर।")

    if st.button(f"{symbol} स्कैन करें 🎲", key="opt_scan"):
        with st.spinner('मार्केट ट्रेंड और स्ट्राइक प्राइस कैलकुलेट हो रहा है...'):
            try:
                # 1. डेटा लाओ
                df = yf.Ticker(symbol).history(period="5d", interval="5m")
                
                if df.empty:
                    st.error("❌ डेटा नहीं मिला")
                else:
                    # 2. ट्रेंड पहचानो
                    df['EMA_9'] = df.ta.ema(length=9)
                    df['EMA_21'] = df.ta.ema(length=21)
                    
                    curr = df.iloc[-1]
                    spot_price = float(curr['Close'])
                    
                    trend = "SIDEWAYS"
                    if curr['EMA_9'] > curr['EMA_21']: trend = "UPTREND (Call Buy)"
                    elif curr['EMA_9'] < curr['EMA_21']: trend = "DOWNTREND (Put Buy)"

                    # 3. सही स्ट्राइक प्राइस चुनना (50/100 Gap Logic)
                    gap = 100 if "BANK" in symbol else 50
                    atm_strike = round(spot_price / gap) * gap
                    
                    # 4. फैसला (Decision Making)
                    rec_type = ""
                    rec_strike = 0
                    
                    if "UPTREND" in trend:
                        rec_type = "CE (Call Option)"
                        rec_strike = atm_strike # ATM लेते हैं
                        premium = calculate_premium(spot_price, rec_strike, 4, "CE") # Approx 4 days expiry
                        entry_price = premium + 5 # 5 रुपये ऊपर एंट्री
                        color = "green"
                        msg = "बाजार ऊपर जा रहा है।"
                    elif "DOWNTREND" in trend:
                        rec_type = "PE (Put Option)"
                        rec_strike = atm_strike
                        premium = calculate_premium(spot_price, rec_strike, 4, "PE")
                        entry_price = premium + 5
                        color = "red"
                        msg = "बाजार नीचे गिर रहा है।"
                    else:
                        color = "gray"
                        msg = "बाजार रुका हुआ है, कोई ट्रेड न लें।"

                    # --- रिजल्ट दिखाओ ---
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.metric("SPOT PRICE (अभी का भाव)", f"₹{spot_price:.2f}")
                        st.info(f"ATM Strike: {atm_strike}")

                    with col2:
                        if color != "gray":
                            st.markdown(f"""
                            <div style="padding: 20px; border: 3px solid {color}; border-radius: 15px; background-color: #ffffff; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                                <h3 style="color: {color}; margin:0;">सिफारिश: {rec_type}</h3>
                                <h1 style="color: #333; margin: 10px 0;">STRIKE: {rec_strike}</h1>
                                <hr>
                                <h2 style="color: {color};">👉 BUY ABOVE: ₹{entry_price:.2f}</h2>
                                <div style="display:flex; justify-content:space-around; margin-top:10px; color:#555;">
                                    <span>🛑 SL: ₹{entry_price*0.9:.2f}</span>
                                    <span>🎯 Target: ₹{entry_price*1.2:.2f}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.success(f"💡 **कारण:** {msg} आप {rec_strike} का लॉट तब खरीदें जब उसका भाव **₹{entry_price:.2f}** को पार करे।")
                        else:
                            st.warning("⚠️ मार्केट अभी साइडवेज है। ऑप्शन में पैसा डूब सकता है। कृपया ट्रेड न लें।")

                    st.markdown("---")
                    st.markdown("### 📊 Option Chain (Table)")
                    
                    # डमी टेबल (Data Visualization के लिए)
                    strikes = [atm_strike-gap, atm_strike, atm_strike+gap]
                    table_data = []
                    for k in strikes:
                        c_p = calculate_premium(spot_price, k, 4, "CE")
                        p_p = calculate_premium(spot_price, k, 4, "PE")
                        status = "👈 ATM" if k == atm_strike else ""
                        table_data.append({"CALL Price (Est)": f"₹{c_p:.2f}", "STRIKE PRICE": f"{k} {status}", "PUT Price (Est)": f"₹{p_p:.2f}"})
                    
                    st.table(pd.DataFrame(table_data))

            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# TAB 2: लाइव चार्ट
# ==========================================
with tab2:
    if st.button("चार्ट रिफ्रेश करें 📉", key="chart_btn"):
        try:
            p, i = ("1y", "1d")
            if "1 Minute" in timeframe: p, i = "5d", "1m"
            elif "5 Minutes" in timeframe: p, i = "5d", "5m"
            elif "15 Minutes" in timeframe: p, i = "1mo", "15m"
            
            df = yf.Ticker(symbol).history(period=p, interval=i)
            if df.empty: st.error("No Data")
            else:
                # Chart Logic
                df['EMA_9'] = df.ta.ema(length=9)
                df['EMA_21'] = df.ta.ema(length=21)
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", increasing_line_color='#008F4C', decreasing_line_color='#D32F2F'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], line=dict(color='orange'), name="EMA 9"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], line=dict(color='blue'), name="EMA 21"), row=1, col=1)
                
                # Volume
                colors = ['#D32F2F' if c < o else '#008F4C' for c, o in zip(df['Close'], df['Open'])]
                fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)
                
                fig.update_layout(height=600, paper_bgcolor='white', plot_bgcolor='white', xaxis_rangeslider_visible=False, showlegend=False, title=f"{symbol} Chart")
                fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0'); fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Chart Load Error")

# ==========================================
# TAB 3: कैंडल ज्ञान (Same)
# ==========================================
with tab3:
    st.header("📚 कैंडलस्टिक ज्ञान")
    st.info("Hammer 🔨 = तेजी | Shooting Star 🌠 = मंदी | Engulfing 📈 = बड़ा मूव")

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
        except: st.error("AI Busy")
