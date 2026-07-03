import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import base64

# 1. API Configuration
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "YOUR_ACTUAL_API_KEY_HERE")
genai.configure(api_key=GOOGLE_API_KEY)
# Safe aur updated stable model use kar rahe hain
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. UI Setup (Matching "AI assistant motion by Robin Holesinsky on Muzli.jpg")
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

# TTS Player
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

# Input Variables
final_query = ""

# Layout for Text & Voice Inputs separately
user_query = st.text_input("Ask anything...", placeholder="Type your message here...", label_visibility="collapsed")

st.write("---")
st.write("Or use Voice Command:")
audio_record = mic_recorder(start_prompt="🎙️ Record Voice", stop_prompt="🛑 Stop & Process", key='recorder')

# Logic separation to avoid InvalidArgument error
if user_query:
    final_query = user_query
elif audio_record and 'bytes' in audio_record:
    with st.spinner("Processing your voice..."):
        try:
            audio_bytes = audio_record['bytes']
            # Gemini ko correct format me audio dictionary de rahe hain
            audio_data = {
                "mime_type": "audio/wav",
                "data": audio_bytes
            }
            # Audio ko directly text/reply me convert karne ka prompt
            response = model.generate_content([
                "The user has spoken. Listen to this audio carefully and reply to whatever they asked or said directly in simple short text.", 
                audio_data
            ])
            final_query = response.text
            st.info(f"Voice Detected: {final_query}")
        except Exception as e:
            st.error("Audio samajhne me dikkat hui. Kripya dobara koshish karein ya type karein.")

# Response Generator
if final_query:
    with st.spinner("AI is thinking..."):
        try:
            # Clean direct string query format
            response = model.generate_content(str(final_query))
            reply = response.text
            
            st.write(f"**AI:** {reply}")
            speak(reply)
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
