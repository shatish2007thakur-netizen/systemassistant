import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder  # Naya package use karenge
from gtts import gTTS
import os
import base64
import io

# API Configuration
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "YOUR_ACTUAL_API_KEY_HERE")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Page Setup (Premium UI Theme)
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

def speak(text):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)

# UI layout for Input
user_query = st.text_input("Ask anything...", placeholder="Type here...", label_visibility="collapsed")

# Browser-compatible Voice Recorder
st.write("Or record your voice:")
audio_record = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="🛑 Stop & Send", key='recorder')

final_query = ""
if user_query:
    final_query = user_query
elif audio_record:
    # Agar voice record hui hai, toh hum use Gemini ke naye model ko directly bhej sakte hain audio format me!
    with st.spinner("Processing audio..."):
        try:
            audio_bytes = audio_record['bytes']
            # Gemini 1.5 multi-modal hai, yeh directly audio samajh sakta hai
            audio_parts = [{"mime_type": "audio/wav", "data": audio_bytes}]
            response = model.generate_content(["Convert this audio speech to text, or reply directly if it's a question:", audio_parts[0]])
            final_query = response.text
        except Exception as e:
            st.error("Audio process karne me dikkat aayi.")

# Final Response
if final_query:
    st.write(f"**Query:** {final_query}")
    with st.spinner("AI is thinking..."):
        response = model.generate_content(final_query)
        reply = response.text
        st.write(f"**AI:** {reply}")
        speak(reply)
