import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
import base64

# 1. API Configuration (Apna Gemini API Key yahan dalein ya Streamlit Secrets me)
# GitHub par daalte waat key ko code me mat chhorna!
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "YOUR_ACTUAL_API_KEY_HERE")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# 2. Page Setup (Premium Dark Theme like the image)
st.set_page_config(page_title="AI Assistant", page_icon="🔮", layout="centered")

# Custom CSS for UI matching "AI assistant motion by Robin Holesinsky on Muzli.jpg"
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .orb-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 50px;
    }
    .orb {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(41,121,255,1) 0%, rgba(0,0,0,1) 70%);
        box-shadow: 0 0 40px 20px rgba(41,121,255,0.6);
        animation: pulse 2s infinite alternate;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 30px 10px rgba(41,121,255,0.4); }
        100% { transform: scale(1.05); box-shadow: 0 0 50px 30px rgba(41,121,255,0.8); }
    }
    .title-text {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 300;
        margin-top: 20px;
        font-size: 24px;
        color: #8E8E93;
    }
    .main-prompt {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# UI Elements
st.markdown('<div class="orb-container"><div class="orb"></div></div>', unsafe_allow_html=True)
st.markdown('<div class="title-text">Hello Robin</div>', unsafe_allow_html=True)
st.markdown('<div class="main-prompt">How can I help you today?</div>', unsafe_allow_html=True)

# Helper function to convert Text to Speech and autoplay
def speak(text):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Voice Input Logic
def listen_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            return text
        except:
            st.error("Sorry, voice samajh nahi aayi. Try again!")
            return None

# User Input (Dono option: Voice aur Text Keyboard input jaise image me hai "Ask anything...")
col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.text_input("Ask anything...", placeholder="Type or click the Mic button...", label_visibility="collapsed")
with col2:
    mic_clicked = st.button("🎙️")

final_query = ""
if mic_clicked:
    final_query = listen_voice()
elif user_query:
    final_query = user_query

# Response Generation
if final_query:
    st.write(f"**You:** {final_query}")
    with st.spinner("Thinking..."):
        try:
            response = model.generate_content(final_query)
            reply = response.text
            st.write(f"**AI:** {reply}")
            speak(reply)
        except Exception as e:
            st.error(f"Error: {e}")
