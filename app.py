import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import base64

# --- MASTER API KEY CONFIGURATION ---
# 1. Sabse pehle Streamlit Cloud ke Secrets se check karega
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", None)

# 2. FALLBACK: Agar secrets kaam nahi kar raha, toh apni ASLI KEY niche dandi (quotes) me paste kar do!
# GitHub par push karne se pehle apni key yahan daal kar test karo.
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_ACTUAL_API_KEY_HERE":
    GOOGLE_API_KEY = " Apni AIzaSy... wali key yahan likhein" # <-- Apni AIzaSy... wali key yahan likhein

# Final validation check
if GOOGLE_API_KEY == "YAHAN_APNI_ASLI_GEMINI_KEY_PASTE_KARO" or not GOOGLE_API_KEY:
    st.error("🚨 **Key Missing:** Kripya code ke andar line 14 par apni asli Gemini API Key paste karein!")
    st.stop()

# Ab clean tarike se configure karein bina kisi extra space ke
try:
    # .strip() lagane se agar koi extra space copy ho gayi hogi toh woh hat jayegi
    genai.configure(api_key=GOOGLE_API_KEY.strip())
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()


# --- UI Setup (Matching "AI assistant motion by Robin Holesinsky on Muzli.jpg") ---
st.set_page_config(page_title="AI Assistant", page_icon="🔮", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .orb-container { display: flex; justify-content: center; align-items: center; margin-top: 50px; }
    .orb {
        width: 150px; height: 150px; border-radius: 50%;
        background: radial-gradient(circle, rgba(41,121,255,1) 0%, rgba(0,0,0,1) 70%);
        box-shadow: 0 0 40px 20px rgba(41,121,255,0.6);
        animation: pulse 2s infinite alternate;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 30px 10px rgba(41,121,255,0.4); }
        100% { transform: scale(1.05); box-shadow: 0 0 50px 30px rgba(41,121,255,0.8); }
    }
    .title-text { text-align: center; font-family: sans-serif; color: #8E8E93; margin-top: 20px; }
    .main-prompt { text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 40px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="orb-container"><div class="orb"></div></div>', unsafe_allow_html=True)
st.markdown('<div class="title-text">Hello Robin</div>', unsafe_allow_html=True)
st.markdown('<div class="main-prompt">How can I help you today?</div>', unsafe_allow_html=True)

# TTS Audio Player
def speak(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        pass

# Input Logic
final_query = ""

user_query = st.text_input("Ask anything...", placeholder="Type your message here...", label_visibility="collapsed")

st.write("---")
st.write("Or use Voice Command:")
audio_record = mic_recorder(start_prompt="🎙️ Record Voice", stop_prompt="🛑 Stop & Process", key='recorder')

if user_query:
    final_query = user_query
elif audio_record and 'bytes' in audio_record:
    with st.spinner("Processing your voice..."):
        try:
            audio_bytes = audio_record['bytes']
            audio_data = {"mime_type": "audio/wav", "data": audio_bytes}
            response = model.generate_content([
                "The user has spoken. Reply directly to whatever they asked in short text.", 
                audio_data
            ])
            final_query = response.text
            st.info(f"Voice Detected: {final_query}")
        except Exception as e:
            st.error("Audio processing failed. Please type instead.")

# Execution and Response
if final_query:
    with st.spinner("AI is thinking..."):
        try:
            response = model.generate_content(str(final_query))
            reply = response.text
            st.write(f"**AI:** {reply}")
            speak(reply)
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
