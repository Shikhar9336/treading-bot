import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

# --- पेज की सेटिंग ---
st.set_page_config(page_title="AI Trading Bot", page_icon="📈", layout="centered")

st.title("📈 AI शेयर मार्केट असिस्टेंट")
st.markdown("यह बॉट निफ्टी, बैंक निफ्टी और स्टॉक्स का लाइव एनालिसिस करता है।")
st.markdown("---")

# --- साइडबार ---
st.sidebar.header("⚙️ सेटिंग्स")
option = st.sidebar.selectbox(
    "आप क्या चेक करना चाहते हैं?",
    ("NIFTY 50", "BANK NIFTY", "SENSEX", "Custom Stock")
)

symbol = ""
if option == "NIFTY 50":
    symbol = "^NSEI"
elif option == "BANK NIFTY":
    symbol = "^NSEBANK"
elif option == "SENSEX":
    symbol = "^BSESN"
else:
    user_input = st.sidebar.text_input("शेयर का सिंबल लिखें (जैसे RELIANCE.NS)", "RELIANCE.NS")
    symbol = user_input.upper()

# --- बटन और मुख्य काम ---
if st.sidebar.button("मार्केट चेक करें 🚀"):
    with st.spinner(f'{option} का डेटा निकाला जा रहा है...'):
        try:
            # --- सुधार: डेटा लाने का सुरक्षित तरीका ---
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")

            if df.empty:
                st.error("❌ डेटा नहीं मिला! कृपया सिंबल सही लिखें (भारतीय शेयर के अंत में .NS लगाएं)")
            else:
                # इंडिकेटर गणना
                df['EMA_9'] = df.ta.ema(length=9)
                df['EMA_21'] = df.ta.ema(length=21)
                df['RSI'] = df.ta.rsi(length=14)
                
                # ATR calculation fix
                # कभी-कभी ATR में दिक्कत आती है, इसलिए basic calculation
                df['ATR'] = df.ta.atr(length=14)
                
                # आखिरी डेटा
                current = df.iloc[-1]
                previous = df.iloc[-2]
                
                current_price = float(current['Close'])
                
                # ATR वैल्यू सुरक्षित तरीके से निकालें
                atr_value = 0
                if 'ATR' in df.columns and not pd.isna(current['ATR']):
                    atr_value = float(current['ATR'])
                else:
                    atr_value = current_price * 0.01 # डिफॉल्ट 1% अगर ATR न मिले

                # --- लॉजिक ---
                signal = "HOLD (इंतजार करें) ⏸️"
                reason = "मार्केट साइडवेज है या कोई साफ सिग्नल नहीं है।"
                color = "blue"

                # Buy Condition
                if current['EMA_9'] > current['EMA_21'] and previous['EMA_9'] <= previous['EMA_21']:
                    signal = "BUY / CALL (खरीदें) 🟢"
                    reason = "Golden Crossover: ट्रेंड ऊपर की तरफ शुरू हुआ है।"
                    color = "green"
                # Sell Condition
                elif current['EMA_9'] < current['EMA_21'] and previous['EMA_9'] >= previous['EMA_21']:
                    signal = "SELL / PUT (बेचें) 🔴"
                    reason = "Death Crossover: ट्रेंड नीचे की तरफ शुरू हुआ है।"
                    color = "red"
                # RSI Condition
                elif current['RSI'] < 30:
                    signal = "BUY (Oversold) 🟢"
                    reason = "RSI 30 से नीचे है, बाउंस आ सकता है।"
                    color = "green"
                elif current['RSI'] > 75:
                    signal = "SELL (Overbought) 🔴"
                    reason = "RSI 75 से ऊपर है, गिरावट आ सकती है।"
                    color = "red"

                # --- स्टॉप लॉस और टारगेट ---
                sl = 0
                tgt = 0
                if "BUY" in signal:
                    sl = current_price - (atr_value * 1.5)
                    tgt = current_price + (atr_value * 3)
                elif "SELL" in signal:
                    sl = current_price + (atr_value * 1.5)
                    tgt = current_price - (atr_value * 3)

                # --- रिजल्ट दिखाना ---
                st.header(f"{option} रिपोर्ट")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="अभी का भाव (CMP)", value=f"₹{current_price:.2f}")
                with col2:
                    st.metric(label="RSI इंडिकेटर", value=f"{current['RSI']:.2f}")

                st.subheader("🤖 AI फैसला:")
                if color == "green":
                    st.success(f"## {signal}")
                elif color == "red":
                    st.error(f"## {signal}")
                else:
                    st.info(f"## {signal}")

                st.write(f"**कारण:** {reason}")

                if "HOLD" not in signal:
                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"🛑 **Stop Loss:** ₹{sl:.2f}")
                    with c2:
                        st.write(f"🎯 **Target:** ₹{tgt:.2f}")

                st.markdown("---")
                st.caption("⚠️ डिस्क्लेमर: यह केवल एक एआई टूल है। कृपया अपने जोखिम पर ट्रेड करें।")

        except Exception as e:
            st.error(f"कुछ तकनीकी दिक्कत आई: {e}")

else:
    st.info("👈 साइडबार से ऑप्शन चुनें और 'मार्केट चेक करें' बटन दबाएं।")
