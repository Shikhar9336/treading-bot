app.pyimport streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

# --- पेज की सेटिंग (Page Config) ---
st.set_page_config(page_title="AI Trading Bot", page_icon="📈", layout="centered")

# --- हेडिंग और डिजाइन ---
st.title("📈 AI शेयर मार्केट असिस्टेंट")
st.markdown("यह बॉट निफ्टी, बैंक निफ्टी और स्टॉक्स का लाइव एनालिसिस करता है।")
st.markdown("---")

# --- साइडबार (मेन्यू) ---
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

# --- बटन ---
if st.sidebar.button("मार्केट चेक करें 🚀"):
    with st.spinner(f'{option} का डेटा निकाला जा रहा है...'):
        try:
            # डेटा डाउनलोड
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if df.empty:
                st.error("❌ डेटा नहीं मिला! कृपया सिंबल सही लिखें (भारतीय शेयर के अंत में .NS लगाएं)")
            else:
                # --- एनालिसिस (Analysis) ---
                df['EMA_9'] = df.ta.ema(length=9)
                df['EMA_21'] = df.ta.ema(length=21)
                df['RSI'] = df.ta.rsi(length=14)
                df['ATR'] = df.ta.atr(length=14)

                current = df.iloc[-1]
                previous = df.iloc[-2]
                current_price = float(current['Close'])
                atr_value = float(current['ATR']) if not pd.isna(current['ATR']) else 0

                # --- लॉजिक ---
                signal = "HOLD (इंतजार करें) ⏸️"
                reason = "मार्केट साइडवेज है या कोई साफ सिग्नल नहीं है।"
                color = "blue"

                # Buy Condition
                if current['EMA_9'] > current['EMA_21'] and previous['EMA_9'] <= previous['EMA_21']:
                    signal = "BUY / CALL (खरीदें) 🟢"
                    reason = "Golden Crossover: मार्केट का ट्रेंड ऊपर की तरफ शुरू हुआ है।"
                    color = "green"
                # Sell Condition
                elif current['EMA_9'] < current['EMA_21'] and previous['EMA_9'] >= previous['EMA_21']:
                    signal = "SELL / PUT (बेचें) 🔴"
                    reason = "Death Crossover: मार्केट का ट्रेंड नीचे की तरफ शुरू हुआ है।"
                    color = "red"
                # RSI Condition
                elif current['RSI'] < 30:
                    signal = "BUY (Oversold) 🟢"
                    reason = "मार्केट बहुत गिर चुका है, बाउंस आ सकता है।"
                    color = "green"
                elif current['RSI'] > 75:
                    signal = "SELL (Overbought) 🔴"
                    reason = "मार्केट बहुत चढ़ चुका है, गिर सकता है।"
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

                # --- रिजल्ट दिखाना (Display) ---
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
                st.caption("⚠️ डिस्क्लेमर: यह केवल एक एआई टूल है। ट्रेडिंग अपने जोखिम पर करें।")

        except Exception as e:
            st.error(f"कुछ गड़बड़ हो गई: {e}")

else:
    st.info("👈 साइडबार से ऑप्शन चुनें और 'मार्केट चेक करें' बटन दबाएं।")
