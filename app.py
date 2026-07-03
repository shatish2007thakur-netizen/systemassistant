import streamlit as st
from streamlit_mic_recorder import speech_to_text
import datetime
import webbrowser
import urllib.parse
import wikipedia

# Streamlit Page Setup
st.set_page_config(page_title="APNA JARVIS SYSTEM", page_icon="🤖", layout="centered")

# Custom CSS for Jarvis Theme
st.markdown("""
    <style>
    .reportview-container { background: #1e1e1e; }
    h1 { color: #00ffcc; font-family: 'Courier New', Courier, monospace; text-align: center; }
    .status { color: #ffffff; font-family: Arial; text-align: center; font-size: 1.2rem; }
    .jarvis-response { background-color: #101010; color: #00ffcc; padding: 15px; border-radius: 5px; font-family: 'Consolas', monospace; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 JARVIS OS")
st.markdown("<p class='status'>Status: Online & Ready</p>", unsafe_allow_html=True)

wikipedia.set_lang("en")

def process_command(query):
    """Executes tasks instantly based on text/voice input."""
    query = query.lower().strip()
    response = ""
    actions = []

    # 1. Advanced Google Search Keyword Triggers
    if 'open the google and search' in query or 'open google and search' in query:
        search_query = query.replace("hey jarvis", "").replace("open the google and search", "").replace("open google and search", "").strip()
        if search_query:
            response = f"Searching for {search_query} on Google, Sir."
            encoded_query = urllib.parse.quote(search_query)
            actions.append(f"https://www.google.com/search?q={encoded_query}")
        else:
            response = "Sir, what do you want me to search on Google?"

    # 2. Base Command for YouTube
    elif 'youtube' in query or 'yutub' in query:
        response = "Opening YouTube, Sir."
        actions.append("https://youtube.com")
        
    # 3. Base Command for Google Homepage
    elif 'google' in query or 'gugal' in query or 'open d google' in query:
        response = "Opening Google, Sir."
        actions.append("https://google.com")
        
    # 4. Fallback Explicit Keyword Search
    elif 'search' in query:
        search_query = query.replace("search", "").strip()
        response = f"Searching for {search_query} on Google, Sir."
        encoded_query = urllib.parse.quote(search_query)
        actions.append(f"https://www.google.com/search?q={encoded_query}")
        
    # 5. Time Checking
    elif 'time' in query or 'samay' in query:
        str_time = datetime.datetime.now().strftime("%H:%M")
        response = f"Sir, the time is {str_time}"
        
    # 6. Normal Small Talk
    elif 'hello' in query or 'hi' in query:
        response = "Hello Sir! How can I help you today?"
    elif 'how are you' in query or 'kaise ho' in query:
        response = "I am doing great Sir, tell me how can I help you?"
        
    # 7. SMART INTERNET SEARCH FALLBACK
    elif 'what is' in query or 'who is' in query or 'tell me about' in query:
        wiki_query = query.replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
        response = f"Searching Wikipedia for {wiki_query}..."
        try:
            results = wikipedia.summary(wiki_query, sentences=2)
            response = f"According to Wikipedia: {results}"
        except Exception:
            response = f"I couldn't fetch a direct summary, searching Google for {wiki_query} instead."
            encoded_query = urllib.parse.quote(wiki_query)
            actions.append(f"https://www.google.com/search?q={encoded_query}")
            
    else:
        # Fallback global search for random queries
        response = f"I found no specific command, performing global search for: {query}"
        encoded_query = urllib.parse.quote(query)
        actions.append(f"https://www.google.com/search?q={encoded_query}")

    return response, actions

# --- UI Layout & Logic ---
st.subheader("Speak or Type your command below:")

# Voice Input Section
st.write("🎙️ **Voice Input:** Click the button below to speak.")
text_from_voice = speech_to_text(
    language='en', 
    start_prompt="🔴 CLICK TO TALK", 
    stop_prompt="⏹️ STOP RECORDING", 
    just_once=True, 
    key='STT'
)

# Text Input Section (Backup)
text_from_input = st.text_input("⌨️ **Text Input:** (Press Enter to execute)")

# Query finalization
final_query = ""
if text_from_voice:
    final_query = text_from_voice
elif text_from_input:
    final_query = text_from_input

if final_query:
    st.markdown(f"**You:** {final_query}")
    
    # Process Command
    jarvis_reply, web_links = process_command(final_query)
    
    # Show Jarvis Response
    st.markdown("### Jarvis Response:")
    st.markdown(f"<div class='jarvis-response'>{jarvis_reply}</div>", unsafe_allow_html=True)
    
    # Handing Web Links (Streamlit cannot automatically open tabs, so we provide clickable link/buttons)
    if web_links:
        for link in web_links:
            st.link_button("🔗 Click here to Open Link", link)